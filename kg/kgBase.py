from py2neo import Graph, Node, Relationship, NodeMatcher
import math

def clearGraph(graph:Graph):
    """ 清除neo4j中原有的结点等所有信息 """
    graph.delete_all()

def findNode(graph:Graph,label,name):
    """ 根据标签和name属性查找节点
    Cypher： MATCH (x:label {name:name}) return x """
    matcher = NodeMatcher(graph)
    res = list(matcher.match(label,name=name))
    return res # 找到返回节点列表，找不到返回空列表

def findRela(graph:Graph,node1,node2,rtype=''):
    """ 查找关系，没传rtype默认查找所有关系
    Cypher: MATCH p=()-[r:rtype]->() RETURN p  """
    res = graph.match({node1,node2})
    if rtype == '就职':
        res = graph.match({node1,node2},rtype)
    return res.first() # 找到返回关系，找不到返回None

def delNode(graph:Graph,node):
    """ 删除节点，如果节点本身存在关系，会将其相连的关系也一起删除。传入的是node类型，一般先用match把节点查出来再delete 
    例：
    删除节点：
    nodes = NodeMatcher(graph).match('Person',name='Euler').first()
    graph.delete(nodes)
    删除关系：
    rel = RelationshipMatcher(graph).match([start_node, end_node], r_type="Knows").first()
    graph.delete(rel)
    """
    # ! 删除节点前必须先删除它的所有关系
    graph.delete(node)

def delRela(graph:Graph,rela):
    """ 删除子图中的关系，不会删除节点 """
    graph.separate(rela)

def delProperty(graph:Graph,item,name):
    """ 修改节点属性 """
    if item[name] != None:
        del item[name]
        graph.push(item)

def updateNode(graph:Graph,node,prop):
    """ 修改节点 """
    node.update(prop)
    graph.push(node)

def updateRela(graph:Graph,rela,prop):
    """ 修改关系 """
    rela.update(prop)
    graph.push(rela)
     

if __name__ == '__main__':
    url = "http://localhost:7474"
    user = "neo4j"
    password = "123456"
    kg = Graph(url,auth=(user,password))