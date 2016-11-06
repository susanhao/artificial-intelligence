import math
import email
import collections
import os
import time

############################################################
# Section 1: Spam Filter
############################################################

def load_tokens(email_path):
    with open(email_path, 'r') as f:
        message = email.message_from_file(f)
    out = []
    m = [out.extend(x.split()) for x in email.Iterators.body_line_iterator(message)]
    return out

def log_probs(email_paths, smoothing):
    toks = []
    m = [toks.extend(load_tokens(x)) for x in email_paths]
    c = collections.Counter(toks)
    z = len(toks) + smoothing * (len(c) + 1)
    d = {"<UNK>" : math.log(smoothing/z)}
    for x in c:
        d[x] = math.log((c[x] + smoothing) / z)
    return d

class SpamFilter(object):

    def __init__(self, spam_dir, ham_dir, smoothing):
        self.spam_dir = os.listdir(spam_dir)
        self.not_spam_dir = os.listdir(ham_dir)
        self.spam_dict = log_probs([(spam_dir + '/' + x) for x in self.spam_dir], smoothing)
        self.not_spam_dict =log_probs([(ham_dir + '/' + x) for x in self.not_spam_dir], smoothing)
        self.prob_spam = math.log(float (len(self.spam_dir)) / (len(self.spam_dir) + len(self.not_spam_dict)))
        self.prob_not_spam = math.log(1 - self.prob_spam)
    
    def is_spam(self, email_path):
        prob_spam = self.prob_spam
        prob_not_spam = self.prob_not_spam
        c = collections.Counter(load_tokens(email_path))
        for x in c:
            if x in self.spam_dict:
                temp = self.spam_dict[x] * c[x]
            else:
                temp = self.spam_dict["<UNK>"] * c[x]
            prob_spam += temp

            if x in self.not_spam_dict:
                temp2 = self.not_spam_dict[x] * c[x]
            else:
                temp2 = self.not_spam_dict["<UNK>"] * c[x]
            prob_not_spam += temp2
        return prob_not_spam < prob_spam

    def most_indicative_spam(self, n):
        ind = {}
        m =[x for x in self.spam_dict if x in self.spam_dict and x in self.not_spam_dict]
        for x in m:
            temp = math.exp(self.spam_dict[x] + self.prob_spam)
            temp2 = math.exp(self.not_spam_dict[x] + self.prob_not_spam)
            ind[x] = self.spam_dict[x] - math.log(temp + temp2)
        return sorted(ind, key=ind.get, reverse=True)[:n]

    def most_indicative_ham(self, n):
        ind = {}
        m =[x for x in self.spam_dict if x in self.spam_dict and x in self.not_spam_dict]
        for x in m:
            temp = math.exp(self.spam_dict[x] + self.prob_spam)
            temp2 = math.exp(self.not_spam_dict[x] + self.prob_not_spam)
            ind[x] = self.not_spam_dict[x] - math.log(temp + temp2)
        return sorted(ind, key=ind.get, reverse=True)[:n]
