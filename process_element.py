import random
from difflib import SequenceMatcher


class ProcessNode:
    def __init__(self):
	self.in_node_list = [ ]
	self.out_node_list = [ ]
	self.state = None
    def add_node(self, node, out_node = False, bidir = False, mutual = False):
	if bidir:
	    self.in_node_list.append(node)
	    self.out_node_list.append(node)
	else:
	    if out_node:
		    self.out_node_list.append(node)
	    else:
		    self.in_node_list.append(node)
	if mutual:
	    node.add_node(self, out_node, False)
    def remove_node(self, node, mutual = True):
	if node in self.in_node_list:
	    i = self.in_node_list.index[node]
	    del self.in_node_list[i]
	if node in self.out_node_list:
	    i = self.out_node_list.index[node]
	    del self.out_node_list[i]
	if mutual:
	    node.remove_node(self, False)

    def get_state(self):
	return self.state

    def process(self):
	pass


class BooleanLogicNode(ProcessNode):
    def __init__(self, bits):
	ProcessNode.__init__(self)
	self.state = [ 0 for i in xrange(0, bits) ]

class LogicOne(BooleanLogicNode):
    def __init__(self, bits = 1):
	BooleanLogicNode.__init__(self, bits)
	self.state = [ 1 for i in xrange(0, bits) ]

class LogicZero(BooleanLogicNode):
    def __init__(self, bits = 1):
	BooleanLogicNode.__init__(self, bits)

class LogicAnd(BooleanLogicNode):
    def __init__(self, bits):
	BooleanLogicNode.__init__(self, bits)

    def process(self):
	res = all([ node.get_state() for node in self.in_node_list ])
	self.state = [ int(res) for i in xrange(0, len(self.state)) ]

class LogicOr(BooleanLogicNode):
    def __init__(self, bits):
	BooleanLogicNode.__init__(self, bits)

    def process(self):
	res = any([ node.get_state() for node in self.in_node_list ])
	self.state = [ int(res) for i in xrange(0, len(self.state)) ]

class LogicNot(BooleanLogicNode):
    def __init__(self, bits):
	BooleanLogicNode.__init__(self, bits)

    def process(self):
	self.state = [ int(not node.get_state()[0]) for node in self.in_node_list ]


one = LogicOne()
zero = LogicZero()

and_el = LogicAnd(2)
or_el = LogicOr(2)
and_el.add_node(one)
and_el.add_node(one)
and_el.process()

or_el.add_node(one)
or_el.add_node(zero)
or_el.process()

not_el = LogicNot(2)
not_el.add_node(or_el)
not_el.add_node(and_el)
not_el.process()

not_el2 = LogicNot(2)
not_el2.add_node(not_el)
not_el2.add_node(zero)
not_el2.process()

print and_el.get_state()
print or_el.get_state()
print not_el.get_state()
print not_el2.get_state()





