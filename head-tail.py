# Build a head-tail segmented corpus
# Input files: POS-tagged files by BUFS
import glob
import argparse
import re
import pickle

# 규칙 저장
wordDic = {}

def savedic(pickle_name):
	with open(pickle_name, 'wb') as f:
		pickle.dump(wordDic, f, pickle.HIGHEST_PROTOCOL)

def loaddic(pickle_name):
	with open(pickle_name, 'rb') as f:
		data = pickle.load(f)
	return data

def save_rule(word):
	'''
	save head-tail rule.
	But, only save head in wordDic, to save memory

	Args
	word : already has head-tail format string (ex. '먹+습니다')

	wordDic save only '먹' in the example
	'''
	global wordDic

	word = word.split('+')
	if word[0] not in wordDic:
		wordDic[word[0]] = 1

	'''
	if len(word) > 1:
		
		
		if word[0] in wordDic:
			wordDic[word[0]] += [word[1]]
		else:
			wordDic[word[0]] = [word[1]]
		
	else:
		wordDic[word[0]] = [999] # 단어 하나만 들어감 head-tail 없이 ex. 가장
	'''
	return 0

def get_head_tail(line):
	'''
	Get Head and Tail token and POStag from BUFS corpus.
	
	Args : 
	line : the line is Universal Dependency format.
	-------------------------------------------------------
	line Example
	1	자기계발을	자기+계발+을	PRON	NP+NNG+JKO	_	2	NP_OBJ	_	_
	2	원하는	원하+는	VERB	VV+ETM	_	3	VP_MOD	_	_
	3	사람에게	사람+에게	NOUN	NNG+JKB	_	5	NP_AJT	_	_
	4	가장	가장	ADV	MAG	_	5	AP	_	_
	5	적합한	적합하+ㄴ	ADJ	VA+ETM	_	6	VP_MOD	_	_
	6	학교	학교	NOUN	NNG	_	0	NP	_	_	
	'''
	a = line.split()
	if len(a) < 10:
		print("Wrong format -- less than 10 values in a line!")
		return ''

	ht = a[2]	# head+tail format --> no syllable decomposition!
	ht_split = ht.split('+')

	#길이가 3 이상인 경우
	if len(ht_split) >= 3:
		ht_pos = a[4] #ht 에 해당하는 pos tag 추출
		ht_pos = ht_pos.split('+')
		
		#두 번째 pos 태그가 N으로 시작하는 경우
		if ht_pos[1].startswith('N'): # 자기+계발+을
			if re.findall('[ㄱ-ㅎ]',ht_split[-1]) != []: #1+명+이+ㄴ데 -> 1명+인데
				ht = ''.join(ht_split[:2]) + '+' +  a[1][len(''.join(ht_split[:2])):]
				ht_pos = ht_pos[1] + '+' + '_'.join(ht_pos[2:])

			else:
				ht_pos = '+'.join(ht_pos[1:])
				ht = ht_split[0] + '+'.join(ht_split[1:]) #자기계발 + 을
		
		elif re.findall('[ㄱ-ㅎ]',ht_split[-1]) != []: #진행중+이+ㄴ -> 진행중+인 / 20대+에+ㄴ -> 20대+엔
			ht_pos = ht_pos[0] + '+' + '_'.join(ht_pos[1:])
			ht = a[1][:len(ht_split[0])] + '+' + a[1][len(ht_split[0]):]

		else: # 저지르+었+다 -> 저질렀+다
			word = a[1]
			ht = word[:len(ht_split[0])] + '+' + word[len(ht_split[0]):] # 저질렀 + 다
			ht_pos = ht_pos[0]+'_'+ht_pos[1] + '+' + ht_pos[-1]

	#길이가 2 인 경우
	elif len(ht_split) == 2 and re.findall('[ㄱ-ㅎ]',ht_split[1]) != []:
	#elif sum([len(i) for i in ht_split]) > len(a[1]):
		if len(ht_split[1]) == 1:  #'하+ㄹ' -> '할' 과 같이 자소 한개가 되는 경우 처리
			ht = a[1]
			ht_pos = a[4]
		else: #'하+ㄴ다' -> '한+다'
			ht = a[1][:len(ht_split[0])] + '+' + a[1][len(ht_split[0]):]
			ht_pos = a[4]

	#'쉬운' -> '쉽'+'ㄴ' 과 같이 쪼개져서 2번째 if문으로 해결 안되는 경우
	elif len(ht_split) == 2 and a[4].split('+')[-1] == 'ETM':
		ht = a[1]
		ht_pos = a[4].replace('+','_')	

	# '하+어야'-> '해야' 로 쪼개지도록 원형 복원
	elif len(ht_split) == 2: 
		ht = a[1][:len(ht_split[0])] + '+' + a[1][len(ht_split[0]):]
		ht_pos = a[4]
	
	# 1개 그대로 들어가는 부분
	# '가장' ,'또' ...
	else:
		ht_pos = a[4]

	return ht, ht_pos

def convert_format(morphs, poss):
	'''
	This function is working Train mode only.

	make output format to 'token/pos' sequence.
	If did not used this function, the output is only 'token' sequence.
	'''
	morphs = morphs.split('+')
	pos = poss.split('+')

	# 2개의 형태소가 하나의 토큰으로 된 경우 'VA_ETM'과 같이 '_'로 연결	
	if len(morphs) != len(pos):
		pos = [pos[0]+"_"+pos[1]]
	'''
	if len(morphs) != len(pos):
		morphs.append('NULL')
	'''

	output = [m+'/'+p for m, p in zip(morphs, pos)]
	
	return '+'.join(output)

def train(args, in_files, out_file):
	'''
	Train Head-Tail tokenizer

	Args :
	in_files : input file list
	out_file : output file name
	'''
	fnames = glob.glob(in_files)
	fout = open(out_file, 'w', encoding='utf8')

	for file in fnames:
		print(file)
		f = open(file, 'r', encoding='utf8')
		lines = f.readlines()
		sent = ''
		for line in lines:
			line = line.rstrip()  #line = remove_CRLF(line)

			if line == '':	#End-Of-Sentence
				fout.write(sent+'\n')
				sent = ''	#reset for next sentence
			elif line[0] == '#':	#comment line
				continue
			else:
				word, pos = get_head_tail(line)
				
				save_rule(word)
				
				if args.output_type == 'morphs':
					sent = sent + ' ' + word
				else:
					sent = sent + ' ' + convert_format(word, pos)
			
		f.close
	fout.close
	print("New file <" + out_file + "> was created!")
	savedic('rules.pkl')

	return 0

def find_headtail(sentList):
	'''
	find Head-Tail from user input sentence

	Args 
	sentList : tokenize based on sentence marker and words List
	'''
	josa = ('은','는','이','가','을','를','의','에','로','으로','과','와','도','에서','만','이나','나','까지','부터','에게','보다','께','처럼','이라도','라도',\
		'으로서','로서','조차','만큼','같이','마저','이나마','나마','한테','더러','에게서','한테서','께서','이야','이라야','고')
	
	output = []

	for subword in sentList:
		if subword.endswith(josa): #subword 토큰이 조사로 끝나는 경우
			josa_pattern = "(" + "$)|(".join(josa) + "$)" # make a regex that matches if any of our regexes match
			head, tail = re.sub(josa_pattern, ' \g<0> ', subword).split() # find regex match and insert replace text

		elif subword in wordDic: # wordDic에서 통채로 살핌
			head, tail = subword, ''
		
		else: # 뒤에서 부터 하나씩 늘려가면서 사전에 들어가는지 봐야함
			i = 1
			while i < len(subword):
				if subword[:-i] in wordDic:
					head, tail = subword[:-i], subword[-i:]
					break
				i += 1
			else: # 사전에서 발견하지 못한 경우, 입력단어를 그대로 내보내줌
				head, tail = subword, ''

		output.append(head+'_'+tail)
	
	return output

def inference(sent):
	global wordDic
	'''
	make head-tail tokenizer from user input sentence

	1. tokenize sentence marker
	2. find head-tail based on dictionary
	3. reformat output
	'''
	# 0. load rules
	wordDic = loaddic('rules.pkl')

	# 1. tokenize sentence marker
	sent = sent.replace('"',' " ').replace("'"," ' ").replace('.',' . ').replace(',',' , ').replace('?',' ? ').strip().split()

	# 2. find head-tail 
	output = find_headtail(sent)

	# 3. reformat output
	re_output = [o[:-1] if o.endswith('_') else o for o in output] 
	
	return ' '.join(re_output).replace('_', '+')

if __name__ == "__main__":

	parser = argparse.ArgumentParser()
	parser.add_argument('--output-type', default='morphs', help='morphs or pos')
	parser.add_argument('--mode', help='train or inference')
	args = parser.parse_args()

	if args.mode == 'train':
		in_files = "./KCCq28_equal_morph-100files/*.txt"
		out_file = "./KCCq28_equal_morph-100files/test/output/head_tail_q28.txt"
		
		train(args, in_files, out_file)
	
	else: # mode == inference
		input_sent = input('write sentence : ')
		print(inference(input_sent))