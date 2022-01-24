import random
from difflib import SequenceMatcher


# Each Bayes network node is associated with a few events,
# each event can occur with its own probability
# when we learn we accumulate this probability and then
# synthesize it aftificially using ranges which ratios
# from total amount of all occurences vs occurences of
# each event.
class BayesNode:
    def __init__(self, data):
        self.outcomes = { }
        self.total = 0.0
        self.ranges = [ ]
        self.data = data

    def learn_outcome(self, node):
        if node not in self.outcomes:
                self.outcomes[node] = 0.0
        self.outcomes[node] += 1.0
        self.total += 1
        self._regenerate_ranges()
        print("Node ", self.data, "learned outcome ", node.data, self.outcomes, self.total, "prob ", self.outcomes[node] / self.total)
        print(self.outcomes, self.total)
        print(self.ranges)

    def print_info(self):
        print("Node ", self.data)
        print("=======================================")
        print("Outcomes:")
        for node in self.outcomes:
            print("Node", node.data, "hits", self.outcomes[node], "prob", self.outcomes[node] / self.total)
        print("=======================================")

    def print_info_str(self):
        s = "Node " + str(self.data) + "\n"
        s += "=======================================\n"
        s += "Outcomes:\n"
        for node in self.outcomes:
            s += "Node " + str(node.data) + " hits " + str(self.outcomes[node]) + " prob " + str(self.outcomes[node] / self.total) + "\n"
        s += "=======================================\n"
        return s

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

# If we get some state which we haven't learned yet,
# we need to do some clasification to associate it
# with something we know.
# There can be multiple ways to do that, currently
# those are using minimum string distance, if we consider
# the state as a whole
class ObjectStringAssociator:
    def __init__(self):
        self.objects = [ ]
    def register_object(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)
    def find_closest(self, obj):
        max_ratio = None
        max_obj = None
        if len(self.objects) == 0:
            print ("No registered objects!")
        for o in self.objects:
            r = SequenceMatcher(None, str(o), str(obj)).ratio()
            if max_ratio == None:
                max_ratio = r
                max_obj = o
            elif max_ratio < r:
                max_ratio = r
                max_obj = o
        return max_obj

# for non correlated events it is better to use
# weighted approach as not all factors are equally
# valueble in informational sense.
# The factors which tend to have more different states
# have less weight than those which have less degrees
# of freedom
# i.e here we go through all the attributes we know
# checking if attribute value has been seen already,
# if it hasn't been seen the value is added to the 
# attribute.
# If the attribute itself haven't been seen - it is
# added to the attributes list
# Then weight of each attribute is calculated as
# total_occurences of all attributes divided by
# number of degrees of freedom 
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
        print(self.attribute_registrator)
    def _calc_weight(self, ind):
        print("Attr: ", self.attribute_registrator[ind])
        weight = self.total_occurences / len(self.attribute_registrator[ind])
        return weight
    def find_closest(self, obj):
        max_obj = self.objects[0]
        max_weight = int(0)
        for o in self.objects:
            w = 0.0
            for ind in range(0, min(len(o), len(obj))):
                if type(o) == str:
                    r = SequenceMatcher(None, str(o), str(obj)).ratio()
                    w += self._calc_weight(ind) * r
                else:
                    diff = float(abs(int(o[ind]) - int(obj[ind])))
                    w += self._calc_weight(ind) / diff
            print(o, "Weight: ", w)
            if w > max_weight:
                max_obj = o
                max_weight = w
        return max_obj

class BayesNetwork:
    def __init__(self, t):
        self.hash_to_nodes = { }
        self.nodes = [ ]
        self.associator = t()
    def learn_outcomes(self, objects):
        for o in objects:
            if str(o) not in self.hash_to_nodes:
                print(o, " is not in ", self.hash_to_nodes, str(o))
                node = BayesNode(o)
                self.hash_to_nodes[str(o)] = node
                self.nodes.append(node)
                self.associator.register_object(o)
        nodes = [ self.hash_to_nodes[str(o)] for o in objects ]
        for i in range(0, len(nodes) - 1):
            nodes[i].learn_outcome(nodes[i+1])
    def predict_outcome(self, _o, steps):
        objects = [ ]
        print(self.hash_to_nodes)
        if str(_o) not in self.hash_to_nodes:

            o = self.associator.find_closest(_o)
        else:
            o = _o
        print("Closest is: ", o, self.hash_to_nodes, str(o))
        node = self.hash_to_nodes[str(o)]
        print("Node is ", node, node.outcomes)
        for i in range(0, steps):
            node = node.predict_outcome()
            if node == None:
                return objects
            objects.append(node.data)
        return objects

    def print_info(self):
        for node in self.nodes:
            node.print_info()

    def print_info_str(self):
        s = ""
        for node in self.nodes:
            s += node.print_info_str()
        return s

def test_orthogonal_associator():
    net = BayesNetwork(ObjectOrthogonalAssociator)
    net.learn_outcomes([ "Human", "Stanislav" ])
    net.learn_outcomes([ "Human", "Jane" ])
    net.learn_outcomes([ "Human", "Slava" ])
    net.learn_outcomes([ "Dog", "Mahmud" ])
    net.learn_outcomes([ "Dog", "Marianna" ])
    net.learn_outcomes([ "Slava", "Wolfy" ])
    net.learn_outcomes([ "Dog", "Wolfy" ])
    print(net.predict_outcome("Doglava", 2))

def test_string_associator():
    net = BayesNetwork(ObjectStringAssociator)
    net.learn_outcomes([ "Human", "Stanislav" ])
    net.learn_outcomes([ "Human", "Jane" ])
    net.learn_outcomes([ "Human", "Slava" ])
    net.learn_outcomes([ "Dog", "Mahmud" ])
    net.learn_outcomes([ "Dog", "Marianna" ])
    net.learn_outcomes([ "Slava", "Wolfy" ])
    net.learn_outcomes([ "Dog", "Wolfy" ])
    print(net.predict_outcome("Doglava", 2))



def test():
    #net = BayesNetwork(ObjectOrthogonalAssociator)

    #net.learn_outcomes([ "one", "two", "three" ])
    #net.learn_outcomes([ "four", "two", "four" ])
    test_orthogonal_associator()
    test_string_associator()
    #return net.predict_outcome("tone", 4)


test()
