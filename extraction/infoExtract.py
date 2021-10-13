from LAC import LAC
import re
from entity.person import Person
class InfoExtract:
    def __init__(self):
        self.lac = LAC(mode='lac')
    
    def EToC(self,s):
        en = [",",";",":","(",")"]
        ch = ["，","；","：","（","）"]
        for i in range(0,len(en)):
            s = s.replace(en[i],ch[i])
        return s
    
    def cutDate(self,matched):
        s = matched.group()
        return s[:4] + "." + s[4:]

    def dealPeriod(self,matched): 
        s = matched.group()
        punc = ["、","，","。","；","：","（"]
        if s[0] not in punc and re.sub("\d","",s[0]) != "":
            s = s[0] + "，" + s[1:]
        if s[-1] not in punc:
            if s[-1] != "至":
                s = s[:-1] +"：" + s[-1]
        else:
            if s[-1] == "，" or s[-1] == "、":
                s = s[:-1] + "："
        return s.replace("--","-").replace("—","-").replace("－","-")

    def dealBorndate(self,matched):
        s = matched.group()
        return s[5:]+"生"

    def dealDate(self,matched):
        s = matched.group()
        if s[-1] in ["、","，"]:
            s = s[:-1]
        return s

    def zhiJin(self,matched):
        s = matched.group()
        if s[-1] == "，" or s[-1] == "、":
            s = s[:-1] + "："
        else:
            s = s[:-1] + "：" + s[-1]
        return s

    def party(self,s: str):
        res = ""
        parties = ["中共","中共党员","中国共产党","致公党","农工党","中国农工民主党","九三学社","民进","民进会员","中国民主促进会","民建会员","中国民主建国会","中国国民党革命委员会","民革","台盟","民盟","台湾民主自治同盟"]
        endWords = ['共','党','员','社','进','会','革','盟']
        if s[-1] in endWords:
            for part in parties:
                if part in s:
                    res = part
                    if res == "中共":
                        res = "中共党员"
                    break
        return res

    def addParty(self,oriparty,newparty):
        if newparty not in oriparty:
            oriparty += newparty + '、'
        return oriparty

    def getInf(self, s: str):
        s = "".join(s.split())
        s = s.strip('。') + '。'
        s = s.replace("+","")
        s = self.EToC(s)
        s = s.replace("；（","（")
        s = re.sub("\d\d\d\d\d\d",self.cutDate,s)
        s = re.sub(".?\d\d\d\d.\d{1,2}(-|—|－){1,2}(\d\d\d\d.\d{1,2})?.",self.dealPeriod,s)
        s = re.sub("出生年月.\d\d\d\d年\d{1,2}月",self.dealBorndate,s)
        s = re.sub("\d\d\d\d年\d{1,2}月.",self.dealDate,s)
        s = re.sub("-至今.",self.zhiJin,s)
        s = re.sub("主要工作.历.","",s)
        s = re.sub("(工作)?简历.","",s)
        edus = ["究生","本科","硕士","博士","学士","学生","学习","学历","连读","读书","毕业","文化","专业"]
        parties = ["党派","党员","会员"]
        person = Person()
        lacResult = self.lac.run(s)  # 通过模型进行NER
        lengthOfSegs = len(lacResult[0])  
        state = 0
        wordBuf = ""

        #状态0: 初始状态或识别人名、性别、民族、政治面貌
        #状态1: 识别经历、出生日期、政治面貌、籍贯

        j = 0
        while j < lengthOfSegs:
            word = lacResult[0][j]
            partOfSpeech = lacResult[1][j]
            if len(partOfSpeech) == 0:
                j += 1
                continue  
            wordBuf += word

            #状态0: 初始状态或识别人名、性别、民族、政治面貌、籍贯
            if state == 0:
                if partOfSpeech == "PER":
                    person.name += word
                    wordBuf = ""
                elif partOfSpeech[0] == "a":
                    if word in ['男','女']:
                        person.sex += wordBuf
                        wordBuf = ""
                    else:
                        state = 1
                elif partOfSpeech[0] == "n":
                    if "族" in word:
                        person.nation += wordBuf
                        wordBuf = ""
                    elif "党员" in word:
                        person.polStatus = self.addParty(person.polStatus,wordBuf)
                        wordBuf = ""
                    elif word[-1] == "人":
                        person.nativePlace += wordBuf[:-1]
                        wordBuf = ""
                    else:
                        state = 1
                elif partOfSpeech == "w":
                    if j>=1 and lacResult[1][j-1] == "LOC":
                        person.nativePlace += wordBuf[:-1]
                    wordBuf = ""
                    state = 0
                elif partOfSpeech == "LOC" or partOfSpeech == "f":
                    if len(word) == 3 and word[-1] == "人":
                        person.nativePlace += wordBuf[:-1]
                        wordBuf = ""
                    state = 0
                else:
                    state = 1

            #状态1: 识别经历、出生日期、政治面貌、(未识别出的)姓名、籍贯
            elif state == 1:
                if partOfSpeech == "w":
                    empty = ""
                    if len(word) > 1:
                        if word[0] == "-":
                            continue
                        empty = word[1:]
                        wordBuf = wordBuf.replace(empty,"")
                        word = word[0]
                    if word in ["。","，","、","；"]:
                        newBuf = wordBuf[:-1]
                        if "参加工作" in wordBuf:
                            person.employment += wordBuf
                        elif "加入" in wordBuf:
                            person.polStatus = self.addParty(person.polStatus,self.party(newBuf))
                        elif newBuf[-2:] in parties:
                            person.polStatus = self.addParty(person.polStatus,newBuf)
                        elif newBuf[-2:] in edus:
                            if "（" in wordBuf and "）" not in wordBuf:
                                beg = newBuf.rfind("（")
                            else:
                                beg = newBuf.rfind("，")
                            person.eduBg += wordBuf[beg+1:].replace("其间：","")
                            person.employment += wordBuf[:beg+1].strip("（")
                        elif newBuf[-1] == "）" and newBuf[-3:-1] in edus: 
                            beg = newBuf.rfind("（")
                            if beg != -1 and wordBuf[beg-2:beg] in edus:
                                person.eduBg += wordBuf
                            else:
                                person.eduBg += newBuf[beg+1:-1].replace("其间：","").replace("其间","") + word
                                person.employment += wordBuf[:beg+1].strip("（") + word
                        elif word in ["。","；"]:
                            if "毕业待分配" in wordBuf or "学位办" in wordBuf:
                                person.employment += wordBuf
                            elif "毕业" in wordBuf or "学历" in wordBuf or "学位" in wordBuf:
                                person.eduBg += wordBuf
                            else:
                                person.employment += wordBuf
                        else:
                            if len(newBuf) <= 3:
                                person.name += newBuf
                            else:
                                j += 1
                                continue
                        wordBuf = empty
                        state = 0
                elif partOfSpeech == "v":
                    if word == "生" or word == "出生":
                        person.bornDate += wordBuf.replace(word,"")
                        wordBuf = ""
                        state = 0
                    elif "入党" in word:
                        person.polStatus = self.addParty(person.polStatus,"中共党员")
                        wordBuf = ""
                        state = 0
                elif word == "人":
                    person.nativePlace += wordBuf[:-1]
                    wordBuf = ""
                    state = 0
            j += 1
        if person.eduBg != "":
            person.eduBg = person.eduBg.strip("，").strip("。").strip("、").strip("；") + "。"
        person.polStatus = person.polStatus.strip("、")
        return person



    def getEdubg(self,s):
        res = ''
        edubg = ["博士研究生","博士","硕士研究生","硕士","研究生","本科","学士","大专","中专"]
        for word in edubg:
            if word in s:
                res = word
                break
        if res == "":
            if s[-4:-2] == "大学":
                res = "本科"
            elif s[-4:-2] == "专科":
                res = "专科"
        return res

    def getHigherEdu(self,oriEdu,newEdu):
        standards = ["博士研究生","硕士研究生","研究生","本科","专科","中专",""]
        newStandard = ''
        if "博士" in newEdu:
            newStandard = standards[0]
        elif "硕士" in newEdu:
            newStandard = standards[1]
        elif "研究生" in newEdu:
            newStandard = standards[2]
        elif "本科" in newEdu or "学士" in newEdu:
            newStandard = standards[3]
        elif "专科" in newEdu or "大专" in newEdu:
            newStandard = standards[4]
        elif "中专" in newEdu:
            newStandard = standards[5]
        else:
            newStandard = standards[6]

        # 比较得到更高级学历    
        res = oriEdu
        if oriEdu == "":
            res = newStandard
        else:
            index1 = standards.index(oriEdu)
            index2 = standards.index(newStandard)
            if index1 > index2:
                res = newStandard
        return res

    def getStudyTriples(self,s):
        res = []
        s = s.strip('。').replace('。','，').replace('；',"，").replace("、","，")
        s = s.split('，')
        keywords = ["学习","学生","毕业"]
        for item in s:
            period = ''
            organization = ''
            position = ''
            merge = True
            if "-" in item:
                item = item.split("：")
                period = item[0]
                item = item[1]
            if "（" in item:
                beg = item.find("（")
                end = item.rfind("）")
                organization = item[beg+1:end]
                merge = False
                item = item.replace("（"+organization+"）","")
            if item[-2:] == "学历" or item[:2] == "学历":
                position = self.getEdubg(item)
            elif item[-2:] in keywords:
                position = self.getEdubg(item)
                if position != "":
                    item = re.sub(position,"",item,count=1,flags=0)
                item = item[:-2]
                if len(item) >= 2:
                    if item[-2:] == "在职":
                        position = "在职" + position
                    elif (item[-2:] == "大学") or (len(item)>=4 and item[-4:]=="专业大学"):
                        item = item[:-2]
                    if organization == "" and len(item) > 0:
                        organization = item
                        merge = False
            else:
                position = item
            if merge and len(res) > 0 and res[-1][1] != "":
                if res[-1][2] == "":
                    res[-1][2] += position
                else:
                    res[-1][2] += '、' + position
            else:
                res.append([period,organization,position])
            
            # 得到最高学历
            result = []
            highest = ''
            for item in res:
                highest = self.getHigherEdu(highest,item[2])
                if item[0] != "" or item[1] != "":
                    result.append(item)
        return highest,result

    def divideJob(self,s,orgEnds):
        organization = ''
        position = ''
        i = 0
        while i < len(orgEnds):
            endword = orgEnds[i]
            i += 1
            index = s.find(endword)
            if index >=2  and index <= len(s)-3:
                if endword in ["省","市","区"] and s[index+1] == "委":
                    index += 1
                    if s[index+1] == "办":
                        index += 1
                elif s[index+1] == "长" or s[index+1] == "级":
                    continue
                elif endword == "委":
                    if s[index:index+3] == "委员会":
                        index += 2
                    elif s[index:index+2] == "委会":
                        index += 1
                elif endword == "会" and s[index+1] == "议":
                    continue
                elif endword == "办" and s[index:index+3] == "办事员":
                    continue
                organization += s[:index+1] + ' '
                if index < len(s)-1:
                    s = s[index+1:]
                    if s[0] == "和":
                        organization += '\t'
                        s = s[1:]
                        i = 0
                else:
                    s = ''
                    break
        position = s
        return organization.strip(),position

    def getJob(self,s,oriState=0,period=''):
        res = []
        punc = ["，","；","。"]
        orgEnds = ["国","厅","省","市","区","园","镇","村","局","协","站","所","道","处","委","会","部","室","心","办","府","科","队"] # 尽量按照优先级从高到底排序
        state = oriState
        organization = ''
        position = ''
        wordBuf = ''
        #状态0: 识别时间
        #状态1: 识别组织名、职位名
        for c in s:
            if state == 0:
                if re.sub("\d","",c) == "" or c in ["-","：",".","至","今"]:
                    if c == "：":
                        period = wordBuf
                        wordBuf = ''
                        state = 1
                    else:
                        wordBuf += c
                else:
                    wordBuf += c
                    state = 1
            elif state == 1:
                if re.sub("\d","",c) == "" or c in punc:
                    if len(wordBuf) > 0 and wordBuf.count("（") != wordBuf.count("）"):
                        wordBuf = wordBuf[:-1]
                    wordBuf = wordBuf.strip("（").strip("、")
                    bufs = wordBuf.split("、")
                    organization,position = self.divideJob(bufs[0],orgEnds)
                    if len(bufs) > 1:
                        for buf in bufs[1:]:
                            org,pos = self.divideJob(buf,orgEnds)
                            # print(org,pos)
                            if org == "":
                                position += '、' + pos
                            elif pos == "":
                                organization += '\t' + org
                            else:
                                if position == "":
                                    organization += '\t' + org
                                    position = pos
                                else:
                                    if position == "" or position[-2:] == "工作":
                                        position += "人员"
                                    res.append([period,organization,position])
                                    position = pos
                                    if " " in org or organization == "":
                                        organization = org  
                                    elif orgEnds.index(organization[-1]) < orgEnds.index(org[-1]):
                                        organization += ' ' + org
                                    elif orgEnds.index(organization[-1]) == orgEnds.index(org[-1]):
                                        if org not in organization:
                                            delLength = len(organization.split(' ')[-1])
                                            organization = organization[:-delLength] + org
                                    else:
                                        groups = organization.split(' ')
                                        i = len(groups)-2
                                        while i >= 0:
                                            group = groups[i]
                                            if orgEnds.index(group[-1]) <= orgEnds.index(org[-1]):
                                                if orgEnds.index(group[-1]) == orgEnds.index(org[-1]):
                                                    index = organization.find(group)
                                                    if org in group:
                                                        organization = organization[:index+len(group)]
                                                    else:
                                                        organization = organization[:index] + org
                                                else:
                                                    index = organization.find(group)
                                                    organization = organization[:index+len(group)+1] + org
                                                break
                                            i -= 1
                                        if i == -1:
                                            organization = org
                    if organization == "" and len(res) > 0:
                        res[-1][2] += '、' + position
                    else:
                        orgs = organization.split("\t")
                        for one in orgs:
                            if position == "" or position == "工作" or position == "挂职":
                                position += "人员"
                            res.append([period,one,position])           
                    organization = ''
                    position = ''
                    if c in punc:
                        wordBuf = ''
                        state = oriState
                    else:
                        wordBuf = c
                        state = 0
                else:
                    wordBuf += c
        return res

    def getJobTriples(self,s):
        res = []
        s = s.replace("（其间：","；").replace("（兼）","").replace("兼任","、").replace("兼","、").replace("借调","")
        punc = ["，","；","。"]
        if "-" in s:
            beg = s.find("-")
            while beg > 0:
                beg -= 1
                if s[beg] in punc:
                    break
            if beg:
                s = s[beg+1:]
            res.extend(self.getJob(s))
        elif "曾任" in s:
            now = s.find("现任")
            last = s.find("曾任")
            nowJob = ''
            lastJob = ''
            if now < last:
                nowJob = s[now+2:last-1] + '。'
                lastJob = s[last+2:]
            else:
                nowJob = s[now+2:]
                lastJob = s[last+2:now-1] + '。'
            res.extend(self.getJob(lastJob,1,"曾经"))
            res.extend(self.getJob(nowJob,1,"现在"))
        else:
            print("!!!",s)
        return res


#程序测试代码
# inf = InfoExtract()
# with open("test.txt",'r',encoding='utf-8') as fs:
#     line = fs.readline()
# res = inf.getJobTriples(line)
# print('工作经历(格式化)：')
# for item in res:
#     print(f'\t{item[0]}\t{item[1]}\t{item[2]}')

# text = '宜兴市太华镇党委宣统委员兼党政办公室主任'
# print(inf.divideJob(text))
