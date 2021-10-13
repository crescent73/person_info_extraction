class Person:
    def __init__(self):
        self.name = ''        # 人名
        self.sex = ''         # 性别
        self.nation = ''      # 民族
        self.nativePlace = '' # 籍贯
        self.bornDate = ''    # 出生日期
        self.polStatus = ''   # 政治面貌
        self.eduBg = ''       # 学习经历
        self.employment = ''  # 就业经历
        self.highestEdu = ''  # 最高学历：中专、专科、本科、研究生(硕士研究生、博士研究生)等
        self.study = []       # 格式化学习信息: 元素形式为[period,organization,position]
        self.job = []         # 格式化工作信息: 元素形式为[period,organization,position]
        # period格式: xxxx.xx.xx-xxxx.xx.xx(年月日) 或 '曾经' 或 '现在'
        # organization格式: 机构全名
        # position格式: x、x

    def printInfo(self):
        print(f'人名：{self.name}')
        print(f'性别：{self.sex}')
        print(f'民族：{self.nation}')
        print(f'籍贯：{self.nativePlace}')
        print(f'出生日期：{self.bornDate}')
        print(f'政治面貌：{self.polStatus}')
        print(f'学习经历：{self.eduBg}')
        print(f'就业经历：{self.employment}')
        print('------------------------------')

    def saveInfo(self,name):
        with open(name,'a',encoding='utf-8') as fs:
            fs.write(f'人名：{self.name}\n')
            fs.write(f'性别：{self.sex}\n')
            fs.write(f'民族：{self.nation}\n')
            fs.write(f'籍贯：{self.nativePlace}\n')
            fs.write(f'出生日期：{self.bornDate}\n')
            fs.write(f'政治面貌：{self.polStatus}\n')
            fs.write(f'学习经历：{self.eduBg}\n')
            fs.write(f'就业经历：{self.employment}\n')
            fs.write('------------------------------\n')

    def printAddInfo(self):
        print(f'最高学历：{self.highestEdu}')  
        print('学习经历(格式化)：')
        for item in self.study:
            print(f'\t{item[0]}\t{item[1]}\t{item[2]}')
        print('工作经历(格式化)：')
        for item in self.job:
            print(f'\t{item[0]}\t{item[1]}\t{item[2]}')
        print('========================================================================')      

    def saveAddInfo(self,name):
        with open(name,'a',encoding='utf-8') as fs:
            fs.write(f'最高学历：{self.highestEdu}\n')
            fs.write('学习经历(格式化)：\n')
            for item in self.study:
                fs.write(f'\t{item[0]}\t{item[1]}\t{item[2]}\n')
            fs.write(f'工作经历(格式化)：\n')
            for item in self.job:
                fs.write(f'\t{item[0]}\t{item[1]}\t{item[2]}\n')
            fs.write('========================================================================\n')