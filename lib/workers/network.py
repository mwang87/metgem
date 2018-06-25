import numpy as np
import igraph as ig

from fa2 import ForceAtlas2
from .base import BaseWorker
from ..config import RADIUS


class NetworkWorker(BaseWorker):
    
    def __init__(self, graph):
        super().__init__()
        self.graph = graph
        self.radius = RADIUS
        self.max = self.graph.vcount()
        self.iterative_update = False
        self.desc = 'Computing layout: {value:d} vertices of {max:d}.'

    def run(self):
        radius = self.radius
        layout = np.zeros((self.max, 2))

        # TODO: Use list of radii in adjustSizes
        forceatlas2 = ForceAtlas2(adjustSizes=2*radius, scalingRatio=radius, verbose=False)

        clusters = sorted(self.graph.clusters(), key=len, reverse=True)
        dx, dy = 0, 0
        max_height = 0
        max_width = 0
        total_count = 0
        for i, ids in enumerate(clusters):
            if self.isStopped():
                self.canceled.emit()
                return False
                
            graph = self.graph.subgraph(ids)
            vcount = graph.vcount()
            
            if vcount == 1:
                l = ig.Layout([(0, 0)])
                border = 2*radius
            elif vcount == 2:
                l = ig.Layout([(0, -2*radius), (0, 2*radius)])
                border = 2*radius
            else:
                l = forceatlas2.forceatlas2_igraph_layout(graph, pos=None, iterations=1000, weight_attr='__weight')
                border = 5*radius
            
            bb = l.bounding_box(border=border)
            l.translate(dx-bb.left, dy-bb.top)
        
            for coord, index in zip(l, ids):
                layout[index] = coord
                
            if max_width == 0:
                max_width = bb.width*2
        
            dx += bb.width
            max_height = max(max_height, bb.height)
            if dx >= max_width:
                dx = 0
                dy += max_height
                max_height = 0

            total_count += vcount
            self.updated.emit(total_count)

        return layout
