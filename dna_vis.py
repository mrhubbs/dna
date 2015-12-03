"""
11-19-15

Uses Kivy to present an interactive visualization of the DNA chain structure.
"""


from kivy.app import runTouchApp
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.properties import ListProperty, NumericProperty
from kivy.lang import Builder

from dna_chain import DNANode
from dna import DNA


class NodeVis(Label):
    color = ListProperty([0, .6, .5])
    padding = NumericProperty('7dp')


Builder.load_string("""
<NodeVis>:
    canvas.before:
        Color:
            rgb: self.color
        Rectangle:
            pos: self.x + self.padding, self.y + self.padding
            size: self.width - self.padding * 2, self.height - self.padding * 2
        Color:
            rgb: 0, 0, 0
        Line:
            rectangle: self.x + self.padding, self.y + self.padding, \
                self.width - self.padding * 2, self.height - self.padding * 2
            width: 2.5
""")


class DNAVis(Widget):
    def __init__(self, **kw):
        super(DNAVis, self).__init__(**kw)
        self.dna = DNA()
        self.crawler = self.dna.spawn_crawler()

        self.bind(size=self.redraw, pos=self.redraw)

    def redraw(self, *ar):
        for w in self.children[:]:
            if isinstance(w, NodeVis):
                self.remove_widget(w)

        node_lookup = {}

        y = self.top - 100
        crawler = self.dna.spawn_crawler()
        crawler.reset()
        indent = 100

        for n, indent_no in crawler.crawl_indents():
            indent += 100 * indent_no

            nv = NodeVis(size=(100, 100), text=n.name)
            node_lookup[n] = nv
            nv.x = self.x + indent
            nv.y = y

            self.add_widget(nv)
            y -= 100

        crawler = self.crawler
        cv = NodeVis(
            size=(100, 100),
            text='CRAWLER',
            color=[.7, .05, 0])
        if crawler.current_node is not None:
            cv.x = node_lookup[crawler.current_node].x - 100
            cv.y = node_lookup[crawler.current_node].y
        else:
            cv.y = self.top - 100
            cv.x = self.width - cv.width
        self.add_widget(cv)

    def eval_input(self, text):
        dna = self.dna
        crawler = self.crawler

        if not hasattr(self, 'exec_locals'):
            self.exec_locals = locals()

        try:
            to_run = compile(text, '', 'exec')
            exec(to_run, globals(), self.exec_locals)
        except (NameError, SyntaxError, AttributeError) as err:
            print(err)

        self.redraw()


Builder.load_string("""
#:import Clock kivy.clock.Clock
<DNAVis>:
    canvas.before:
        Color:
            rgb: 1, .9, .8
        Rectangle:
            size: self.size
            pos: self.pos

    TextInput:
        id: input
        pos: root.pos
        size: root.width, '35dp'
        multiline: False
        on_text_validate:
            root.eval_input(self.text)
            self.text = ''
            Clock.schedule_once(lambda dt: setattr(self, 'focus', True), .1)
""")


if __name__ == '__main__':
    from kivy.clock import Clock

    dv = DNAVis()

    def the_deeds(*ar):
        n = DNANode()
        n.name = 'NODE 1'
        dv.dna.head = n
        c = dv.dna.spawn_crawler()

        n = DNANode()
        n.name = 'NODE 2'
        c.insert_child(n, dv.dna.head)

        dv.crawler.reset()
        dv.redraw()

    Clock.schedule_once(the_deeds, 1.0)

    runTouchApp(dv)
