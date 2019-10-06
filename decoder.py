# coding = utf-8
# TLV解码规则
import re
import textwrap

class BER_TLV:
    # 定义基本属性,tlvObj=[level:int, extend:int, number:int, tag:str, length:str, value:str]
    tlvObj = [1, 0, 0, 'tag', 'length', 'value']
    tlvList = []
    exTag =[]
    #长度检查参数,limt=[tag:str, number:int]
    chk = ['', 0]
    # 不同扩展级别下的Value字节数 numBytes={'level1':number1, 'level2':number2,……}
    numBytes = dict()

    def __init__(self, rawData:str, exTag:list=None):
        # 初始化类参数
        self.tlvObj = [1, 0, 0, 'tag', 'length', 'value']
        self.tlvList = []
        self.exTag = []
        self.chk = ['', 0]
        self.numBytes = dict()
        # 数据格式检查
        if rawData == None:
            print("The Raw Data cannot be empty! ")
            return
        if type(rawData) == int:
            print('This String is NOT HexString!')
            return
        else:
            hexStr = self.isHexString(rawData)
            print("Ready to decode the HexString.\nHexString:\n"+(textwrap.fill(rawData,100)))
        # 检查异常Tag参数
        if exTag != None or []:
            self.exTag = exTag
        # 初始化边界
        self.numBytes['0'] = len(hexStr)
        self.chk[1] = len(hexStr)
        self.decoding(hexStr)

    def decoding(self, hexStr:str):
        while len(hexStr):
            self.getTag(hexStr)
            self.getLength(hexStr)
            level = self.tlvObj[0]
            extend = self.tlvObj[1]
            numbers =self.tlvObj[2]
            if extend == 1:
                self.tlvObj[5] = ''
                self.numBytes[str(level)] = numbers
                self.chk = [self.tlvObj[3], numbers]
                self.tlvList.append(list(self.tlvObj))
                value = hexStr[:numbers]
                hexStr = hexStr[numbers:]
                self.tlvObj[0] += 1
                self.decoding(value)
            else:
                self.tlvObj[5] = ''.join(hexStr[:numbers])
                self.tlvList.append(list(self.tlvObj))
                hexStr = hexStr[numbers:]
                count = 0
                for tlv in self.tlvList:
                    if tlv[0] == level:
                        count += tlv[2]+len(''.join(tlv[3:5]))//2
                if self.numBytes[str(level-1)] == count:
                    self.tlvObj[0] -= 1
        return

    def isHexString(self, str):
        # 判断数据长度
        if len(str)%2 != 0:
            print('Length of HexString is Error！')
            return
        # 处理可能的数据前缀
        if str[0:2] in ('0x', '0X'):
            str = str[2:]
        # 检查16进制字符类型
        match = re.fullmatch(r'^[0-9a-fA-F]+$', str)
        if match == None:
            print('This String is NOT HexString!')
            return
        # 完成检查，返回HexString列表
        return re.findall(r'.{2}', str)

    def getTag(self, hexStr:str):
        tag = hexStr.pop(0)
        # 检查TLV数据类型：基本类型 or 嵌套类型，Mask=0010 0000(32)
        if (tag not in self.exTag) and (int(tag, 16) & 32 == 32):
            self.tlvObj[1] = 1
        else:
            self.tlvObj[1] = 0
        # 检查Tag类型：单字节 or 多字节，Mask1=0001 1111(31)，Mask2=1000 0000（128）
        if int(tag, 16) & 31 == 31:
            end = 1
            while end:
                subTag = hexStr.pop(0)
                tag = tag + subTag
                end = int(subTag, 16) & 128
        self.tlvObj[3] = tag
        return tag

    def getLength(self, hexStr:str):
        length = hexStr.pop(0)
        # 检查Length类型：单字节(0 <= int <= 127) or 多字节
        if length == '80':
            print("Length of Tag('%s') is Error!" % self.tlvObj[2])
        if int(length,16) in range(128):
            self.tlvObj[2] = int(length,16)
            self.tlvObj[4] = length
        else:
            numLen = int(length,16) - 128
            while numLen:
                length = length + hexStr.pop(0)
                if int(length[2:], 16) > self.chk[1]:
                    print("The Tag='%s' decoding Error!"% self.chk[0])
                    return
                numLen -= 1
            self.tlvObj[2] = int(length[2:], 16)
            self.tlvObj[4] = length
        return length

    def print(self):
        print('Result：')
        for tlvObj in self.tlvList:
            print('\t'*(tlvObj[0]-1)+tlvObj[3]+' '+tlvObj[4]+' '+tlvObj[5])
        return


if __name__ == "__main__":
    rawData = '618202466682013400018338bd97a524fb0b9504ff3850952b2e1bcae23e6b80acbfd46b5b4414ecd3ff71fa7419f19173362afadb28dac9e74195c5a9d615cbbdfa6781e1caf30f84be00000000c350000fa05d7869d0028f7081800003000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000e1bb29f660741a3cd2291524b6ebf9bd117d4809241fcb0a83efd86839f52bf2650a2fe39c2dd73f139495dd38cfc4a9f42deb8f7450ae945ec4af4ca2fb26f50000000000000000000000000000000030303431303030343034323032303838410A0000000000000000000142090000000000000500007181B25002303151053030303031520053103030343130303034303432303230383854070156817249641855033030315609503030313130313031570900000000000005000058090000000000000500008620EBB031FE64453404E084B9300AAE56D0D7D28B4352AAE1F1F60B270B65FE6D6F5940000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004F4000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000'
    #rawData = '6113710B5002303151053030303031530431323334410103'
    arry = BER_TLV(rawData, ['66'])
    arry.print()