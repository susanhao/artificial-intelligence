

import collections

def load_corpus(path):
    with open(path, 'r') as f:
    	return [[tuple(x.split('=')) for x in y.split()] for y in f]

class Tagger(object):

    def __init__(self, sentences):
        self.tags = ['VERB', 'NOUN', 'ADV', 'ADJ', 'PRON', 'DET', 'PRT', '.', 'ADP', 'NUM', 'CONJ', 'X']
        self.a = collections.defaultdict(float)
        self.b = collections.defaultdict(float)
        self.pi = collections.defaultdict(float)

        pi_temp = collections.defaultdict(int)
        a_temp = collections.defaultdict(int)
        b_temp = collections.defaultdict(int)
        tag_temp = collections.defaultdict(int)

        for x in sentences:
        	for y in xrange(len(x)):
        		if y <= len(x) - 2:
        			a_temp[(x[y][1], x[y+1][1])] += 1
        		b_temp[(x[y][1], x[y][0])] += 1
        		tag_temp[x[y][1]] += 1
        	pi_temp[x[0][1]] += 1

        a_count = collections.Counter(list(a_temp))
        b_count = collections.Counter(list(b_temp))

        for (x, y) in a_temp:
        	self.a[(x, y)] = (a_temp[(x, y)] + 1e-10)/float(tag_temp[x] + 1e-10 * a_count[x])

        for (x, y) in b_temp:
        	self.b[(x, y)] = (b_temp[(x, y)] + 1e-10)/float(tag_temp[x] + 1e-10 * b_count[x])

        for x in pi_temp:
        	self.pi[x] = (pi_temp[x] + 1e-10)/float(len(sentences) + 1e-10 * len(pi_temp))

    def most_probable_tags(self, tokens):
    	d = [dict((x, y) for x, y in self.b.iteritems() if x[1] == t) for t in tokens]
    	ans = [max(x, key=x.get)[0] for x in d]
    	return ans

    def viterbi_tags(self, tokens):
        daisy = [{} for x in xrange(len(tokens))]
        neptune = [{} for x in xrange(len(tokens))]

        for x in self.tags:
        	daisy[0][x] = self.pi[x] * self.b[(x, tokens[0])]

        for x in xrange(1, len(tokens)):
        	for y in self.tags:
        		(daisy[x][y], neptune[x][y]) = max((daisy[x-1][t] * self.a[(t, y)] * self.b[(y, tokens[x])], t) for t in self.tags)

        pluto = [max((daisy[-1][x], x) for x in self.tags)[1]]


        [pluto.append(neptune[x][pluto[-1]]) for x in xrange(len(tokens) - 1, 0, -1)]
        return list(reversed(pluto))
