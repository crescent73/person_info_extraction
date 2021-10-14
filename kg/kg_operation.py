from py2neo import Graph, Node, Relationship, NodeMatcher
import math
from kg_base import *

class KG:
    """ neo4j封装类 """

    def __init__(self,url,user,password):
        self.graph = KG(url,user,password)

    def addPerson(self, tripleList, persons):
        """ 输入三元组关系，将三元组关系存入知识图谱
        tripleList List(tuple)待存入的三元组列表
        :persons Class 任务基本信息
        """
        nodeDict = {}
        for item in tripleList:
            # 创建节点
            node1 = Node()
            node2 = Node()
            if item[0] not in nodeDict.keys():
                if isinstance(item[0],int): # 添加任务节点
                    person = persons[item[0]]
                    node1 = Node('人物',id=person.id,name=person.name,sex=person.sex,nation=person.nation,eduBg=person.eduBg,bornDate=person.bornDate,polStatus=person.polStatus)
                else: # 添加组织机构节点
                    node1 = Node('组织机构',name=item[0])
                nodeDict[item[0]] = node1
            else:
                node1 = nodeDict[item[0]]
            if item[2] not in nodeDict.keys(): # 添加组织机构节点
                node2 = Node('组织机构',name=item[2])
                nodeDict[item[2]] = node2
            else:
                node2 = nodeDict[item[2]]
            self.graph.create(node1) # node1 任务节点
            self.graph.create(node2) # node2 组织结构节点

            # 创建关系 
            relation = Relationship(node1)
            if item[1] == '就职':
                person = persons[item[0]]
                position = ''
                onepost = ''
                for job in person.oldJob:
                    if job[0] != '':
                        temp = job[0].split(' ')
                        if temp[-1] == item[2] and job[1] != '':
                            onepost += job[1] + '、'
                if onepost != '':
                    position += '曾经 ' + onepost.strip('、') + '\n'

                onepost = ''
                for job in person.newJob:
                    if job[0] != '':
                        temp = job[0].split(' ')
                        if temp[-1] == item[2] and job[1] != '':
                            onepost += job[1] + '、'
                if onepost != '':
                    position += '现在 ' + onepost.strip('、') + '\n'
                relation = Relationship(node1,item[1],node2,position=position.strip('\n')) # 添加就职关系(人物，关系名，职位，属性)
            else:
                relation = Relationship(node1,item[1],node2) # 添加就职关系（人物，关系名，职位）
            self.graph.create(relation)

    def calcPeriod(self,pos,arg1=5,arg2=20): # 参数1代表现就职的推测时长、参数2代表曾就职的推测时长
        """ 格式化就职时间 """
        res = list()
        now = 2021
        if pos == '':
            pos = '现在'
        periods = pos.split('\n')
        for period in periods:
            period = period.split(' ')[0]
            if period == '曾经':
                res.append([now-arg1-arg2,now-arg1,'past'])
            elif period == '现在':
                res.append([now-arg1,now,'now'])
            else:
                period = period.split('-')
                temp1 = period[0].split('.')
                temp2 = period[1].split('.')
                date1 = int(temp1[0])
                date2 = int(temp2[0])
                if len(temp1) > 1:
                    date1 += int(temp1[1])/12
                if len(temp2) > 1:
                    date2 += int(temp2[1])/12
                res.append([date1,date2,'standard'])
        return res

    def calcCross(self,period1,period2,arg1=4): # 参数1是曾就职时长/现就职时长的结果，代表更确切的曾就职时长
        """ 计算就职时长 """
        crossTime = 0
        for per1 in period1:
            for per2 in period2:
                startt = max(per1[0],per2[0])
                endt = min(per1[1],per2[1])
                timeLen = max(endt-startt,0)
                if per1[2] == 'past' or per2[2] == 'past':
                    timeLen /= arg1
                crossTime += timeLen
        return crossTime

    def calcScore(self,id1,id2,arg1=2,arg2=5,arg3=1): # 参数1、2代表计算式中的常数基数、参数3控制得分等比例变化
        hassRela = False
        # queryStr = "MATCH p = (:人物 {id:" + str(id1) + "})-[*]-(:人物 {id:" + str(id2) + "}) RETURN p" # 多属性逗号隔开
        queryStr = f"Match p = (a)-[*]->(b) where id(a) = {id1} and id(b) = {id2} return p"
        paths = self.graph.run(queryStr).data()
        score = 0
        if len(paths) > 0:
            hassRela = True

        # 遍历所有路径
        for path in paths:
            # 跳过带环的路径
            nodes = path['p'].nodes
            relations = path['p'].relationships
            nodeSet = set(nodes)
            if len(nodeSet) < len(relations) + 1:
                continue
            # 计算该路径得分
            print('*',path['p'],end=' ')
            n = len(nodes)
            minScore = 100
            midNodes = 0
            i1 = 0
            i2 = 1
            while i2 < n:
                if str(nodes[i2].labels) == ':人物':
                    midNodes += 1
                    pathLen = i2 - i1
                    rela1 = self.graph.match_one({nodes[i1],nodes[i1+1]})
                    rela2 = self.graph.match_one({nodes[i2],nodes[i2-1]})
                    pos1 = dict(rela1)['position']
                    pos2 = dict(rela2)['position']
                    period1 = self.calcPeriod(pos1)
                    period2 = self.calcPeriod(pos2)
                    crossTime = self.calcCross(period1,period2)
                    directScore = crossTime/math.log(pathLen,arg1)
                    minScore = min(minScore,directScore)
                    i1 = i2
                i2 += 1
            midNodes -= 1
            scorei = minScore/arg2**midNodes
            print(scorei)
            score += scorei
        print('SCORE:',score*arg3)
        return hassRela

    def calcIntimacy(self,p1,p2):
        res = False
        if isinstance(p1,int):
            res = self.calcScore(p1,p2)
            print('是否存在路径:',res)
        else:
            nodes1 = self.findNode('人物',p1)
            nodes2 = self.findNode('人物',p2)
            if len(nodes1) == 0:
                print(p1+'节点不存在!')
                return 
            if len(nodes2) == 0:
                print(p2+'节点不存在!')    
                return  
            for node1 in nodes1:
                id1 = node1.identity    
                for node2 in nodes2:
                    id2 = node2.identity
                    res = self.calcScore(id1,id2)
                    print('是否存在路径:',res)

    def findNode(self,label,name):
        """ 根据标签和name属性查找节点
        Cypher： MATCH (x:label {name:name}) return x """
        matcher = NodeMatcher(self.graph)
        res = list(matcher.match(label,name=name))
        return res # 找到返回节点列表，找不到返回空列表

    def findRela(self,node1,node2,rtype=''):
        """ 查找关系，没传rtype默认查找所有关系
        Cypher: MATCH p=()-[r:rtype]->() RETURN p  """
        res = self.graph.match({node1,node2})
        if rtype == '就职':
            res = self.graph.match({node1,node2},rtype)
        return res.first() # 找到返回关系，找不到返回None

    def delNode(self,node):
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
        kg.graph.delete(node)

    def updateNode(self,node,prop):
        """ 修改节点 """
        node.update(prop)
        self.graph.push(node)

    def updateRela(self,rela,prop):
        """ 修改关系 """
        rela.update(prop)
        self.graph.push(rela)

    def judgeSame(self,old,new,isNode=True):
        """ 判断两个节点是否相同 """
        situation = 2 # 情况0代表需创建一个新的节点/关系、情况1代表需修改已存在的同名节点/关系、情况2代表信息重合且不用改动图谱
        data = dict() # 保存修改信息
        prop1 = dict(old)
        prop2 = dict(new)
        if not isNode:
            data = list() 
        for key in prop1.keys():
            if prop1[key] != prop2[key] and prop2[key] != '': # 如果两个节点的属性不相同
                if prop1[key] != '':
                    if isNode:
                        situation = 0 # 则认为是一个新节点
                    else:
                        periods1 = prop1[key].split('\n')
                        periods2 = prop2[key].split('\n')
                        for period2 in periods2:
                            time2 = period2.split(' ')[0]
                            appeared = False 
                            for period1 in periods1:
                                time1 = period1.split(' ')[0]
                                if time1 == time2:
                                    appeared = True
                                    break
                            if not appeared:
                                situation = 1 # 如果就职经历相同，则修改节点
                                data.append(period2)
                    break
                else:
                    if isNode:
                        data[key] = prop2[key]
                    else:
                        data.append(prop2[key])
                    situation = 1
        return situation,data
        
    def addNode(self,label,prop):
        """ 添加节点，需要判断节点是否已存在，如果已存在则更新节点，如果没有存在则插入节点。 """
        newNode =  Node()
        oldNode = Node()
        situation = 0 # 情况0代表需创建一个新的节点、情况1代表需修改已存在的同名节点、情况2代表信息重合且不用改动图谱
        data = dict() # 保存修改信息
        if label == '人物':
            newNode = Node(label,name=prop['name'],sex=prop['sex'],nation=prop['nation'],eduBg=prop['eduBg'],bornDate=prop['bornDate'],polStatus=prop['polStatus'])
            res = self.findNode(label,prop['name']) # 先查找节点
            for node in res:
                situation,data = self.judgeSame(node,newNode) # 然后判断节点间关系，确定是否更新修改
                if situation != 0:
                    oldNode = node
                    break
        elif label == '组织机构':
            newNode = Node(label,name=prop['name'])
            res = self.findNode(label,prop['name'])
            if len(res) != 0:
                situation = 2 # 如果得到这个节点，则说明节点已存在

        if situation == 0: # 如果节点不存在，则创建节点
            self.graph.create(newNode)
        elif situation == 1: # 如果节点存在但需要修改，则修改节点
            self.updateNode(oldNode,data)
        return situation
            
    def addRela(self,node1,node2,rtype,prop={}):
        """ 添加关系，需要判断关系是否存在，如果不存在添加新的关系 """
        newRela = Relationship(node1)
        oldRela = Relationship(node1)
        situation = 0 # 情况0代表需创建一个新的关系、情况1代表需修改已存在的关系、情况2代表信息重合且不用改动图谱
        data = list() # 保存修改信息
        if rtype == '就职':
            newRela = Relationship(node1,rtype,node2,position=prop['position'])
            oldRela = self.findRela(node1,node2,rtype)
            if oldRela != None:
                situation,data = self.judgeSame(oldRela,newRela,False)
        elif rtype == '下设':
            newRela = Relationship(node1,rtype,node2)
            oldRela = self.findRela(node1,node2,rtype)
            if oldRela != None:
                situation = 2
        elif rtype == '认识':
            newRela = Relationship(node1,rtype,node2)
            
        if situation == 0:
            self.graph.create(newRela)
            self.updateRela(newRela,prop)
        elif situation == 1:
            newData = dict(oldRela)
            for item in data:
                if newData['position'] == '':
                    newData['position'] += item
                else:
                    newData['position'] += '\n' + item
            self.updateRela(oldRela,newData)
        return situation

    def addPersonRela(self,node1,node2,source,prop={}):
        sourceList = ['开源数据','人工添加']
        success = True
        rela = self.findRela(node1,node2,'认识')
        if rela == None:
            prop['source'] = source
            self.addRela(node1,node2,'认识',prop)
        else:
            oldSource = rela['source']
            if sourceList.index(source) > sourceList.index(oldSource):
                success = False
            else:
                self.delRela(rela)
                prop['source'] = source
                self.addRela(node1,node2,'认识',prop)
        return success
     

if __name__ == '__main__':
    url = "http://localhost:7474"
    user = "neo4j"
    password = "123456"
    kg = KG(url,user,password)

    # 0 删除多余属性
    # for id in kg.graph.nodes:
    #     kg.delProperty(kg.graph.nodes[id],'id') 

    # 1 计算两人物节点的亲密度得分
    # kg.calcIntimacy(44,116)

    # 2 测试知识图谱的增删改查接口
    # person = {'name':'王五','sex':'女','nation':'','eduBg':'','bornDate':'0000年','polStatus':''}
    # org = {'name':'大大洋集团'}
    # position = {'position':'2000.1-2021.2 总经理\n现在 大傻子'}
    # pos = {'position':''}
    # data = {'intimacy':9}
    # print(kg.addPersonRela(kg.graph.nodes[4],kg.graph.nodes[5],'人工添加',data))

# 可能用到的语句
# res = kg.graph.run("MATCH (n:Person {id:'a'})-[b:就职|学习*]-(c:Person {id:'c'}) RETURN n,b,c")
# print(kg.graph.nodes[80].identity)
# print(kg.addPersonRela(kg.graph.nodes[4],kg.graph.nodes[5],'人工添加',data))