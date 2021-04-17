# Multi-Document text summarizer
__A naive imolementation of Wordnet based Lesk-word sense disambiguation for text summarization.___
Natural language and Information retrieval have led plenty of researches in the domain of 
text summarizer. Most of the summarizer today uses sentence extraction on the basis of 
sentence importance score. Sentence scoring method uses both statistical and semantic 
feature to distinguish between important sentences and redundant sentences. Other kind of 
summarizer are abstractive. They rely upon abstract of sentences. Instead of inserting the 
original sentence, they modify the sentences semantically in the summary. Most common 
way to calculate the sentence importance score is to train a binary classifier, Markov model 
or directly assigning weight based on different similarity measures. In this report, I have 
implemented a multi-document extraction-based text-summarizer.

__Smilarity measures used in this project are -__
* Cosine similarity
* Lesk Sense Disambiguation (LSD)

__Evaluation Metrics__
* ROUGE score

__Sentence similarity score__
* Cosine similarity score - Not much effective in this case ( as the order of words doesn't matter at all)
* Semantic similarity score -
	* Tokenize the sentences
	* Stemming
	* PoS tagging
	* Find appropriate word sense using LSD
	* Find sentence similarity based on word pair similarity


### Flow chart
![](https://github.com/chandan5362/Information-retrieval/blob/b1358bd01152dc2abf95631ece8cf15963657506/MUlti-Document%20Text%20summarizer/Images/model_design.JPG)



## Dataset
Dataset is included in the file. For more information about the dataset, please visit this [website](https://www-nlpir.nist.gov/projects/duc/data/2004_data.html)

## Setup
To setup the environment run the following commands.

### 1. To create virtual environment run -
```python -m venv myenv```
		
### 2. To activate myenv run -
```source myenv/bin/activate (on unix)```
		
### 3. Install required packages using following commnad.
```pip install -r requirements.txt```
		
### 4. Execute python script as -
`python summarizer.py`
	
### 5. select the directory containing .txt files.
Example -
`Desktop/036-Project-IR-MYMPY/DUC2004_documents_cleaned_tokenized/d30001t_raw`

### GUI
![](https://github.com/chandan5362/Information-retrieval/blob/44b0797569badd9b8cad9ebd8473a4ee2e595530/MUlti-Document%20Text%20summarizer/Images/GUI.JPG)<br>
	
### Demo
![](https://github.com/chandan5362/Information-retrieval/blob/b1358bd01152dc2abf95631ece8cf15963657506/MUlti-Document%20Text%20summarizer/Images/Demo.JPG)
