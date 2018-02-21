from lxml import etree

import numpy as np
import igraph as ig

GRAPHML_NAMESPACE_URI = "http://graphml.graphdrawing.org/xmlns"

class GraphMLParser:
    
    def __init__(self):
        self._keys = {}
        
    
    def _convert(self, key, value):
        '''Helper function to convert data types'''
        
        if not key in self._keys:
            return None
        t = self._keys[key]['type'] 
        if t == 'boolean':
            return bool(value)
        elif t in ('int', 'long'):
            try:
                return int(value)
            except ValueError:
                return 0
        elif t in ('float', 'double'):
            try:
                return float(value)
            except ValueError:
                return 0.
        elif t == 'string':
            return str(value)
        
        
    def parse(self, fname):
        '''Parse GraphML from file'''
        
        doc = etree.parse(fname)
        root = doc.getroot()
        
        return self._parse(root)
        
        
    def fromstring(self, xml):
        '''Parse GraphML from string'''
        
        if isinstance(xml, str):
            xml = xml.encode()
            
        root = etree.fromstring(xml)
        
        return self._parse(root)
        
        
    def _parse(self, root):
        # Find 'key' objects that defines data types
        self._keys = {key.attrib['id']: {'for': key.attrib['for'],
                               'name': key.attrib['attr.name'],
                               'type': key.attrib['attr.type']}
                    for key in root.findall('key', namespaces=root.nsmap)}
                  

        # Find graph object
        g = root.find('graph', namespaces=root.nsmap)
                  
        # Create graph
        graph = ig.Graph()
        
        # Load graph attributes
        for data in g.findall('data', namespaces=root.nsmap):
            key = data.attrib['key']
            if key in self._keys and self._keys[key]['for'] == 'graph':
                name = self._keys[key]['name']
                graph[name] = self._convert(key, data.text)
        
        # Load vertices
        vertices = {}
        for id_, node in enumerate(g.findall('node', namespaces=root.nsmap)):
            graph.add_vertex(name=node.attrib['id'])
            for data in node.findall('data', namespaces=root.nsmap):
                key = data.attrib['key']
                if key in self._keys and self._keys[key]['for'] == 'node':
                    name = self._keys[key]['name']
                    value = self._convert(key, data.text)
                    if name == 'name':
                        vertices[node.attrib['id']] = int(value)
                    graph.vs[id_][name] = value
                    
        # Load edges
        for id_, edge in enumerate(g.findall('edge', namespaces=root.nsmap)):
            source = vertices.get(edge.attrib['source'], edge.attrib['source'])
            target = vertices.get(edge.attrib['target'], edge.attrib['target'])
            
            graph.add_edge(source, target)
            for data in edge.findall('data', namespaces=root.nsmap):
                key = data.attrib['key']
                if key in self._keys and self._keys[key]['for'] == 'edge':
                    name = self._keys[key]['name']
                    value = data.text
                    graph.es[id_][name] = self._convert(key, value)
                    
        return graph
    
    
class GraphMLWriter():

    def __init__(self):
        self._graph_keys = {}
        self._nodes_keys = {}
        self._edges_keys = {}
        

    def _get_type(self, val):
        '''Helper function to identify data types'''
        if isinstance(val, (float, int)) or (hasattr(val, 'dtype') and issubclass(val.dtype.type, (np.integer, np.floating))):
            return 'double'
        elif isinstance(val, bool):
            return 'boolean'
        elif isinstance(val, str):
            return 'string'
        else:
            return False
            
    
    def tostring(self, graph):
        '''Convert graph object to GraphML'''
        
        self._graph_keys = {}
        self._nodes_keys = {}
        self._edges_keys = {}
        
        # Root element
        xsi = "http://www.w3.org/2001/XMLSchema-instance"
        nsmap = {None: GRAPHML_NAMESPACE_URI, 'xsi': xsi}
        schema_location = GRAPHML_NAMESPACE_URI + " " + "http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd"
        root = etree.Element('graphml', attrib={"{{{}}}schemaLocation".format(xsi) : schema_location}, nsmap=nsmap)
        
        # Graph attributes
        for attr in graph.attributes():
            type_ = self._get_type(graph[attr])
            if not type_:
                continue
            
            key_attr = {'id': 'g_{}'.format(attr),
                        'for': 'graph',
                        'attr.name': attr,
                        'attr.type': type_}
            e = etree.Element('key', attrib=key_attr)
            self._graph_keys[key_attr['attr.name']] = key_attr
            root.append(e)
    
        # Vertices attributes
        for attr in graph.vs.attributes():
            type_ = self._get_type(graph.vs[0][attr])
            if not type_:
                continue
                
            key_attr = {'id': 'v_{}'.format(attr),
                        'for': 'node',
                        'attr.name': attr,
                        'attr.type': type_}
            e = etree.Element('key', attrib=key_attr)
            self._nodes_keys[key_attr['attr.name']] = key_attr
            root.append(e)
            
        # Edges attributes
        for attr in graph.es.attributes():
            type_ = self._get_type(graph.es[0][attr])
            if not type_:
                continue
                
            key_attr = {'id': 'e_{}'.format(attr),
                        'for': 'edge',
                        'attr.name': attr,
                        'attr.type': type_}
            e = etree.Element('key', attrib=key_attr)
            self._edges_keys[key_attr['attr.name']] = key_attr
            root.append(e)
            
        # Graph element
        directed = 'directed' if graph.is_directed() else 'undirected'
        g = etree.Element('graph', attrib={'id': 'G', 'edgedefault': directed})
        root.append(g)
        
        # Dumps graph attributes
        for attr in graph.attributes():
            if attr in self._graph_keys:
                data = etree.Element('data', attrib={'key': 'g_{}'.format(attr)})
                data.text = graph[attr]
                g.append(data)
            
        # Dumps vertices attributes
        for graph_node in graph.vs:
            node_id = graph_node['name'] if 'name' in graph_node.attributes() else 'n{}'.format(graph_node.index)
            if isinstance(node_id, float):
                node_id = int(node_id)
                
            node = etree.Element('node', attrib={'id': str(node_id)})
            g.append(node)
            
            for attr in graph_node.attributes():
                if attr in self._nodes_keys:
                    data = etree.Element('data', attrib={'key': 'v_{}'.format(attr)})
                    val = graph_node[attr]
                    if attr == 'name' and isinstance(val, float):
                        val = int(val)
                    data.text = str(val)
                    node.append(data)
                
        # Dumps edges attributes
        for graph_edge in graph.es:
            edge_source = graph.vs[graph_edge.source]['name'] if 'name' in graph.vs[graph_edge.source].attributes() else 'n{}'.format(graph_edge.source)
            if isinstance(edge_source, float):
                edge_source = int(edge_source)
                
            edge_target = graph.vs[graph_edge.target]['name'] if 'name' in graph.vs[graph_edge.target].attributes() else 'n{}'.format(graph_edge.target)
            if isinstance(edge_target, float):
                edge_target = int(edge_target)
                
            edge = etree.Element('edge', attrib={'source': str(edge_source),
                                                 'target': str(edge_target)})
            g.append(edge)
            
            for attr in graph_edge.attributes():
                if attr in self._edges_keys:
                    data = etree.Element('data', attrib={'key': 'e_{}'.format(attr)})
                    val = graph_edge[attr]
                    if attr == 'name' and isinstance(val, float):
                        val = int(val)
                    data.text = str(val)
                    edge.append(data)
        
        return etree.tostring(root, xml_declaration=True, encoding='utf-8', pretty_print=True)
        
        
if __name__ == '__main__':
    import tempfile
    
    graph = ig.Graph()
    
    graph.add_vertices(4)
    graph.add_edges([(0,0), (0, 1), (1, 2), (0, 3), (2, 3)])
    graph['foo'] = 'bar'
    graph.vs['id'] = range(4)
    graph.es['id'] = [str(x) for x in range(5)]
        
    writer = GraphMLWriter()
    gxl = writer.tostring(graph)
    
    parser = GraphMLParser()
    graph2 = parser.fromstring(gxl)
    
    assert(len(graph.vs) == len(graph2.vs))
    assert(len(graph.es) == len(graph2.es))
    assert(graph['foo'] == graph2['foo'] == 'bar')
    assert(graph.vs['id'] == graph2.vs['id'] == list(range(4)))
    assert(graph.es['id'] == graph2.es['id'] == [str(x) for x in range(5)])
    