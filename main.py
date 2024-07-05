import sys
import cv2
import numpy as np
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QFileDialog, QComboBox, \
    QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        # Настройка главного окна
        self.setFixedSize(1000, 950)
        self.setWindowTitle("Image Editor")

        # Лейбл для показа изображения
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(1000, 600)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Текст, поля ввода для функции изменения размеров
        self.cut_instruction = QLabel(self)
        self.cut_instruction.setText("Для изменения размера изображения введите:")
        self.cut_instruction.move(20, 660)
        self.cut_instruction.adjustSize()

        self.new_width = QLabel(self)
        self.new_width.setText("Новая ширина:")
        self.new_width.move(20, 695)
        self.new_width.adjustSize()

        self.new_height = QLabel(self)
        self.new_height.setText("Новая высота:")
        self.new_height.move(20, 730)
        self.new_height.adjustSize()

        self.new_width_line = QLineEdit(self)
        self.new_width_line.move(140, 687)

        self.new_height_line = QLineEdit(self)
        self.new_height_line.move(140, 723)

        # Кнопка, по нажатию которой меняется размер
        self.cut_button = QPushButton(self)
        self.cut_button.setText("Изменить размер")
        self.cut_button.move(20, 780)
        self.cut_button.adjustSize()
        self.cut_button.clicked.connect(lambda: self.resize())

        # Текст, поля ввода для функции изменения яркости
        self.bright_instruction = QLabel(self)
        self.bright_instruction.setText("Число, на которое понизить параметр яркости")
        self.bright_instruction.move(375, 660)
        self.bright_instruction.adjustSize()

        self.bright_line = QLineEdit(self)
        self.bright_line.move(375, 692)

        # Кнопка, по нажатию которой меняется яркость
        self.bright_button = QPushButton(self)
        self.bright_button.setText("Изменить яркость")
        self.bright_button.move(375, 740)
        self.bright_button.adjustSize()
        self.bright_button.clicked.connect(lambda: self.change_brightness())

        # Текст, поля ввода для функции вставки прямоугольника
        self.rectangle_start = QLabel(self)
        self.rectangle_start.setText("Вставка прямоугольника.")
        self.rectangle_start.move(700, 660)
        self.rectangle_start.adjustSize()

        self.rectangle_instruction = QLabel(self)
        self.rectangle_instruction.setText("Введите следующие координаты:")
        self.rectangle_instruction.move(700, 685)
        self.rectangle_instruction.adjustSize()

        self.left_x_rectanglelabel = QLabel(self)
        self.left_x_rectanglelabel.setText("Левый верхний угол по X:")
        self.left_x_rectanglelabel.move(700, 720)
        self.left_x_rectanglelabel.adjustSize()

        self.left_y_rectanglelabel = QLabel(self)
        self.left_y_rectanglelabel.setText("Левый верхний угол по Y:")
        self.left_y_rectanglelabel.move(700, 755)
        self.left_y_rectanglelabel.adjustSize()

        self.right_x_rectanglelabel = QLabel(self)
        self.right_x_rectanglelabel.setText("Правый нижний угол по X:")
        self.right_x_rectanglelabel.move(700, 790)
        self.right_x_rectanglelabel.adjustSize()

        self.right_y_rectanglelabel = QLabel(self)
        self.right_y_rectanglelabel.setText("Правый нижний угол по Y:")
        self.right_y_rectanglelabel.move(700, 825)
        self.right_y_rectanglelabel.adjustSize()

        self.left_x_rectangleline = QLineEdit(self)
        self.left_x_rectangleline.move(880, 712)

        self.left_y_rectangleline = QLineEdit(self)
        self.left_y_rectangleline.move(880, 749)

        self.right_x_rectangleline = QLineEdit(self)
        self.right_x_rectangleline.move(880, 784)

        self.right_y_rectangleline = QLineEdit(self)
        self.right_y_rectangleline.move(880, 820)

        # Кнопка, по нажатию которой меняется яркость
        self.rectangle_button = QPushButton(self)
        self.rectangle_button.setText("Вставить прямоугольник")
        self.rectangle_button.move(700, 865)
        self.rectangle_button.adjustSize()
        self.rectangle_button.clicked.connect(lambda: self.draw())

        # Список для выбора цветовых каналов изображения
        self.combobox = QComboBox(self)
        self.combobox.addItems(["Все каналы", "Красный канал", "Зеленый канал", "Синий канал"])
        self.combobox.move(375, 800)
        self.combobox.adjustSize()

        self.change_chanel = QPushButton(self)
        self.change_chanel.setText("Поменять канал")
        self.change_chanel.move(375, 855)
        self.change_chanel.adjustSize()
        self.change_chanel.clicked.connect(lambda: self.display_image(self.current_image))

        # Кнопки открытия и съемки изображения
        self.choose_button = QPushButton(self)
        self.choose_button.setText("Выбрать картинку")
        self.choose_button.move(260, 610)
        self.choose_button.adjustSize()
        self.choose_button.clicked.connect(lambda: self.choose_cliked())

        self.camera_button = QPushButton(self)
        self.camera_button.setText("Открыть веб-камеру")
        self.camera_button.move(425, 610)
        self.camera_button.adjustSize()
        self.camera_button.clicked.connect(lambda: self.start_camera())

        self.photo_button = QPushButton(self)
        self.photo_button.setText("Сделать фото")
        self.photo_button.move(605, 610)
        self.photo_button.adjustSize()
        self.photo_button.clicked.connect(lambda: self.capture_image())
        self.photo_button.setEnabled(False)

        # Дополнительные переменные
        self.cap = None
        self.timer = QTimer(self)
        self.timer.timeout.connect(lambda: self.display_video_stream())

        self.current_image = None


    def resize(self):
        """Функция изменения размеров изображения"""
        try:
            resized_image = cv2.resize(self.current_image,
                                       ((int(self.new_width_line.text())), int(self.new_height_line.text())))
            self.current_image = resized_image
            self.display_image(resized_image)
            self.new_width_line.setText("")
            self.new_height_line.setText("")
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Проверьте правильность ввода размеров, а также выбора изображения!")
            self.new_width_line.setText("")
            self.new_height_line.setText("")

    def change_brightness(self):
        """Функция изменения яркости изображения"""
        try:
            brightness = int(self.bright_line.text())
            adjusted_image = self.adjust_brightness(self.current_image, brightness)
            self.current_image = adjusted_image
            self.display_image(adjusted_image)
            self.bright_line.setText("")
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Проверьте правильность ввода величины, а также выбора изображения!")
            self.bright_line.setText("")

    def draw(self):
        """Функция вывода прямоугольника"""
        try:
            start_point = (int(self.left_x_rectangleline.text()), int(self.left_y_rectangleline.text()))
            end_point = (int(self.right_x_rectangleline.text()), int(self.right_y_rectangleline.text()))
            color = (255, 0, 0)
            thickness = 2
            image = cv2.rectangle(self.current_image, start_point, end_point, color, thickness)
            self.display_image(image)
            self.left_x_rectangleline.setText("")
            self.left_y_rectangleline.setText("")
            self.right_x_rectangleline.setText("")
            self.right_y_rectangleline.setText("")
            self.current_image = image
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Проверьте правильность ввода координат, а также выбора изображения!")
            self.left_x_rectangleline.setText("")
            self.left_y_rectangleline.setText("")
            self.right_x_rectangleline.setText("")
            self.right_y_rectangleline.setText("")

    def choose_cliked(self):
        """Функция выбора изображения из файлов"""
        file_dialog = QFileDialog(self)
        filename, _ = file_dialog.getOpenFileName(self, "Выбрать изображение", "", "Изображения (*.png *.jpg)")
        if filename:
            self.current_image = cv2.imread(filename)
            self.display_image(self.current_image)

    def display_image(self, image):
        """Функция вывода изображения на экран (учитывая выбранный цветовой канал в списке)
        :param image - выводимое изображение"""
        if image is not None:
            channel = self.combobox.currentText()
            if channel == "Красный канал":
                image = self.extract_channel(image, 2)
            elif channel == "Зеленый канал":
                image = self.extract_channel(image, 1)
            elif channel == "Синий канал":
                image = self.extract_channel(image, 0)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            height, width, channel = image.shape
            bytes_per_line = 3 * width
            q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            self.image_label.setPixmap(pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio))

    def start_camera(self):
        """Функция запуска камеры"""
        try:
            self.cap = cv2.VideoCapture(0)
            self.timer.start(30)
            self.photo_button.setEnabled(True)
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Проблема с подключением к камере!")

    def capture_image(self):
        """Функция захвата изображения с камеры"""
        ret, frame = self.cap.read()
        if ret:
            self.current_image = frame
            self.display_image(frame)
            self.timer.stop()
            self.cap.release()
            self.photo_button.setEnabled(False)

    def display_video_stream(self):
        """Функция вывода фото"""
        ret, frame = self.cap.read()
        if ret:
            self.current_image = frame
            self.display_image(frame)

    @staticmethod
    def extract_channel(image, channel_idx):
        """Функция вывода канала"""
        channel_image = np.zeros_like(image)
        channel_image[:, :, channel_idx] = image[:, :, channel_idx]
        return channel_image

    @staticmethod
    def adjust_brightness(image, brightness):
        """Функция изменения параметра яркости"""
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        h, s, v = cv2.split(hsv)
        v = np.clip(v - brightness, 0, 255)
        final_hsv = cv2.merge((h, s, v))
        image = cv2.cvtColor(final_hsv, cv2.COLOR_HSV2BGR)
        return image


app = QApplication(sys.argv)
app.setStyle('Fusion')
MainWindow = MainWindow()
MainWindow.show()
sys.exit(app.exec_())
