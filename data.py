

class Node:
    def __init__(self, name: str):
        self.name = name
        self.parent = None
        self.children = []

    def to_root(self):
        x = self
        while x.parent:
            x = x.parent
        return x

    def attach(self, p):
        if self.parent:
            return None
        else:
            self.parent = p
            p.children.append(self)
            return self

    def __iter__(self):
        yield self
        for n in self.children:
            if len(n.children):
                yield from n
            else:
                yield n


def main():
    n1 = Node('1')
    n2 = Node('2')
    n3 = Node('3')
    n3.attach(n2)
    n2.attach(n1)
    print(n3.to_root().name)
    print(n3.attach(n2))
    for n in n1:
        print(n.name)
    print(len(list(n1)))


if __name__ == '__main__':
    main()
