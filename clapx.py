#version 1.4

import os
import sys
from configparser import ConfigParser
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QPushButton, QMessageBox, QCheckBox, QTextEdit
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QPixmap

config_file = 'config.ini'
config = ConfigParser()
config.read(config_file)



class Crosshair(QtWidgets.QWidget):
    def __init__(self, parent=None, image_path=""):
        QtWidgets.QWidget.__init__(self, parent)
        self.image_path = image_path
        self.label = QtWidgets.QLabel(self)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.WindowStaysOnTopHint | QtCore.Qt.WindowTransparentForInput)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        QtWidgets.QApplication.instance().installEventFilter(self)

        if not self.load_image():
            
            sys.exit(1)  # Exit if the user cancels image selection

    def load_image(self):
        if not self.image_path:
            return False

        image_reader = QtGui.QImageReader(self.image_path)
        width = image_reader.size().width()
        height = image_reader.size().height()
        if width == 30 and height == 30:
            pass
        else:
            QtWidgets.QMessageBox.warning(self, "Invalid Size!", "The image you selected is not 30x30 pixels. Please select an image that is 30x30 pixels.")
            os.execv(sys.executable, ['python'] + sys.argv)

        pixmap = QtGui.QPixmap(self.image_path)
        self.label.setPixmap(pixmap)

        self.resize(pixmap.width(), pixmap.height())
        self.move(QtWidgets.QApplication.desktop().screen().rect().center() - self.rect().center() + QtCore.QPoint(1, 1))

        return True

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F3:
            file_selector_widget.show()
        elif event.key() == QtCore.Qt.Key_F4:
            file_selector_widget.close()
            self.close()
            self.close()
        elif event.key() == QtCore.Qt.Key_F5:
            manual_widget.show()

class Manual(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("How to use Clap X")
        self.setFixedSize(300, 250)
        self.move(QtWidgets.QApplication.desktop().screen().rect().center() - self.rect().center() + QtCore.QPoint(1, 1))
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        
        self.text = QTextEdit(self)
        self.text.setReadOnly(True)  # Set the text edit to be read-only
        
        # Set text for each line
        self.text.setPlainText("F3 = Open the crosshair selector if you wish to change your selection.\n\nF4 = Close Clap X\n\nF5 = Open this manual again. (Useful if you check 'hide on start' and forget how to use Clap X)\n\nCustom Crosshairs:\nTo use a custom crosshair simply press 'Open Folder' on the crosshair selector and drag your own crosshair image in. It must be a *.png. It must also be 30x30 pixels and have a transparent background. There are 3 crosshairs pre-installed on Clap X.")
        
        self.checkbox = QCheckBox("Hide on start?", self)
        self.checkbox.stateChanged.connect(self.checkbox_state_changed)
        if (config['config_vars']['hide_on_start'] == "1"):
            self.checkbox.setChecked(True)
        elif (config['config_vars']['hide_on_start'] == "0"):
            self.checkbox.setChecked(False)
        
        
        layout = QVBoxLayout(self)
        layout.addWidget(self.text)
        layout.addWidget(self.checkbox)

    def checkbox_state_changed(self, state):
        if state == QtCore.Qt.Checked:
            config.set('config_vars', 'hide_on_start', '1')
            with open(config_file, 'w') as configwriter:
                config.write(configwriter)
        else:
            config.set('config_vars', 'hide_on_start', '0')
            with open(config_file, 'w') as configwriter:
                config.write(configwriter)

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F4:
            Crosshair().close()
            file_selector_widget.close()
            self.close()

class FileSelectorWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Crosshair Selector")
        #self.setGeometry(0, 0, 300, 70)
        self.setFixedSize(300, 120)
        self.move(QtWidgets.QApplication.desktop().screen().rect().center() - self.rect().center() + QtCore.QPoint(1, 1))

        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)


        self.crosshair_widget = None

        self.folder_path = 'crosshairs/'  # Change this to your folder path

        self.file_dropdown = QComboBox(self)
        self.file_dropdown.setObjectName("fileDropdown")
        self.file_dropdown.setSizeAdjustPolicy(QComboBox.AdjustToContents)

        self.select_button = QPushButton("Apply", self)
        self.select_button.clicked.connect(self.apply)

        self.folder_button = QPushButton("Open Folder", self)
        self.folder_button.clicked.connect(self.open_folder)

        

        layout = QVBoxLayout(self)
        layout.addWidget(self.file_dropdown)
        layout.addWidget(self.select_button)
        layout.addWidget(self.folder_button)

        self.populate_dropdown()
    

    def populate_dropdown(self):
        self.files = [f for f in os.listdir(self.folder_path) if os.path.isfile(os.path.join(self.folder_path, f)) and f.lower().endswith('.png')]
        
        if not self.files:
            self.file_dropdown.addItem("No *.png Files Available")
        for file in self.files:
            icon = QIcon(self.folder_path + file)
            self.file_dropdown.addItem(icon, file)

    def apply(self):
        if (self.files):
            self.load_crosshair()
            self.hide()
        else:
            QtWidgets.QMessageBox.warning(self, "No File Selected!", "There are no images in the folder! Open the folder and paste some in!")

        

    def open_folder(self):
        path = "crosshairs"
        os.startfile(path)

    def load_crosshair(self):
        selected_file = self.file_dropdown.currentText()
        if selected_file:
            image_path = os.path.join(self.folder_path, selected_file)
            self.crosshair_widget = Crosshair(image_path=image_path)
            self.crosshair_widget.show()
        else:
            QMessageBox.warning(self, "No File Selected", "Please select a file")
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F4:
            Crosshair().close()
            manual_widget.close()
            self.close()
        elif event.key() == QtCore.Qt.Key_F5:
            manual_widget.show()
        

if __name__ == "__main__":
    app = QApplication([])

    # Create and show FileSelector widget
    file_selector_widget = FileSelectorWidget()
    file_selector_widget.show()
    
    manual_widget = Manual()
    if (config['config_vars']['hide_on_start'] == "0"):
        manual_widget.show()

    sys.exit(app.exec_())


#open on start crap
    