### Head-Tail Tokenizer

'Information Retrivel' class projoct in Kookmin University.

This code make Head-Tail Tokenizer from Universal Dependency corpus to Head-Tail corpus.

### 1. Universal Dependency corpus
- Universal Dependency corpus has 10 columns. 
- data from [tagged KCCq28 by BUFS-JBNU](https://github.com/bufsnlp2030/BUFS-JBNUCorpus2020)
- Data example
```
# sent_id = 1003
# file = 00001
# text = 자기계발을 원하는 사람에게 가장 적합한 학교
1	자기계발을	자기+계발+을	PRON	NP+NNG+JKO	_	2	NP_OBJ	_	_
2	원하는	원하+는	VERB	VV+ETM	_	3	VP_MOD	_	_
3	사람에게	사람+에게	NOUN	NNG+JKB	_	5	NP_AJT	_	_
4	가장	가장	ADV	MAG	_	5	AP	_	_
5	적합한	적합하+ㄴ	ADJ	VA+ETM	_	6	VP_MOD	_	_
6	학교	학교	NOUN	NNG	_	0	NP	_	_
```
### 2. Head-Tail corpus & Train
- convert UD corpus to Head-Tail corpus
- used `head-tail.py`
- Run
```
python3 head-tail.py --output-type morphs --mode train
```
### 3. Inference
- Tokenize User input sentence. (only Korean)
- Run
```
python3 head-tail.py --mode inference
```
