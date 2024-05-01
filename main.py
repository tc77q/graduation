import sys
import time
import UI_.res_rc
import subprocess
from PyQt5.QtCore import Qt, QTimer, QObject, pyqtSignal, QThread
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QApplication
from UI_.UI import Ui_MainWindow

import os


save_addr = ''
class ModelThread(QThread):
    finished = pyqtSignal(str)  # 函数跑完后返回的类型
    stopped = pyqtSignal()
    trans = pyqtSignal(str)
    algo_send = pyqtSignal(str)

    def __init__(self, room, step):
        super(ModelThread, self).__init__()
        self.room = room
        self.env = self.room + '-v4'
        self.step = step
        self.stopped_flag = False
        self.algo = "a2c"

    def choose_algo(self):
        algo = self.room
        if algo=="BeamRider":
            if self.step < 1000000 : self.algo = "dqn"
            else: self.algo = "qrdqn"

        elif algo == "Breakout":
            if self.step < 750000 : self.algo = "ppo"
            else:self.algo = "dqn"

        elif algo == "Enduro":
            if self.step < 500000 : self.algo = "ppo"
            else:self.algo = "qrdqn"

        elif algo == "Pong":
            if self.step < 900000 : self.algo = "ppo"
            else:self.algo = "dqn"

        elif algo == "Qbert":
            if self.step < 600000 : self.algo = "qrdqn"
            else:self.algo = "dqn"
            # self.algo = "qrdqn"

        elif algo == "Seaquest":
            self.algo = "ppo"
            if self.step > 1750000 : self.algo = 'dqn'

        elif algo == "SpaceInvaders":
            self.algo = "qrdqn"

        elif algo == "MsPacman":
            if self.step < 300000: self.algo = 'a2c'
            elif self.step <800000: self.algo = 'qrdqn'
            else: self.algo = 'dqn'

        elif algo == "Asteroids":
            if self.step < 500000: self.algo = 'ppo'
            elif self.step < 1300000 : self.algo = "a2c"
            else  : self.algo = 'ppo'

        elif algo == "RoadRunner":
            self.algo = "ppo"

    def write(self, text):
        self.trans.emit(str(text))  # 发射信号

    def run(self):

        self.choose_algo()
        self.write(f"已为您自动选择{self.algo}算法")
        self.algo_send.emit(self.algo)
        command = f"python train.py --algo {self.algo} --env {self.env} -n {self.step}"
        self.subp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE,  encoding="utf-8")


        # t1 = time.time()
        # time.sleep(10)
        while(self.subp.poll() is None):
            if self.stopped_flag:
                self.subp.kill()
                self.stopped.emit()
                return

            str = self.subp.stdout.readline()

            if str != b'':
                print(str.strip('\r\n'))
                self.write(str.strip('\r\n'))
            else:
                continue

        self.finished.emit("运行结束")
            # self.trans.emit(str)
            # print(str)
            # login.append_plain(str)

    def stop(self):
        self.stopped_flag = True




class Login(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(Login, self).__init__(parent)
        self.setupUi(self)
        self.save_addr = ''
        self.algo = 'ppo'
        self.env = ''
        self.step = 1000
        self.setWindowFlags(Qt.FramelessWindowHint)  # 隐藏标题栏
        self.pushButton_2.clicked.connect(QApplication.quit)
        self.pushButton.clicked.connect(self.minimizeWindow)
        self.pushButton_start.clicked.connect(self.displayContent)
        self.pushButton_export.clicked.connect(self.stopModel)
        self.model_thread = None

    def minimizeWindow(self):
        self.showMinimized()  # 将窗口最小化

    def append_plain(self, str):
        self.plainTextEdit.appendPlainText(str)
    def algo_update(self, str):
        self.algo = str
    def displayContent(self):
        self.plainTextEdit.clear()
        self.env = self.comboBox.currentText() + '-v4'
        self.step = self.spinBox.value()

        self.plainTextEdit.appendPlainText(
            f"场景选择: {self.env}\n训练步数: {self.step}\n---------------------\n模型运行中...")

        self.run(self.comboBox.currentText(), self.step)

    def run(self, room, step):
        self.model_thread = ModelThread(room, step)
        self.model_thread.finished.connect(self.modelFinished)
        self.model_thread.stopped.connect(self.modelStopped)
        self.model_thread.trans.connect(self.append_plain)
        self.model_thread.algo_send.connect(self.algo_update)
        self.model_thread.start()


    def stopModel(self):
        with open("save_path.txt", 'r') as f:
            self.save_addr = f.read()
            print(f.read)
            f.close()
        if self.model_thread:
            self.model_thread.stop()

    def modelFinished(self, result):
        # self.plainTextEdit.clear()
        with open("save_path.txt", 'r') as f:
            self.save_addr = f.read()
            # print(f.read)
            f.close()

        if self.model_thread:
            self.model_thread.stop()
        # self.plainTextEdit.appendPlainText(result)  # 在plainTextEdit中显示模型运行结果
        QMessageBox.information(self, "提示", f"模型运行已完成，保存地址:{self.save_addr}")
        self.show_res()

    def modelStopped(self):
        self.plainTextEdit.appendPlainText(f"模型中止成功,  保存地址:{self.save_addr}")
        QMessageBox.information(self, "提示", f"模型已停止   保存地址:{self.save_addr}")
        self.show_res()

    def show_res(self):
        question = QMessageBox.question(self,'提问','是否需要结果展示',)
        if question == QMessageBox.Yes:

            command = f"python enjoy.py --algo {self.algo} --env {self.env} --folder logs/ -n 5000"
            self.subp = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,encoding="utf-8")
        else:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = Login()
    login.show()
    sys.exit(app.exec_())
