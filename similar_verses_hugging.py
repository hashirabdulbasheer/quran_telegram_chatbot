#
# This chatbot is designed to provide relevant verses from the Noble Quran
# that may address a question, along with a potential answer derived
# from those verses using an AI-powered language model
#
# uxquran.com
#

import numpy as np
import json
import itertools
import zipfile
import os
from langchain.embeddings import HuggingFaceInferenceAPIEmbeddings

class QuranSimilarVerses:
    quran_data = None
    translation = None
    embedding = None

    def __init__(self, folder, quran_embeddings_name, translation_file, token):
        self.embedding = HuggingFaceInferenceAPIEmbeddings(api_key=token, model_name="sentence-transformers/all-MiniLM-l6-v2")
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
        self.translation = trans_json


    def get_verse(self, surah, aya):
        return [d for d in self.translation["quran"] if int(d['chapter']) == int(surah) and int(d['verse']) == int(aya)][0]["text"]


    def get_similar(self, question):
        if self.quran_data is None:
            return "Error: Loading data, please try again after some time"

        embedding_input_string = self.embedding.embed_query(question)
        items = self.quran_data.item()
        result = {}
        for key in items:
            result[key] = np.dot(embedding_input_string, items[key])


        # sorting in descending order
        sorted_result = dict(sorted(result.items(), key=lambda item: item[1], reverse=True))

        response = "Qn: " +  question
        response = response + "\nVerses:\n"

        # get top N results
        N = 8
        sliced_result = dict(itertools.islice(sorted_result.items(), N))

        for item in sliced_result:
            indices = item.split("_")
            surah = indices[0]
            aya = indices[1]
            response = response + str(surah) + ":" + str(aya) + " " + self.get_verse(surah, aya) + "\n"
            response = response + "https://uxquran.com/apps/quran-ayat/?sura=" + surah + "&aya=" + aya + "\n\n"

        return response


# quran = QuranSimilarVerses("./", "embeddings_wahiddudin_hugg", "input.json", "")
# answer = quran.get_similar("How many years did Ashabul Khaf sleep in the cave")
# print(answer)