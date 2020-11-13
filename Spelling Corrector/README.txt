1. Install numpy as

	- pip install numpy

2.Spelling corrector has been modeled only for unigram.

3.For Language model, candidates within both one and two unit distance have been considered. 
  as a result, it has better accuracy of 35.30% on test data.

4.For noisy channel model, only candidates within one unit distance have been considered.
  as a result it has accuracy of only 26.5%.

5. test code segment have been commented out as it takes longer time to evaluate. 
   you can try it by uncommenting, provided you have enough time to wait for the result.

6. to run the code, type
	if you want to use "language" model and the incorrect word is "thew".

		- python spelling_corrector.py "language" "thew"

	similarly, if you want to use "noisy" channel model and incorrect word is "thew".
		
		- python spelling_corrector.py "noisy" "thew"
 