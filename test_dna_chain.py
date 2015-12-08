"""
11-17-15

Test the DNA chain structure and DNACrawler functionality.
"""


import unittest

from dna_chain import DNANode
from dna import DNA


class TestNode(DNANode):
    def __init__(self, name):
        super(TestNode, self).__init__()
        self.name = name

    def __repr__(self):
        s = super(TestNode, self).__repr__()[:-1]
        return '{} name={}>'.format(s, self.name)


class test_utils(unittest.TestCase):

    def check_seq(self, n1, n2):
        """
        Check that n1 and n2 are linked to each other, (n1 first).
        """

        self.assertIs(n1.dna_node_next_sib, n2)
        self.assertIs(n2.dna_node_prev_sib, n1)

    def check_child(self, n_par, n_chi):
        """
        Check that n_par and n_chi are in a parent-child relationship.
        """

        self.assertIs(n_par.dna_node_child, n_chi)
        self.assertIs(n_chi.dna_node_parent, n_par)


class tests(test_utils):

    def setUp(self):
        self.dna = DNA()

        self.n1 = TestNode('node1')
        self.n2 = TestNode('node2')
        self.n3 = TestNode('node3')
        self.n4 = TestNode('node4')

        self.dna.head = self.n1
        self.crawler = self.dna.spawn_crawler()
        self.crawler.attach_to(self.n1)

    # test inserting (before, after, child)

    def test_1_insert_before(self):
        self.crawler.add_before(self.n2)
        self.check_seq(self.n2, self.n1)

        self.assertIsNone(self.n2.dna_node_prev_sib)
        self.assertIsNone(self.n1.dna_node_next_sib)

    def test_2_insert_after(self):
        self.crawler.add_after(self.n2)
        self.check_seq(self.n1, self.n2)

        self.assertIsNone(self.n1.dna_node_prev_sib)
        self.assertIsNone(self.n2.dna_node_next_sib)

    def test_3_insert_child(self):
        self.crawler.add_child(self.n3)
        self.check_child(self.n1, self.n3)

    # test removing

    def test_4_remove_head(self):
        c = self.crawler
        c.add_after(self.n2, self.n1)
        c.add_after(self.n3, self.n2)
        c.remove(self.n1)

        self.assertRaises(AssertionError, self.check_seq, self.n1, self.n2)
        self.assertIsNone(self.n1.dna_node_next_sib)

    def test_5_remove_tail(self):
        c = self.crawler
        c.add_after(self.n2, self.n1)
        c.add_after(self.n3, self.n2)
        c.remove(self.n3)

        self.assertRaises(AssertionError, self.check_seq, self.n2, self.n3)
        self.assertIsNone(self.n3.dna_node_prev_sib)

    def test_6_remove_middle(self):
        c = self.crawler
        c.add_after(self.n2, self.n1)
        c.add_after(self.n3, self.n2)
        c.remove(self.n2)

        self.check_seq(self.n1, self.n3)
        self.assertIsNone(self.n2.dna_node_next_sib)
        self.assertIsNone(self.n2.dna_node_prev_sib)

    def test_7_remove_child(self):
        c = self.crawler
        c.add_child(self.n2, self.n1)
        c.add_after(self.n3, self.n2)
        c.remove(self.n2)

        self.check_child(self.n1, self.n3)
        self.assertIsNone(self.n2.dna_node_parent)
        self.assertIsNone(self.n2.dna_node_next_sib)
        self.assertIsNone(self.n2.dna_node_prev_sib)

    # test low-level traversing

    def test_8_traverse_sibs(self):
        c = self.crawler
        c.add_child(self.n2, self.n1)
        c.add_after(self.n3, self.n1)

        self.assertIs(self.n1, c.current_node)
        self.assertIs(self.n3, c.next_sib())
        self.assertIsNone(c.next_sib())

    def test_9_traverse_node_flat(self):
        c = self.crawler
        c.add_after(self.n2, self.n1)
        c.add_after(self.n3, self.n2)

        self.assertIs(self.n1, c.current_node)
        self.assertIs(self.n2, c.next_node())
        self.assertIs(self.n3, c.next_node())
        self.assertIsNone(c.next_node())

    def test_10_traverse_node_wchild(self):
        c = self.crawler
        c.add_child(self.n2, self.n1)
        c.add_after(self.n3, self.n1)

        c = self.crawler
        self.assertIs(self.n1, c.current_node)
        self.assertIs(self.n2, c.next_node())
        self.assertIs(self.n3, c.next_node())
        self.assertIsNone(c.next_node())

    # test crawling

    def test_11_crawl_sibs(self):
        c = self.crawler
        c.add_child(self.n2, self.n1)
        c.add_after(self.n3, self.n1)

        gen = c.crawl_sibs()
        self.assertIs(self.n1, gen.next())
        self.assertIs(self.n3, gen.next())
        self.assertRaises(StopIteration, gen.next)

    def test_12_crawl_flat(self):
        c = self.crawler
        c.add_after(self.n2, self.n1)
        c.add_after(self.n3, self.n2)

        gen = c.crawl()
        self.assertIs(self.n1, gen.next())
        self.assertIs(self.n2, gen.next())
        self.assertIs(self.n3, gen.next())
        self.assertRaises(StopIteration, gen.next)

    def test_13_crawl_wchild(self):
        c = self.crawler
        c.add_child(self.n2, self.n1)
        c.add_after(self.n3, self.n1)

        gen = c.crawl()
        self.assertIs(self.n1, gen.next())
        self.assertIs(self.n2, gen.next())
        self.assertIs(self.n3, gen.next())
        self.assertRaises(StopIteration, gen.next)

    def test_14_crawl_w_mul_children(self):
        """
        Tests that when traversing this stucture we correctly jump from n3 to
        n4.

            n1 -- n2 -- n3
            |
            n4
        """
        c = self.crawler
        c.add_child(self.n2, self.n1)
        c.add_child(self.n3, self.n2)
        c.add_after(self.n4, self.n1)

        gen = c.crawl()
        self.assertIs(self.n1, gen.next())
        self.assertIs(self.n2, gen.next())
        self.assertIs(self.n3, gen.next())
        self.assertIs(self.n4, gen.next())
        self.assertRaises(StopIteration, gen.next)


if __name__ == '__main__':
    unittest.main()
