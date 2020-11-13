import numpy as np
import sys
import re
from collections import Counter

alphabets = 'abcdefghijklmnopqrstuvwxyz'
insert_conf = np.zeros((26,26))
delete_conf = np.zeros((26,26))
substitute_conf = np.zeros((26,26))
transpose_conf = np.zeros((26,26))
output_l = dict()
output_n = dict()


def edit_dist1(word,alphabet = alphabets):
    '''
    generates all the psossible candidates within 1 edit distance
    '''
    delete = [word[:i]+word[i+1:] for i in range(len(word))]
    insert = [word[:i]+x+word[i:] for x in alphabet for i in range(len(word)+1)]
    replace = [word[:i]+x+word[i+1:] for x in alphabet for i in range(len(word))]
    transposition = [word[:i-2]+word[i-1]+word[i-2]+word[i:] for i in range(2,len(word)+1)]
    return set(delete+insert+replace+transposition)

def edit0(word):
    '''
    returns the tokens within zero edit distance or word itself
    '''
    if word in token_freq:
        return {word}

def edit1(word):
    '''
    return tokens within one edit distance that are there in the corpus
    '''
    return {wd for wd in word if wd in token_freq}

def edit2(word):
    '''
    return words within 2 edit distance
    '''
    edit_2 = {wd for tok in word for wd in edit_dist1(tok) if wd in token_freq }
    return edit_2

def generate_candidate(word):
    '''
    generates all the possible candidates which are there in the dictionary
    '''
    words = edit_dist1(word)
    return edit0(word) or edit1(words) or edit2(words) or [word]


def language_model(word):
    '''
    returns the correct word corresponding to incorrect one
    '''
    candidates= {wd:token_freq[wd] for wd in generate_candidate(word) if wd in token_freq  }
    candidates = generate_candidate(word.lower())
    
    return max(candidates,key = token_freq.get)

def create_confusion_matrix(count_edit1):
    for ele in count_edit1.split("\n"):
        try:
            temp = ele.split()[0].split("|")
            try:
                if(len(temp[0]) == len(temp[1]) and len(temp[0])==1):
                    substitute_conf[ord(temp[0])-97,ord(temp[1])-97] = int(ele.split()[1])
                if(len(temp[0]) == len(temp[1]) and len(temp[0])==2):
                    transpose_conf[ord(temp[0][0])-97,ord(temp[0][1])-97] = int(ele.split()[1])
                if(len(temp[0]) > len(temp[1])):
                    delete_conf[ord(temp[0][0])-97,ord(temp[0][1])-97] = int(ele.split()[1])
                if(len(temp[0]) < len(temp[1])):
                    insert_conf[ord(temp[1][0])-97,ord(temp[1][1])-97] = int(ele.split()[1])
            except:
                pass
        except:
            pass
       
def find_diff(str1,str2):
    '''
    remove common prefixes from the given pair of strings
    '''
    i1,i2= 0,0
    while i1 < len(str1) and i2 < len(str2):
        if str1[i1] != str2[i2]:
            break
        i1+=1
        i2+=1
    str1 = str1[i1:]
    str2 = str2[i2:]
    
    '''
    removes common suffixes from the sliced pair of strings
    '''
    j1,j2 = len(str1)-1, len(str2)-1
    while j1 >= 0 and j2 >=0:
        if str1[j1] != str2[j2]:
            break
        j1-=1
        j2-=1
    str1 = str1[:j1+1]
    str2 = str2[:j2+1]
    
    return (str1,str2)

def countChar(ch):
    return str(incorr_list).count(ch)

def computeChannelProbability(inc):
    '''
    generates candidates for each incorrect word that is there in the dictionary within one edit distance
    '''
    prob = dict()
    edit1_words = edit1(edit_dist1(inc))
    for wd in edit1_words:
        ret_ch = find_diff(inc,wd)

        if len(ret_ch[0])== len(ret_ch[1]):

            if len(ret_ch[1])==1 and ret_ch[0] !='' and ret_ch[1]!='':
                '''
                error probability of candidate generated due to substitution within one edit distance
                '''
                prob[wd] = (substitute_conf[ord(ret_ch[0])-97,ord(ret_ch[1])-97]+1)/(countChar(ret_ch[0])+26)
                
            if len(ret_ch[1])==2 and ret_ch[0] !=' ' and ret_ch[1]!=' ':
                '''
                error probability of candidate generated due to Transposition within one edit distance
                '''
                prob[wd] = (transpose_conf[ord(ret_ch[0][0])-97, ord(ret_ch[0][1])-97]+1)/(26+countChar(ret_ch[0]))

        if len(ret_ch[1])==0:
            '''
            error probability of candidate generated due to Deletion within one edit distance
            exception handles the zero edit distance error
            '''
            try:
                ind = inc.index(ret_ch[0])
                ch = inc[ind-1]+inc[ind]
                prob[wd] = (delete_conf[ord(inc[ind-1])-97,ord(ret_ch[0])-97]+1)/(26+countChar(ch))
            except TypeError:
                pass

        if len(ret_ch[0])==0:
            '''
            error probability of candidate generated due to Insertion within one edit distance
            exception handles zero edit distance error
            '''
            try:
                ind = wd.index(ret_ch[1])
                ch = wd[ind-1]+wd[ind]
                prob[wd] = (delete_conf[ord(wd[ind-1])-97,ord(ret_ch[1])-97]+1)/(26+countChar(ch))
            except TypeError:
                pass
        
        if len(ret_ch[0])==0 and len(ret_ch[1])==0:
            '''
            return 1 in case the incorrect word is itself in the dictionary
            '''
            prob[wd] = 1
    return prob

    
def findRightCandidate(word):
    word = word.strip()
    noise_prob = computeChannelProbability(word)
    for key,value in noise_prob.items():
        noise_prob[key] = value*(token_freq[key]/1105285)*(10**8)

    try:
        return max(noise_prob,key = noise_prob.get)
    except ValueError:
        return word
    


def eval(correct_set, incorrect_set,model):
    tp = 0
    total = 0
    for i in range(len(correct_set)):
        temp_set = incorrect_set[i].split(",")

        for j in range(len(temp_set)):  
            
            ch = re.findall('[a-z]+',temp_set[j])
            
            try:
                l_m = language_model(ch[0])
                n_m = findRightCandidate(ch[0])
                output_n[ch[0]] = n_m
                output_l[ch[0]] = l_m
                if model == "noisy_channel":
                    if n_m==correct_set[i]:
                        tp+=1
                    total+=1
                if model == 'language_model':
                    if l_m==correct_set[i]:
                        tp+=1
                    total+=1
                    
            except IndexError:
                pass
        
    return total,tp      
    

if __name__ == "__main__":
    model = sys.argv[1]
    word = sys.argv[2]
    # print(sys.argv[1])
    '''
    load the test-set document. store correct words in
    corr_list and incorrect words in incorr_list
    '''
    with open('spell-errors.txt','r') as f:
        corr_incorr_pair = f.read()
    corr_list =[]
    incorr_list = []
    for st in corr_incorr_pair.split("\n"):
        correct = st.split(":")[0]
        incorrect = st.split(":")[1]
        corr_list.append(correct)
        incorr_list.append(incorrect)
    """
    load the corpus 'big.txt' and create a dictionary 'token_frequency'
    to store the frequency of each word
    """
    with open('big.txt','r') as f:
        text = f.read()
    word_bag = re.findall('[a-z]+',text.lower())
    word_bag = word_bag+corr_list
    token_freq = Counter(word_bag)

    """
    load the document containing the relative edit between correct
    and incorrect word within one edit distance for the corpus 'big.txt'.
    """
    with open('count_1edit.txt','r') as f:
        count_edit1 = f.read()
    create_confusion_matrix(count_edit1)

    if model == 'language':
        print("Correct word is -> ",end=" ")
        print(language_model(word))
    if model == 'noisy':
        print("correct word is -> ",end =" ")
        print(findRightCandidate(word))


    """
    model evaluation
    """
    # total_l,tp_l = eval(corr_list,incorr_list,"language_model")
    # total_n, tp_n = eval(corr_list,incorr_list,"noisy_channel")
    # print("accuracy for language model is {:2f}".format((tp_l/total_l)*100))
    # print("accuracy for noisy channel model is {:2f}".format((tp_n/total_n)*100))

    # """writing output to text file"""
    # f_l = open("lang_out.txt","w")
    # f_l.write(str(output_l))
    # f_l.close()
    # f_n = open("noisy_out.txt","w")
    # f_n.write(str(output_n))
    # f_n.close()
    
    