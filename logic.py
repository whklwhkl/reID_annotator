from data import Node
from random import choice


class Annotation:
    def __init__(self, inputs, heuristics=None):
        nodes = set(Node(x) for x in inputs)
        self.candidates = {k: set(n for n in nodes - set(k) if n.name > k.name) for k in nodes}
        self.visited = {k: set() for k in nodes}
        self.get_node = {x.name: x for x in nodes}
        l = len(nodes)
        self.max_step = l * (l - 1) // 2
        self.heuristics = heuristics

    def new_job(self):
        if self.heuristics:
            while len(self.heuristics):
                k, n = map(self.get_node.__getitem__, self.heuristics.pop())
                if k not in self.candidates:
                    continue
                elif n in self.candidates[k]:
                    return k, n
                else:
                    continue
        for k, v in self.candidates.items():
            if len(v):
                n = choice(list(v))
                return k, n

    def _ignore(self, n):
        # n = self.get_node[n]
        ns = self.candidates.pop(n)
        self.max_step -= len(ns)
        for k in self.candidates:
            if k.name < n.name:
                if n in self.candidates[k]:
                    self.candidates[k].remove(n)
                    self.max_step -= 1
        ns = self.visited.pop(n)

    def ignore(self, n):
        n = self.get_node[n]
        self._ignore(n)

    def submit(self, merge:bool, n1, n2):
        n1 = self.get_node[n1]
        n2 = self.get_node[n2]
        try:
            self.candidates[n1].remove(n2)
            self.visited[n1].add(n2)
        except KeyError:
            # in case of consistency issues
            return
        if merge:
            r1 = n1.to_root()
            r2 = n2.to_root()
            if r1.name > r2.name:
                n = r1.attach(r2)
            else:
                n = r2.attach(r1)
            if n:
                self._ignore(n)
                ## TODO: inherit heuristics
        else:
            self.max_step -= 1


class AnnotationFromScratch(Annotation):
    def __init__(self, inputs):
        nodes = set(Node(x) for x in inputs)
        self.candidates = {k: set(n for n in nodes - set(k) if n.name > k.name) for k in nodes}
        self.visited = {k: set() for k in nodes}
        self.get_node = {x.name: x for x in nodes}
        l = len(nodes)
        self.max_step = l * (l - 1) // 2
        self.heuristics = None
