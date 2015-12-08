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

    Functionality and terminology:

        "crawls" a DNA chain

        "emits" events when editing the chain
    """

    def __init__(self, dna):
        self.dna = dna
        self.__node = None
        self.__parent_node_stack = deque()

    # - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ -
    # traversing/reading
    # - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ -

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
                # We may simply need to jump back up to the parent to continue,
                # as in this case:
                #
                #    JUMP FROM 3. TO 1.
                #
                #          |----<---<---<---<---<-|
                #          \/                     |
                #    1. DNANode -- 2. DNANode     |
                #          |             |        |
                #          |       3. DNANode ->--|
                #    4. DNANode
                #          |
                #         ...
                #
                # ...or we may need to jump back up several parents, as in this
                # case:
                #
                #    JUMP FROM 5. TO 2., AND THEN FINALLY TO 1.
                #
                #          |----<---<----|
                #          |             |-----------|
                #          \/            \/          |
                #    1. DNANode -- 2. DNANode        |--<----<--|
                #          |             |                      |
                #          |       3. DNANode -- 4. DNANode     |
                #    6. DNANode                        |        |
                #          |                     5. DNANode ->--|
                #         ...
                #
                # The loop construct used below can handle any number of jumps
                # necessary to get back up the chain.
                cur_parent = stack.pop()
                while cur_parent.dna_node_next_sib is None and stack:
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

    def crawl_indents(self):
        """
        Same as crawl but returns a tuple.  The first item is the node and the
        second item is the indentation of the node relative to the previous
        node returned.
        """

        stack = self.__parent_node_stack
        node = self.__node
        indent = len(stack)
        while node is not None:
            yield node, len(stack) - indent
            indent = len(stack)
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

    def get_origin(self, node):
        """
        Starts at the given node and climbs backwards and up the chain as far
        as possible.
        """
        while True:
            if node.dna_node_prev_sib is not None:
                node = node.dna_node_prev_sib
            elif node.dna_node_parent is not None:
                node = node.dna_node_parent
            else:
                break

        return node

    # - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ -
    # editing "backend"
    # - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ -

    def __insert_before(self, node, ref_node=None):
        """
        Insert node before ref_node.  Use the current node if ref_node is not
        specified.
        """

        ref_node = self.__node if ref_node is None else ref_node
        if ref_node is None:
            raise DNACrawlerException(
                "Cannot insert, no node specified and current node is None.")

        if ref_node is self.dna.head:
            self.dna.head = node

        prev_n = ref_node._dna_node_prev_sib
        parent = ref_node._dna_node_parent

        # handle next/prev

        ref_node._dna_node_prev_sib = node
        node._dna_node_next_sib = ref_node

        if prev_n is not None:
            prev_n._dna_node_next_sib = node
            node._dna_node_prev_sib = prev_n

        # handle parent/child

        if parent is not None:
            ref_node._dna_node_parent = None
            node._dna_node_parent = parent
            parent._dna_node_child = node

        return ref_node

    def __insert_after(self, node, ref_node=None):
        """
        Insert node after ref_node.  User current node if ref_node is not
        specified.
        """

        ref_node = self.__node if ref_node is None else ref_node
        if ref_node is None:
            raise DNACrawlerException(
                "Cannot insert, no node specified and current node is None.")

        next_n = ref_node.dna_node_next_sib

        ref_node._dna_node_next_sib = node
        node._dna_node_prev_sib = ref_node

        if next_n is not None:
            next_n._dna_node_prev_sib = node
            node._dna_node_next_sib = next_n

        return ref_node

    def __insert_child(self, node, ref_node=None):
        """
        Insert node as child of ref_node.  Use current node if ref_node is not
        specified.
        """

        ref_node = self.__node if ref_node is None else ref_node
        if ref_node is None:
            raise DNACrawlerException(
                "Cannot insert, no node specified and current node is None.")

        # If the node we are inserting as a child is the DNA head, then we
        # need to update the head.
        if ref_node is self.dna.head:
            self.dna.head = self.get_origin(ref_node)

        child = ref_node._dna_node_child

        if child is None:
            # Easy, there is no child.
            ref_node._dna_node_child = node
            node._dna_node_parent = ref_node
        else:
            # There is already a child
            # TODO: this inserts node at the head of the list of children.
            # TODO: we probably want to insert it at the tail.
            self.__insert_before(node, child)

        return ref_node

    def __remove(self, node=None):
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

        # Update the DNA head if we are removing it.
        if node is self.dna.head:
            self.dna.head = next_n

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

    def __create_node(self, node):
        """
        Creates a new node if the given node is None.
        """
        if node is None:
            return self.dna.node_factory()

        return node

    # - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ -
    # editing "fronted"
    # - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ -

    # TODO: if someone accidentally uses add_* when they should use move_*,
    # that will be bad.  The node will still be connected to other parts of
    # the DNA chain.  Need to do something about it.  It's currently easy to
    # make the mistake.

    def add_before(self, node=None, ref_node=None):
        node = self.__create_node(node)
        ref_node = self.__insert_before(node, ref_node)
        self.emit(('c', '+', node, 'b', ref_node))

    def add_after(self, node=None, ref_node=None):
        node = self.__create_node(node)
        ref_node = self.__insert_after(node, ref_node)
        self.emit(('c', '+', node, 'a', ref_node))

    def add_child(self, node=None, ref_node=None):
        node = self.__create_node(node)
        ref_node = self.__insert_child(node, ref_node)
        self.emit(('c', '+', node, 'c', ref_node))

    def move_before(self, node, ref_node=None):
        self.__remove(node)
        ref_node = self.__insert_before(node, ref_node)
        self.emit(('c', '^', node, 'b', ref_node))

    def move_after(self, node, ref_node=None):
        self.__remove(node)
        ref_node = self.__insert_after(node, ref_node)
        self.emit(('c', '^', node, 'a', ref_node))

    def move_child(self, node, ref_node=None):
        self.__remove(node)
        ref_node = self.__insert_child(node, ref_node)
        self.emit(('c', '^', node, 'c', ref_node))

    def remove(self, node=None):
        self.__remove(node)
        self.emit(('c', '-', node))

    # - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ -
    # event emitting
    # - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ - ~ -

    def emit(self, event):
        print(event)
