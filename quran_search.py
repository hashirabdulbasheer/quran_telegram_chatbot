#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
from flask import json

class QuranSearch:

    MAX_NUM_RESULTS = 10

    @staticmethod
    def __normalize(input):
          input = input.replace('\u0610', '') #ARABIC SIGN SALLALLAHOU ALAYHE WA SALLAM
          input = input.replace('\u0611', '') #ARABIC SIGN ALAYHE ASSALLAM
          input = input.replace('\u0612', '') #ARABIC SIGN RAHMATULLAH ALAYHE
          input = input.replace('\u0613', '') #ARABIC SIGN RADI ALLAHOU ANHU
          input = input.replace('\u0614', '') #ARABIC SIGN TAKHALLUS

          #Remove koranic anotation
          input = input.replace('\u0615', '') #ARABIC SMALL HIGH TAH
          input = input.replace('\u0616', '') #ARABIC SMALL HIGH LIGATURE ALEF WITH LAM WITH YEH
          input = input.replace('\u0617', '') #ARABIC SMALL HIGH ZAIN
          input = input.replace('\u0618', '') #ARABIC SMALL FATHA
          input = input.replace('\u0619', '') #ARABIC SMALL DAMMA
          input = input.replace('\u061A', '') #ARABIC SMALL KASRA
          input = input.replace('\u06D6', '') #ARABIC SMALL HIGH LIGATURE SAD WITH LAM WITH ALEF MAKSURA
          input = input.replace('\u06D7', '') #ARABIC SMALL HIGH LIGATURE QAF WITH LAM WITH ALEF MAKSURA
          input = input.replace('\u06D8', '') #ARABIC SMALL HIGH MEEM INITIAL FORM
          input = input.replace('\u06D9', '') #ARABIC SMALL HIGH LAM ALEF
          input = input.replace('\u06DA', '') #ARABIC SMALL HIGH JEEM
          input = input.replace('\u06DB', '') #ARABIC SMALL HIGH THREE DOTS
          input = input.replace('\u06DC', '') #ARABIC SMALL HIGH SEEN
          input = input.replace('\u06DD', '') #ARABIC END OF AYAH
          input = input.replace('\u06DE', '') #ARABIC START OF RUB EL HIZB
          input = input.replace('\u06DF', '') #ARABIC SMALL HIGH ROUNDED ZERO
          input = input.replace('\u06E0', '') #ARABIC SMALL HIGH UPRIGHT RECTANGULAR ZERO
          input = input.replace('\u06E1', '') #ARABIC SMALL HIGH DOTLESS HEAD OF KHAH
          input = input.replace('\u06E2', '') #ARABIC SMALL HIGH MEEM ISOLATED FORM
          input = input.replace('\u06E3', '') #ARABIC SMALL LOW SEEN
          input = input.replace('\u06E4', '') #ARABIC SMALL HIGH MADDA
          input = input.replace('\u06E5', '') #ARABIC SMALL WAW
          input = input.replace('\u06E6', '') #ARABIC SMALL YEH
          input = input.replace('\u06E7', '') #ARABIC SMALL HIGH YEH
          input = input.replace('\u06E8', '') #ARABIC SMALL HIGH NOON
          input = input.replace('\u06E9', '') #ARABIC PLACE OF SAJDAH
          input = input.replace('\u06EA', '') #ARABIC EMPTY CENTRE LOW STOP
          input = input.replace('\u06EB', '') #ARABIC EMPTY CENTRE HIGH STOP
          input = input.replace('\u06EC', '') #ARABIC ROUNDED HIGH STOP WITH FILLED CENTRE
          input = input.replace('\u06ED', '') #ARABIC SMALL LOW MEEM

          #Remove tatweel
          input = input.replace('\u0640', '')

          #Remove tashkeel
          input = input.replace('\u064B', '') #ARABIC FATHATAN
          input = input.replace('\u064C', '') #ARABIC DAMMATAN
          input = input.replace('\u064D', '') #ARABIC KASRATAN
          input = input.replace('\u064E', '') #ARABIC FATHA
          input = input.replace('\u064F', '') #ARABIC DAMMA
          input = input.replace('\u0650', '') #ARABIC KASRA
          input = input.replace('\u0651', '') #ARABIC SHADDA
          input = input.replace('\u0652', '') #ARABIC SUKUN
          input = input.replace('\u0653', '') #ARABIC MADDAH ABOVE
          input = input.replace('\u0654', '') #ARABIC HAMZA ABOVE
          input = input.replace('\u0655', '') #ARABIC HAMZA BELOW
          input = input.replace('\u0656', '') #ARABIC SUBSCRIPT ALEF
          input = input.replace('\u0657', '') #ARABIC INVERTED DAMMA
          input = input.replace('\u0658', '') #ARABIC MARK NOON GHUNNA
          input = input.replace('\u0659', '') #ARABIC ZWARAKAY
          input = input.replace('\u065A', '') #ARABIC VOWEL SIGN SMALL V ABOVE
          input = input.replace('\u065B', '') #ARABIC VOWEL SIGN INVERTED SMALL V ABOVE
          input = input.replace('\u065C', '') #ARABIC VOWEL SIGN DOT BELOW
          input = input.replace('\u065D', '') #ARABIC REVERSED DAMMA
          input = input.replace('\u065E', '') #ARABIC FATHA WITH TWO DOTS
          input = input.replace('\u065F', '') #ARABIC WAVY HAMZA BELOW
          input = input.replace('\u0670', '') #ARABIC LETTER SUPERSCRIPT ALEF

          #Replace Waw Hamza Above by Waw
          input = input.replace('\u0624', '\u0648')

          #Replace Ta Marbuta by Ha
          input = input.replace('\u0629', '\u0647')

          #Replace Ya
          # and Ya Hamza Above by Alif Maksura
          input = input.replace('\u064A', '\u0649')
          input = input.replace('\u0626', '\u0649')

          # Replace Alifs with Hamza Above/Below
          # and with Madda Above by Alif
          input = input.replace('\u0622', '\u0627')
          input = input.replace('\u0623', '\u0627')
          input = input.replace('\u0625', '\u0627')

          return input


    @staticmethod
    def __similar(first, second) -> float:
        # if both are null
        if first is None and second is None:
            return 1;

        # as both are not null if one of them is null then return 0
        if first is None or second is None:
            return 0;

        # remove all whitespace
        first = re.sub(r"\s+\b|\b\s", "", first)
        second = re.sub(r"\s+\b|\b\s", "", second)

        # if both are empty strings
        if first == "" and second == "":
            return 1;

        # if only one is empty string
        if first == "" or second == "":
            return 0;

        # identical
        if first == second:
            return 1

        # both are 1-letter strings
        if len(first) == 1 and len(second) == 1:
            return 0

        # if either is a 1-letter string
        if len(first) < 2 or len(second) < 2:
            return 0

        firstBigrams = {}
        for i in range(0, len(first)-1):
            bigram = first[i:i+2]
            count = 0
            if bigram in firstBigrams:
                count = firstBigrams[bigram] + 1
            else:
                count = 1

            firstBigrams[bigram] = count


        intersectionSize = 0
        for i in range(0, len(second)-1):
            bigram = second[i:i+2]
            count = 0
            if bigram in firstBigrams:
                count = firstBigrams[bigram]
            else:
                count = 0

            if count > 0:
                firstBigrams[bigram] = count - 1;
                intersectionSize = intersectionSize + 1

        return (2.0 * intersectionSize) / (len(first) + len(second) - 2);


    @staticmethod
    def __sortFunc(e):
      return e["score"]

    @staticmethod
    def search_word(word, count = None, json_path = None):
        data_path = "./wordslist.json"
        if json_path:
            data_path = json_path
        json_data = open(data_path)
        data = json.load(json_data)
        is_arabic_input = \
            re.search("[\u0600-\u06ff]|[\u0750-\u077f]|[\ufb50-\ufc3f]|[\ufe70-\ufefc]"
                      , word)
        results = []
        for w in data:
            score = 0
            if is_arabic_input:
                normalized_w = QuranSearch.__normalize(w['ar'])
                normalized_input = QuranSearch.__normalize(word)
                score = QuranSearch.__similar(u'{}'.format(normalized_w), u'{}'.format(normalized_input))
            else:
                score = QuranSearch.__similar(u'{}'.format(w['tr']), u'{}'.format(word))

            if score-0.5 > 0:
                results.append({"score": score, "word": w})

        if len(results) > 0:
            # sort based on score
            results.sort(key=QuranSearch.__sortFunc, reverse=True)

            # return count items
            max = QuranSearch.MAX_NUM_RESULTS
            if count:
                max = count
            if len(results) > max:
                return results[:max]
            return results

        return results

