"""
11-11-15
"""


from dna_chain import DNACrawler


__globals__ = ('DNA', )


class DNA(object):
    def __init__(self):
        self.head = None

    def spawn_crawler(self):
        c = DNACrawler(self)
        c.attach_to(self.head)
        return c
