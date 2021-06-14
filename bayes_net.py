import random
from difflib import SequenceMatcher



class BayesNode:
    def __init__(self, data):
        self.outcomes = { }
        self.total = 0
        self.ranges = [ ]
        self.data = data

    def learn_outcome(self, node):
        if node not in self.outcomes:
                self.outcomes[node] = 0
        self.outcomes[node] += 1
        self.total += 1
        self._regenerate_ranges()
        print (self.outcomes, self.total)
        print (self.ranges)

    def predict_outcome(self):
        i = random.randint(0, self.total)
        for r in  self.ranges:
            if i >= r[0] and i <= r[1]:
                return r[2]
        return None

    def _regenerate_ranges(self):
        r = 0
        ranges = [ ]
        for n in self.outcomes:
            ranges.append(( r, r + self.outcomes[n], n))
            r += self.outcomes[n]
        self.ranges = ranges

class ObjectStringAssociator:
    def __init__(self):
        self.objects = [ ]
    def register_object(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)
    def find_closest(self, obj):
        max_ratio = 0
        max_obj = None
        for o in self.objects:
            r = SequenceMatcher(None, str(o), str(obj)).ratio()
            if max_ratio < r:
                max_ratio = r
                max_obj = o
        return max_obj

class ObjectOrthogonalAssociator:
    def __init__(self):
        self.total_occurences = 0
        self.attribute_registrator = [ ]
        self.objects = [ ]
    def register_object(self, obj):
        ind = 0
        for i in obj:
            if ind >= len(self.attribute_registrator):
                self.attribute_registrator.append([ ])
            if i not in self.attribute_registrator[ind]:
                self.attribute_registrator[ind].append(i)
            ind += 1
        if obj not in self.objects:
            self.objects.append(obj)
        self.total_occurences += 1
        print (self.attribute_registrator)
    def _calc_attr_match_metric(self, o1, o2, ind):
        if type(o1) == str:
            dist = float(abs(ord(o1[ind]) - ord(o2[ind])))
        else:
            dist = float(abs(int(o1[ind]) - int(o2[ind])))
        weight = self.total_occurences / len(self.attribute_registrator[ind])
        return dist / weight
    def find_closest(self, obj):
        min_obj = self.objects[0]
        min_weight = int(4000000)
        for o in self.objects:
            w = 0.0
            for ind in xrange(0, min(len(o), len(obj))):
                w += self._calc_attr_match_metric(o, obj, ind)
            if w < min_weight:
                min_obj = o
                min_weight = w
        return min_obj

class BayesNetwork:
    def __init__(self, t):
        self.hash_to_nodes = { }
        self.nodes = { }
        self.associator = t()
    def learn_outcomes(self, objects):
        for o in objects:
            if hash(o) not in self.hash_to_nodes:
                self.hash_to_nodes[hash(o)] = BayesNode(o)
                self.associator.register_object(o)
        nodes = [ self.hash_to_nodes[hash(o)] for o in objects ]
        for i in range(0, len(nodes) - 1):
            nodes[i].learn_outcome(nodes[i+1])
    def predict_outcome(self, _o, steps):
        objects = [ ]
        if hash(_o) not in self.hash_to_nodes:
            o = self.associator.find_closest(_o)
        else:
            o = _o
        node = self.hash_to_nodes[hash(o)]
        for i in range(0, steps):
            node = node.predict_outcome()
            if node == None:
                return objects
            objects.append(node.data)
        return objects

def test():
    net = BayesNetwork(ObjectStringAssociator)

    net.learn_outcomes([ "one", "two", "three" ])
    net.learn_outcomes([ "four", "two", "four" ])
    return net.predict_outcome("tone", 4)


print (test())
