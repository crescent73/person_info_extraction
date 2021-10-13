import os
import csv
from extraction.infoExtract import InfoExtract
from entity.person import Person

def infoExtra(inf,path,file,encode):
    with open(path + "/" + file,'r',encoding=encode) as f:
        reader = csv.reader(f)
        rows = [row for row in reader]
        # 找到“姓名”和“简历”两列位置
        nameLoc = rows[0].index('姓名')
        infoLoc = rows[0].index('简历')
        # 提取简历信息
        rows = rows[1:] 
        persons = list()
        for row in rows:
            person = Person()
            description = row[infoLoc]
            # 将描述文本中的信息进行提取
            person = inf.getInf(description)
            person.name = row[nameLoc].replace(" ","")  # 姓名一列单独赋值
            # person.saveInfo("result1.txt")  # 打印提取到的信息 
            persons.append(person)
        return persons

if __name__ == "__main__":
    inf = InfoExtract()
    path = "data"  # 在这里输入待提取的目录(目录下要求是.csv文件)
    allFiles = os.listdir(path)
    persons = list()
    print('==============================================================')

    # 1 结构化信息抽取
    for file in allFiles:
        try:
            persons.extend(infoExtra(inf,path,file,'utf-8'))
        except:
            persons.extend(infoExtra(inf,path,file,'gbk'))

    # 2 人物格式化学习、工作信息[period,company,position]三元组提取
    for i in range(len(persons)):
        persons[i].highestEdu,persons[i].study = inf.getStudyTriples(persons[i].eduBg)
        persons[i].job = inf.getJobTriples(persons[i].employment)
        persons[i].saveInfo("result/result2.txt")
        persons[i].saveAddInfo("result/result2.txt")
