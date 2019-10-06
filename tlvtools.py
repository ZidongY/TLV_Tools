#coding = utf-8
#TLV工具箱主函数

import sys
import re
from PyQt5.QtWidgets import QApplication, QMainWindow
from mainUI import Ui_MainWindow
from decoder import BER_TLV

class TlvTools(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.btn_decoding.clicked.connect(self.decode)
        self.chb_extTag.stateChanged.connect(self.setExTag)
        self.btn_clsRaw.clicked.connect(self.te_rawData.clear)
        self.btn_clsStruct.clicked.connect(self.te_structData.clear)

    def decode(self):
        # 获取待解析TLV数据
        rawData = self.te_rawData.toPlainText()
        # 清空解析窗口数据
        self.te_structData.clear()
        # 检查待解析TLV数据格式
        statusCode = self.chkStr(rawData)
        if statusCode:
            self.te_structData.appendPlainText('解析停止！')
            return
        # 检查是否存在特殊Tag设置
        if self.chb_extTag.isChecked():
            extTag = self.le_extTag.text().split(' ')
            self.te_structData.appendPlainText('特殊Tag： '+str(extTag))
        else:
            extTag = None
        decoder = BER_TLV(rawData, extTag)
        for tlvObj in decoder.tlvList:
            self.te_structData.appendPlainText('\t' * (tlvObj[0] - 1) + tlvObj[3] + ' ' + tlvObj[4] + ' ' + tlvObj[5])

    def setExTag(self):
        if self.chb_extTag.isChecked():
            self.le_extTag.setEnabled(True)
        else:
            self.le_extTag.setEnabled(False)

    def chkStr(self, str):
        statusCode = 0
        # 数据格式检查
        if str == None:
            self.te_structData.setPlainText('TLV数据为空!')
            statusCode = 1
        if type(str) == int:
            self.te_structData.setPlainText('TLV数据不是有效的 HexString !')
            statusCode = 1
        # 判断数据长度
        if len(str) % 2 != 0:
            self.te_structData.setPlainText('TLV数据长度错误！')
            statusCode = 1
        # 处理可能的数据前缀
        if str[0:2] in ('0x', '0X'):
            str = str[2:]
        # 检查16进制字符类型
        match = re.fullmatch(r'^[0-9a-fA-F]+$', str)
        if match == None:
            self.te_structData.setPlainText('TLV数据不是有效的 HexString !')
            statusCode = 1
        return statusCode

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TlvTools()
    window.show()
    sys.exit(app.exec_())