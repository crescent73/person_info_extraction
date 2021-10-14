# coding=utf-8
# 字典嵌套牛逼,别人写的,这样每一层非常多的东西,搜索就快了,树高26.所以整体搜索一个不关多大的单词表,还是O(1).

'''
    Python 字典 setdefault() 函数和get() 方法类似, 如果键不存在于字典中，将会添加键并将值设为默认值。
    说清楚就是:如果这个键存在字典中,那么这句话就不起作用,否则就添加字典里面这个key的取值为后面的默认值.
    简化了字典计数的代码.并且这个函数的返回值是做完这些事情之后这个key的value值.
    dict.setdefault(key, default=None)
    Python 字典 get() 函数返回指定键的值，如果值不在字典中返回默认值。
    dict.get(key, default=None)
'''

from LAC import LAC


class DicTrie:
    root = {}
    END = '$'  # 加入这个是为了区分单词和前缀,如果这一层node里面没有/他就是前缀.不是我们要找的单词.
    lac = LAC(mode='rank')

    def insert(self, s):
        # 从根节点遍历单词,char by char,如果不存在则新增,最后加上一个单词结束标志
        node = self.root  # 从字典树的根节点开始
        for word in s:
            """
            利用嵌套来做,一个trie树的子树也是一个trie树.
            利用setdefault的返回值是value的特性,如果找到了key就进入value
            没找到,就建立一个空字典
            """
            node = node.setdefault(word, {})  # 若当前字符不存在于字典树，则应该将后缀建立为一颗新的字典树，加入到后续
        node[self.END] = None

    def delete(self, word):  # 字典中删除word
        node = self.root
        for c in word:
            if c not in node:
                print('字典中没有不用删')
                return False
            node = node[c]
        # 如果找到了就把'/'删了
        del node['$']
        # 后面还需要检索一遍,找一下是否有前缀的后面没有单词的.把前缀的最后一个字母也去掉.因为没单词了,前缀也没意义存在了.
        # 也就是说最后一个字母这个节点,只有'/',删完如果是空的就把这个节点也删了.
        while node == {}:
            if word == '':
                return
            tmp = word[-1]
            word = word[:-1]
            node = self.root
            for c in word:
                node = node[c]
            del node[tmp]

    def search(self, word):
        node = self.root
        for c in word:
            if c not in node:
                return False
            node = node[c]
        return self.END in node

    def associateSearch(self, pre):  # 搜索引擎里面的功能是你输入东西,不管是不是单词,他都输出以这个东西为前缀的单词.
        node = self.root
        for c in pre:
            if c not in node:
                return []  # 因为字典里面没有pre这个前缀
            node = node[c]  # 有这个前缀就继续走,这里有个问题就是需要记录走过的路径才行.

        def travel(node):  # 返回node节点和他子节点拼出的所有单词
            if node == None:
                return ['']
            a = []  # 现在node是/ef

            for i in node:
                tmp = node[i]
                tmp2 = travel(tmp)
                for j in tmp2:
                    a.append(i + j)
            return a

        output = travel(node)
        for i in range(len(output)):
            output[i] = (pre + output[i])[:-1]
        return output

    def retAllInstitute(self, s): # 将机构切分
        prevCount = 0
        allInstitute = []
        curInstitute = a.associateSearch(s)  # 获得在该前缀下所有的机构

        if len(curInstitute) == prevCount: # 如果之前没有这个机构，就插入这个机构
            self.insert(s)

        prefix = ""
        node = self.root
        for word in s: # 从头到尾扫描，如果碰到分支节点，表明是一个层级结构，提取出来，会漏掉最后一个组织
            prefix += word
            subTree = node[word]  # 检查子树宽度
            switches = subTree.keys()
            if len(switches) >= 2: # 检测到分支
                allInstitute.append(prefix)
            node = node[word]

        finalInstitute = []
        for word in allInstitute:
            rankResult = self.lac.run(word) # 词性标注，二次识别
            for properties in rankResult[1]:
                if properties[0] == "n" and len(properties) > 1:
                    finalInstitute.append(word)
                elif properties == "ORG": # ORG属性表示是机构
                    finalInstitute.append(word)

        finalInstitute.append(s)

        allInstitute = finalInstitute
        finalInstitute = []
        curPrefix = ""
        allPrefix = ""
        # 将机构切分
        for word in s:
            curPrefix += word
            allPrefix += word
            if allPrefix in allInstitute:
                finalInstitute.append(curPrefix)
                curPrefix = ""

        return finalInstitute


if __name__ == "__main__":
    a = DicTrie() # 每个字为一个节点，创建一个树形结构，存储各个组织的名字
    a.insert('中国科学院计算技术研究所')
    a.insert('中国科学院自动化研究所')
    a.insert('中国科学院空天信息研究院')
    a.insert('中国科学技术大学计算机学院')
    a.insert("中国科学技术大学信息与通信工程学院")
    a.insert("北京邮电大学信息与通信工程学院")
    a.insert("北京邮电大学计算机学院计算机科学与技术专业")
    a.insert("北京邮电大学计算机学院智能科学与技术专业")
    a.insert("中国科学技术大学信息与通信工程学院")
    a.insert("中国传媒大学")
    a.insert("中央广播电视台")
    a.insert("南京大学人工智能学院")

    print(a.retAllInstitute('北京邮电大学计算机学院计算机科学与技术专业2018211307班'))
