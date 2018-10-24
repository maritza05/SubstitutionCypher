import random
from math import log10
from collections import Counter, OrderedDict
import operator
import re

class SubstitutionCypher:

    def __init__(self, key=None):
        self.ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
        if key is None:
            self.KEY = self._generate_random_key()
        else:
            self.KEY = key

    def encrypt(self, message):
        result = ''
        message = message.lower()
        for c in message:
            result += self._encrypt_char(c)
        return result

    def decrypt(self, encrypted_message):
        result = ''
        for c in encrypted_message:
            result += self._decrypt_char(c)
        return result

    def _encrypt_char(self, char):
        if char.isspace():
            return char
        idx = self.ALPHABET.find(char)
        return self.KEY[idx]

    def _decrypt_char(self, char):
        if char.isspace():
            return char
        idx = self.KEY.find(char)
        return self.ALPHABET[idx]

    def _generate_random_key(self):
        key = ''
        for i in range(26):
            key += self._generate_unrepeated_random_character(key)
        return key

    def _generate_unrepeated_random_character(self, key):
        letter = self._generate_random_character()
        while letter in key:
            letter = self._generate_random_character()
        return letter

    def _generate_random_character(self):
        char_index = random.randint(0, 25)
        letter = self.ALPHABET[char_index]
        return letter



class FitnessMeasure:

    def __init__(self, ngrams_file, sep=' '):
        ngrams = self._get_ngrams_from_file(ngrams_file)
        self.N = self._get_total_count_ngrams(ngrams)
        self.ngrams = self._get_ngrams_probability(ngrams)
        self.floor = log10(0.01/self.N)

    def score(self, text):
        score = 0
        text_ngrams = self._get_text_ngrams(text, 4)
        for n in text_ngrams:
            if n in self.ngrams.keys():
                score += self.ngrams[n]
            else:
                score += self.floor
        return score

    def _get_ngrams_from_file(self, ngrams_file):
        ngrams = {}
        lines = self._read_ngrams_file(ngrams_file)
        for line in lines:
            key, count = line.split()
            ngrams[key] = int(count)
        return ngrams

    def _get_total_count_ngrams(self, ngrams):
        return sum(ngrams.values())

    def _get_ngrams_probability(self, ngrams):
        for key in ngrams.keys():
            ngrams[key] = log10(float(ngrams[key]) / self.N)
        return ngrams

    def _get_text_ngrams(self, text, n):
        result = []
        text = re.sub('[^A-Z]','',text.upper())
        for i in range(len(text)-n+1):
            result.append(text[i:i+n])
        return result

    def _read_ngrams_file(self, ngrams_file):
        with open(ngrams_file) as file:
            lines = file.readlines()
        return lines



class SubstitutionBreaker:

    def __init__(self):
        self.LETTERS_BY_FREQ = 'etaoinshrdlcumwfgypbvkjxqz'
        self.ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
        self.fm = FitnessMeasure('english_quadgrams.txt')
        self.maxscore = -99e9

    def decrypt(self, text):
        text = re.sub('[^A-Za-z\s]','',text.lower())
        maxscore = -99e9
        i = 0
        while 1:
            i = i+1
            parentkey = self._get_initial_guess_key(text)
            deciphered = SubstitutionCypher(key=parentkey).decrypt(text)
            parentscore = self.fm.score(deciphered)
            count = 0

            while count < 1000:
                child = self._swap_chars(parentkey)
                deciphered = SubstitutionCypher(key=child).decrypt(text)
                score = self.fm.score(deciphered)
                if score > parentscore:
                    parentscore = score
                    parentkey = child[:]
                    count = 0
                count = count + 1
            if parentscore > maxscore:
                maxscore, maxkey = parentscore, parentkey[:]
                print(f'\nbest score so far: {maxscore}, on iteration {i}')
                ss = SubstitutionCypher(key=maxkey)
                print(f'best key: {maxkey}')
                print(f'plaintext: {ss.decrypt(text)}')



    def _swap_chars(self, text):
        idx1 = random.randint(0, len(text) - 1)
        idx2 = random.randint(0, len(text) - 1)
        if idx1 != idx2:
            text_list = list(text)
            text_list[idx2], text_list[idx1] = text_list[idx1], text_list[idx2]
            return ''.join(text_list)
        else:
            return self._swap_chars(text)


    def _get_initial_guess_key(self, message):
        message = message.lower()
        chars_freq = self._get_chars_by_frequency(message)
        mapped_chars = self._map_frequency_letters(chars_freq)
        mapped_chars = sorted(mapped_chars.items())
        key = ''
        for k, v in mapped_chars:
            key += v
        return key

    def _map_frequency_letters(self, chars):
        correspondency_table = {}
        for idx, c in enumerate(self.LETTERS_BY_FREQ):
            if idx < len(chars):
                correspondency_table[c] = chars[idx]
            else:
                correspondency_table[c] = self._get_random_unrepeated_char(list(correspondency_table.values()))
        return correspondency_table

    def _get_random_unrepeated_char(self, chars):
        char_index = random.randint(0, 25)
        letter = self.ALPHABET[char_index]
        if letter in chars:
            return self._get_random_unrepeated_char(chars)
        else:
            return letter

    def _get_chars_by_frequency(self, message):
        freq_table = Counter(message).most_common()
        return [item[0] for item in freq_table]


if __name__ == "__main__":
    sb = SubstitutionBreaker()
    with open('test.txt') as file:
        message = file.read().replace('\n', '')
    print("=" * 40)
    print("PLEASE USE CTRL+C TO END THE PROGRAM")
    print("=" * 40)
    sb.decrypt(message)
