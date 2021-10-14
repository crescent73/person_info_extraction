from typing import List
from py2neo import Graph, Node, Relationship, NodeMatcher
from entity.person import Person


def has_person(person:Person):
    """ 判断知识图谱里是否有已经有这个人 """
    # 根据名字查找
    return False

def has_goverment(goverment):
    """ 判断知识图谱里是否有已经有这个人 """
    # 根据名字查找
    return False

def has_relation():
    """ 判断就职经历 """
    return False

def add_person(graph:Graph,person):
    """ 将识别出来的person信息插入到neo4j中 """
    # 添加人物节点
    p = Node('Person',name=person.name,gender=person.sex,nation=person.nation,\
            nativePlace=person.nativePlace,bornDate=person.bornDate,\
            politicsStatus=person.polStatus,educationBg=person.eduBg)
    if not has_person(person): # 判断人物节点是否存在，是否需要修改
        graph.create(p)
    # 添加人物关系节点
    for job in person.job:
        # ['2003.07-2006.11', '市政府办公室 经济科', '秘书']
        government = Node("Government",name = job[1]) # 有一个问题，政府名称？
        if not has_goverment(job[1]):# 创建政府的时候，首先需要判断政府是否存在，如果不存在，需要插入政府实体，并添加上下级关系
            graph.create(government) 
        times = job[0].split("-")
        # print(times)
        relation = Relationship(p,"TAKE_OFFICE",government,startTime=times[0],endTime=times[1],name=job[2])
        if not has_relation(): # 判断关系，是否需要更新、修改
            graph.create(relation)

