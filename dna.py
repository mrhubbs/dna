"""
11-11-15
"""


from dna_chain import DNACrawler, DNANode


__globals__ = ('DNA', )


class DNA(object):
    """
    A language to describe changes:

    Two contexts: DNA chain or DNA node

        DNA chain: context is chain ( c )
            - remove node
                ( c - NODE )
            + add node
                c/a/b (child / sibling after / sibling before)
                ( c + NODE c/a/b REF_NODE )
            ^ move node
                c/a/b (child / sibling after / sibling before)
                ( c ^ NODE c/a/b REF_NODE )

        DNA node: context is node ( n )
            + add attribute
                ( n + NAME OBJECT)
            - delete attribute
                ( n - NAME )
            ^ change attribute
                ( n ^ NAME OBJECT )
    """

    def __init__(self, **kwargs):
        self.head = None
        self.node_factory = kwargs.get('node_factory', DNANode)

        self.__rnas = []

    def link(self, rna, update=True):
        if rna not in self.__rnas:
            self.__rnas.append(rna)
            if update:
                # TODO: update RNA
                pass

    def unlink(self, rna):
        if rna in self.__rnas:
            self.__rnas.remove(rna)

    def spawn_crawler(self):
        c = DNACrawler(self)
        c.attach_to(self.head)
        return c
