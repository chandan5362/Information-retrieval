import glob
import os
import re
import numpy as np
import nltk
from pathlib import Path
from tkinter import *
from tkinter import ttk
from tkinter import filedialog
from rouge import Rouge
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

gui = Tk()
d = Text(gui, height=18, width=80)


def getFolderPath():
    folder_selected = filedialog.askdirectory()
    folderPath.set(folder_selected)


def calculateCosineSimilariy(doc):
    """
    cosine similarity using tf-idf of terms
    """
    l = len(doc)
    vectorizer = TfidfVectorizer(sublinear_tf=True)
    sim_matrix = np.zeros((l, l))
    tf_idf_vector = vectorizer.fit_transform(doc).toarray()
    for i in range(l):
        for j in range(l):

            sim_matrix[i, j] = np.dot(tf_idf_vector[i], tf_idf_vector[j].T)
    return np.round(sim_matrix, 2)


def predictWordSense(tagged_si):
    """
    tagged_si = input sentene whose word's word sense is to be predicted
    best_sense_ar = array containing the best sense of each word of the input sentence

    """
    tag = ['VBD', 'VB', 'VBG', 'RB', 'RBR', 'JJ']
    tagged_si = [w for w in tagged_si if w[1] in tag]
    best_sense_arr = []
    for ele in tagged_si:
        target = ele
        context_arr = []
        context = [w for w in tagged_si if not w is target]
        target_syn = wn.synsets(target[0])
        target_arr = [w.definition() for w in target_syn]
        context_syn = [wn.synsets(w[0]) for w in context]
        collapse_arr = [w for wd in context_syn for w in wd]
        context_arr = [w.definition() for w in collapse_arr]
        context_arr = " ".join(context_arr)
        # find the sense of a given word
        best_sense = target_syn[0]
        cmn_word = 0
        for l_ in range(len(target_arr)):
            le = len(list(set(context_arr) & set(target_arr[l_])))
            if le > cmn_word:
                best_sense = target_syn[l_]
        best_sense_arr.append(best_sense)
    return tagged_si, best_sense_arr


def calculateSemanticSimilarity(doc):
    """
    sim_matrix = sentence similarity matrix
    tagged_si, tagged_sj = sentence tokens tagged with part of speech 

    """
    stop_words = set(stopwords.words('english'))
    l = len(doc)
    sim_matrix = np.zeros((l, l))
    ps = WordNetLemmatizer()
    for i in range(l):
        # print(doc[i])
        token_si = re.findall("\w+", doc[i])
        # stop words removal
        token_si = [wi for wi in token_si if not wi in stop_words]
        token_si = [ps.lemmatize(w) for w in token_si]  # stemming
        tagged_si = nltk.pos_tag(token_si)  # part of speech tagging
        for j in range(l):
            token_sj = re.findall("\w+", doc[j])
            # stop words removal
            token_sj = [wj for wj in token_sj if not wj in stop_words]
            token_sj = [ps.lemmatize(w) for w in token_sj]  # stemming
            tagged_sj = nltk.pos_tag(token_sj)  # part of speech tagging
            try:
                # print(predictWordSense(tagged_si))
                synset_arr_s1, sense_arr_s1 = predictWordSense(tagged_si)
                sysnset_arr_s2, sense_arr_s2 = predictWordSense(tagged_sj)
            except (IndexError, UnboundLocalError):
                pass
            sim_s1s2 = np.zeros((len(sense_arr_s1), len(sense_arr_s2)))
            for s1 in range(len(sense_arr_s1)):
                for s2 in range(len(sense_arr_s2)):
                    sim_s1s2[s1, s2] = sense_arr_s1[s1].path_similarity(
                        sense_arr_s2[s2])

            sim_s1s2[np.isnan(sim_s1s2)] = 0
            try:
                sim_matrix[i, j] = max(np.sum(sim_s1s2, axis=1))
            except ValueError:
                sim_matrix[i, j] = 0
    return sim_matrix


def symmetrize(lst):
    for i in range(lst.shape[0]):
        for j in range(i, lst.shape[1]):
            lst[i, j] = max(lst[i, j], lst[j, i])
            lst[j, i] = lst[i, j]

    return lst


def find_centroid(arr, mat):
    set_ele = list(set(arr))
    centroid = [0]*(max(set_ele)+1)
    for el in set_ele:
        temp_arr = []
        for i in range(len(arr)):
            if arr[i] == el:
                temp_arr.append(i)
        max_score = 0
        max_index = None
        for j in temp_arr:
            score = 0
            for k in temp_arr:
                score += (mat[j, k])
            if score >= max_score:
                max_index = j
                max_score = score
        centroid[el-1] = max_index

    return centroid


# say we want only 6 sentences in the summary,
# therefore k = 6
def clustering(sim_matrix, list_of_sentences):
    """
    clsutering of sentences based on similarity score
    """
    l = len(sim_matrix)
    np.random.seed(4)
    clusteroid = np.random.randint(0, l+1, 5)
    initial_clusteroid = [list_of_sentences[i] for i in clusteroid]

    num_iteration = 50
    for iter in range(num_iteration):
        cluster_seq = [0]*l
        for i in range(l):
            temp_clust = []
            for ind in clusteroid:
                temp_clust.append(sim_matrix[i, ind])
            cluster_seq[i] = temp_clust.index(max(temp_clust))
        clusteroid = find_centroid(cluster_seq, sim_matrix)
    return clusteroid


def loadDocuments():
    """
    READ DOCUMENTS 
    """
    folder = folderPath.get()

    path = Path(folder)
    rg = Rouge()
    file_ = sorted(os.listdir(path))
    corpus = []
    for fl in sorted(file_):
        fl = os.path.join(path, fl)

        with open(fl, 'r') as fp:
            corpus.append(fp.read())
    merged_list1 = corpus[10]
    list_of_sentences = merged_list1.split(".\n")
    similarity_matrix = calculateCosineSimilariy(
        list_of_sentences)  # Cosine similarity

    sim_array = calculateSemanticSimilarity(
        list_of_sentences)  # semantic similarity
    sentence_sim_score = symmetrize(sim_array)

    op = clustering(sentence_sim_score, list_of_sentences)
    hypothesis = ". ".join([list_of_sentences[i] for i in sorted(op)])
    d.insert(END, hypothesis)


gui.geometry("600x600")
gui.title("Multi-document Text summarizer ")
folderPath = StringVar()
a = Label(gui, text="select folder")
E = Entry(gui, textvariable=folderPath)
btnFind = ttk.Button(gui, text="Browse Folder", command=getFolderPath)
folder = folderPath.get()
f = Button(gui, text="summarize", bg="green", command=loadDocuments)
b2 = Button(gui, text="Exit", command=gui.destroy, bg="red")
a.pack(padx=5, pady=0)
E.pack(padx=10, pady=0)
btnFind.pack()
f.pack(pady=1)
d.pack(pady=0)
b2.pack()
gui.mainloop()
