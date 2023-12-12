#
# This chatbot is designed to provide relevant verses from the Noble Quran
# that may address a question, along with a potential answer derived
# from those verses using an AI-powered language model
#
# uxquran.com
#

import numpy as np
import json
import zipfile
import os
from sentence_transformers import SentenceTransformer, util
from transformers import pipeline


class QuranSimilarVerses:
    # quran verses embeddings
    quran_data = None
    
    # quran verse translations in text
    translation = []
    
    # model used for semantic search
    search_model = None

    # model used for qn and answering
    qa_model = None

    def __init__(self, folder, quran_embeddings_name, translation_file, token):
        self.search_model = SentenceTransformer('all-MiniLM-l6-v2')
        
        # models: deepset/roberta-base-squad2-distilled, deepset/roberta-large-squad2, deepset/tinyroberta-squad2
        # https://docs.cloud.deepset.ai/docs/language-models-in-deepset-cloud
        self.qa_model = pipeline("question-answering", model="deepset/tinyroberta-squad2")

        # if first time, then unzip quran embeddings
        embedding_file_path = os.path.join(folder, quran_embeddings_name + ".npy")
        if not os.path.exists(embedding_file_path):
            zip_file_path = os.path.join(folder, quran_embeddings_name + ".zip")
            with zipfile.ZipFile(zip_file_path,"r") as zip_ref:
                    zip_ref.extractall(folder)

        # load quran embeddings
        self.quran_data = np.load(embedding_file_path, allow_pickle=True)

        # load quran translation
        translation_file_path = os.path.join(folder, translation_file)
        trans_file = open(translation_file_path)
        trans_json = json.load(trans_file)
        trans_file.close()
        self.translation = []
        for quran in trans_json['quran']:
            chapter = quran['chapter']
            verse = quran['verse']
            text = quran['text']
            verse = str(chapter) + "###" + str(verse) + "###" + text
            self.translation.append(verse)

    def get_similar(self, question):            
        if self.quran_data is None:
            return "Error: Loading data, please try again after some time"

        # encode the question to its embedding vector
        embedding_input_string = self.search_model.encode(question)

        # get top 10 semantically simlar verses
        result = util.semantic_search(query_embeddings=embedding_input_string, corpus_embeddings=self.quran_data, top_k=10)

        # generate the response
        response = "Qn: " +  question
        response = response + "\nRefs:\n"

        # get top N results
        N = 8
        sliced_result = result[0][:N]

        for item in sliced_result:
            index = item['corpus_id']
            translation_components = self.translation[index].split("###")
            sura = translation_components[0]
            aya = translation_components[1]
            verse = translation_components[2]
            response = response + str(sura) + ":" + str(aya) + " " + verse + "\n"
            response = response + "https://uxquran.com/apps/quran-ayat/?sura=" + sura + "&aya=" + aya + "\n\n"

        return response, question, result
    
    def get_answer(self, question, search_result):
        if self.quran_data is None:
            return "Error: Loading data, please try again after some time"

        # get the translation texts corresponding to the similar verses for context
        results_text = ""
        for item in search_result[0]:
            index = item['corpus_id']
            results_text = results_text + "," + self.translation[index]

        # find an answer from the results_text as context
        answer = self.qa_model(question = question, context = results_text)

        # generate the response
        response = "Qn: " +  question
        response = response + "\nProbable Answer: " + answer['answer'] + "\n"

        return response


# quran = QuranSimilarVerses("./static/", "embeddings", "input.json", "")
# response, question, result = quran.get_similar("how long did ashabul khaf sleep in the cave?")
# print(response)
# answer = quran.get_answer(question, result)
# print(answer)