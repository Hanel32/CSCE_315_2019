import sys
#Have to install PyQt5, pip install PyQt5
import Queries
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QLabel, QLineEdit, QPushButton, QTextEdit

class Example(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()
    
    def initUI(self):
        
        self.lbl = QLabel("Bacon Number",self)

        combo = QComboBox(self)
        combo.addItem("Bacon Number")
        combo.addItem("Constellation of Co-Stars")
        combo.addItem("Typecasting")
        combo.addItem("Cover Roles")
        combo.addItem("Best of Days, Worst of Days")
        combo.move(50, 40)
        
        self.arg1Lbl = QLabel("Actor Name                                 ",self)
        self.arg1Lbl.move(50,130)
        self.arg1 = QLineEdit(self)
        self.arg1.move(50, 150)
        self.arg1.resize(250,40)
        
        self.arg2Lbl = QLabel("Actor Name                                 ",self)
        self.arg2Lbl.move(450,130)
        self.arg2 = QLineEdit(self)
        self.arg2.move(450,150)
        self.arg2.resize(250,40)
        
        self.button = QPushButton('Execute', self)
        self.button.move(50,250)
        self.button.clicked.connect(self.on_click)
        
        self.output=QTextEdit(self)
        self.output.move(50,350)
        self.output.resize(650,400)
        self.output.setEnabled(False)
        self.output.verticalScrollBar()
        
        self.outputLbl = QLabel("Output",self)
        self.outputLbl.move(50,330)

        combo.activated[str].connect(self.onActivated)        
         
        self.setGeometry(1000, 1000, 800, 800)
        self.setWindowTitle('Phase 3 GUI')
        self.show()

    def onActivated(self, text):
        
        self.lbl.setText(text)
        self.lbl.adjustSize()  
        
        if(text == "Bacon Number"):
            self.arg2.setEnabled(True)
            self.arg1Lbl.setText("Actor Name")
            self.arg2Lbl.setText("Actor Name")
        elif(text == "Constellation of Co-Stars"):
            self.arg2.setEnabled(True)
            self.arg1Lbl.setText("Actor Name")
            self.arg2Lbl.setText("Number of Co-Star Appearances")
        elif(text == "Typecasting"):
            self.arg2.setEnabled(False)
            self.arg1Lbl.setText("Actor Name")
            self.arg2Lbl.setText("")
            self.arg2.setText("")
        elif(text == "Cover Roles"):
            self.arg2.setEnabled(False)
            self.arg2.setText("")
            self.arg1Lbl.setText("Character Name")
            self.arg2Lbl.setText("")
        elif(text == "Best of Days, Worst of Days"):
            self.arg2.setEnabled(False)
            self.arg2.setText("")
            self.arg1Lbl.setText("Actor Name")
            self.arg2Lbl.setText("")
        
    def on_click(self):
        textBox1 = self.arg1.text()
        textBox2 = self.arg2.text()
         
        if(self.lbl.text() == "Bacon Number"):
            #Call Bacon Number
            string = queries.BaconNumber(textBox1,textBox2)
            self.output.setText(string)
            self.output.setEnabled(True)
        elif(self.lbl.text() == "Constellation of Co-Stars"):
            #Call Constellation of Co-Star
            string = queries.constellation(textBox1,textBox2)
            self.output.setText(string)
            self.output.setEnabled(True)
        elif(self.lbl.text() == "Typecasting"):
            #Call Typecasting function
            string = queries.Typecasting(queries,textBox1)
            self.output.setText(string)
            self.output.setEnabled(True)
        elif(self.lbl.text() == "Cover Roles"):
            #Call Cover Roles
            string = queries.CoverRoles(textBox1)
            self.output.setText(string)
            self.output.setEnabled(True)
        elif(self.lbl.text() == "Best of Days, Worst of Days"):
            #Call Best of Days, Worst of Days
            string = queries.BestWorstDays(textBox1)
            self.output.setText(string)
            self.output.setEnabled(True)
            
        self.arg1.setText("")
        self.arg2.setText("")
    
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    queries = Queries.Queries()
    ex = Example()
    sys.exit(app.exec_())