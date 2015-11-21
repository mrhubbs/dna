"""
11-11-15

The DNA structure is a doubly-linked list modified to support hierarchical
information.  It's intended to be a simple balance between memory efficiency
and computational efficiency.

Below is a visual of the DNA structure.  Each node has links to the next and
previous sibling.  If it has a child, it has a link to the FIRST child in the
chain.  The first child in a chain has a link back to its parent.

    ...
     |
  DNANode -- DNANode
     |          |
     |       DNANode
     |          |
     |       DNANode -- DNANode
     |          |          |
     |       DNANode    DNANode
     |
  DNANode
     |
  DNANode
     |
  DNANode -- DNANode
     |          |
     |       DNANode
     |
  DNANode
     |
  DNANode -- DNANode
     |
  DNANode
     |
  DNANode
     |
    ...
"""


from collections import deque


__globals__ = ('DNANode',
               'DNACrawlerException',
               'DNACrawler')


class DNANode(object):
    """
    The base unit of our DNA data structure.
    """

    def __init__(self):
        self._dna_node_child = None
        self._dna_node_parent = None
        self._dna_node_next_sib = None
        self._dna_node_prev_sib = None

    @property
    def dna_node_child(self):
        return self._dna_node_child

    @property
    def dna_node_parent(self):
        return self._dna_node_parent

    @property
    def dna_node_next_sib(self):
        return self._dna_node_next_sib

    @property
    def dna_node_prev_sib(self):
        return self._dna_node_prev_sib


class DNACrawlerException(Exception):
    pass


class DNACrawler(object):
    """
    An object for traversing, reading, and editing the DNA structure.
    """

    def __init__(self, dna):
        self.dna = dna
        self.__node = None
        self.__parent_node_stack = deque()

    # traversing/reading

    def attach_to(self, node):
        """
        The crawler will not be able to traverse any level higher than the node
        it's originally attached to.
        """
        self.__node = node
        self.__parent_node_stack.clear()

    def reset(self):
        self.__node = self.dna.head
        self.__parent_node_stack.clear()

    @property
    def current_node(self):
        return self.__node

    def next_node(self):
        """
        Move to and return the next node in the DNA.  Returns None if there is
        no next.
        """
        cur_node = self.__node

        if cur_node is None:
            return None

        stack = self.__parent_node_stack

        if cur_node.dna_node_child is not None:
            stack.append(cur_node)
            self.__node = cur_node.dna_node_child
        elif cur_node.dna_node_next_sib is not None:
            self.__node = cur_node.dna_node_next_sib
        else:
            # We may be at the end of the entire chain,
            # or just the local chain.
            if stack:
                # At the end of a local chain.
                cur_parent = stack.pop()
                self.__node = cur_parent.dna_node_next_sib
            else:
                # Nothing in the stack, at the end of the entire chain.
                self.__node = None

        return self.__node

    def next_sib(self):
        """
        Move to and return the next sibling in the DNA.  Returns None if there
        is no next.
        """

        cur_node = self.__node

        if cur_node is None:
            return None

        self.__node = cur_node.dna_node_next_sib
        return self.__node

    def crawl(self):
        """
        Traverse the entire structure from the current node to the end.
        """

        node = self.__node
        while node is not None:
            yield node
            node = self.next_node()

    def crawl_sibs(self):
        """
        Traverse all the siblings coming after
        (and including) the current node.
        """

        node = self.__node
        while node is not None:
            yield node
            node = self.next_sib()

    # editing

    def insert_before(self, node, basen=None):
        """
        Insert node before basen.  Use the current node if basen is not
        specified.
        """

        cur = self.__node if basen is None else basen
        if cur is None:
            raise DNACrawlerException(
                "Cannot insert, no node specified and current node is None.")

        if cur is self.dna.head:
            self.dna.head = node

        prev_n = cur._dna_node_prev_sib
        parent = cur._dna_node_parent

        # handle next/prev

        cur._dna_node_prev_sib = node
        node._dna_node_next_sib = cur

        if prev_n is not None:
            prev_n._dna_node_next_sib = node
            node._dna_node_prev_sib = prev_n

        # handle parent/child

        if parent is not None:
            cur._dna_node_parent = None
            node._dna_node_parent = parent
            parent._dna_node_child = node

    def insert_after(self, node, basen=None):
        """
        Insert node after basen.  User current node if basen is not specified.
        """

        cur = self.__node if basen is None else basen
        if cur is None:
            raise DNACrawlerException(
                "Cannot insert, no node specified and current node is None.")

        next_n = cur.dna_node_next_sib

        cur._dna_node_next_sib = node
        node._dna_node_prev_sib = cur

        if next_n is not None:
            next_n._dna_node_prev_sib = node
            node._dna_node_next_sib = next_n

    def insert_child(self, node, basen=None):
        """
        Insert node as child of basen.  Use current node if basen is not
        specified.
        """

        cur = self.__node if basen is None else basen
        if cur is None:
            raise DNACrawlerException(
                "Cannot insert, no node specified and current node is None.")

        child = cur._dna_node_child

        if child is None:
            # Easy, there is no child.
            cur._dna_node_child = node
            node._dna_node_parent = cur
        else:
            # There is already a child
            # TODO: this inserts node at the head of the list of children.
            # TODO: we probably want to insert it at the tail.
            self.insert_before(node, child)

    def remove(self, node=None):
        """
        Removes node from the chain.  Use current node if node is not
        specified.
        """

        node = self.__node if node is None else node
        if node is None:
            raise DNACrawlerException(
                "Cannot remove, no node specified and current node is None.")

        prev_n = node.dna_node_prev_sib
        next_n = node.dna_node_next_sib

        node._dna_node_next_sib = None
        node._dna_node_prev_sib = None

        # Does this node have a parent?
        if node.dna_node_parent is not None:
            # There should not be a prev in this case, check if there is a
            # next to link the parent to.

            node.dna_node_parent._dna_node_child = next_n
            if next_n is not None:
                next_n._dna_node_parent = node.dna_node_parent
            node._dna_node_parent = None

        # Do we have a previous node?
        if prev_n is not None:
            prev_n._dna_node_next_sib = next_n

        # Do we have a next node?
        if next_n is not None:
            next_n._dna_node_prev_sib = prev_n
