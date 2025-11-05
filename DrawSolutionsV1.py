import tkinter as tk
from tkinter import colorchooser, filedialog
from PIL import Image, ImageDraw
import math

class DeformableCanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DrawSolutions")
        self.root.geometry("900x700")

        # Основной фрейм
        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        # Выбор шаблона
        tk.Label(top_frame, text="Стиль:").pack(side=tk.LEFT)
        self.pattern_var = tk.StringVar(value="Нет")
        # Добавлены новые шаблоны
        pattern_options = ["Синусоидальный", "Круговой", "Спиральный", "Волны", "Турбулентность", "Метаморфоз", "Кристалл", "Фрактал", "Пульсар", "Хаос", "Нет"]        
        self.pattern_menu = tk.OptionMenu(top_frame, self.pattern_var, *pattern_options)
        self.pattern_menu.pack(side=tk.LEFT, padx=5)

        # Цвет
        tk.Label(top_frame, text="Цвет:").pack(side=tk.LEFT, padx=(10, 0))
        self.color_button = tk.Button(top_frame, bg="black", width=3, height=1, command=self.choose_color)
        self.color_button.pack(side=tk.LEFT, padx=5)
        self.current_color = "black"

        # Толщина
        tk.Label(top_frame, text="Толщина:").pack(side=tk.LEFT, padx=(10, 0))
        self.brush_size = tk.Scale(top_frame, from_=1, to=10, orient=tk.HORIZONTAL, length=100)
        self.brush_size.set(4)
        self.brush_size.pack(side=tk.LEFT, padx=5)

        # Кнопка очистки
        clear_btn = tk.Button(top_frame, text="Очистить", command=self.clear_canvas)
        clear_btn.pack(side=tk.LEFT, padx=5)

        # Кнопка сохранения
        save_btn = tk.Button(top_frame, text="Сохранить в PNG", command=self.save_as_png)
        save_btn.pack(side=tk.RIGHT, padx=5)

        # Холст
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Состояния
        self.lines = []
        self.current_line = None
        self.previous_point = None  # Для интерполяции
        self.is_animated = False
        self.animation_id = None
        self.deformation_offset = 0

        # Привязка событий
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.save_line_on_release)
        self.root.bind("<Key>", self.on_key)

    def choose_color(self):
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.current_color = color
            self.color_button.config(bg=color)

    def start_draw(self, event):
        self.current_line = [(event.x, event.y)]
        self.previous_point = (event.x, event.y) # Сброс предыдущей точки

    def draw(self, event):
        if self.current_line is None:
            return

        current_point = (event.x, event.y)
        # Интерполяция между предыдущей и текущей точкой
        if self.previous_point:
            points_to_add = self.interpolate_points(self.previous_point, current_point)
            for point in points_to_add:
                if point != self.current_line[-1]: # Избегаем дубликатов
                    self.current_line.append(point)
                    # Рисуем только последний сегмент
                    x1, y1 = self.current_line[-2]
                    x2, y2 = self.current_line[-1]
                    self.canvas.create_line(x1, y1, x2, y2, fill=self.current_color, width=self.brush_size.get())
        else:
            # На случай, если предыдущая точка не установлена (первое движение)
            self.current_line.append(current_point)
            x1, y1 = self.current_line[-2]
            x2, y2 = self.current_line[-1]
            self.canvas.create_line(x1, y1, x2, y2, fill=self.current_color, width=self.brush_size.get())

        self.previous_point = current_point


    def interpolate_points(self, p1, p2, max_dist=2):
        """Интерполирует точки между p1 и p2, если расстояние между ними больше max_dist."""
        x1, y1 = p1
        x2, y2 = p2
        dx = x2 - x1
        dy = y2 - y1
        distance = math.hypot(dx, dy)

        if distance <= max_dist:
            return [p2]

        points = []
        steps = int(distance / max_dist) + 1
        for i in range(1, steps):
            t = i / steps
            ix = x1 + dx * t
            iy = y1 + dy * t
            points.append((ix, iy))
        points.append(p2) # Всегда добавляем конечную точку
        return points


    def on_key(self, event):
        if event.char.lower() == 'd':
            self.toggle_animation()

    def toggle_animation(self):
        if self.is_animated:
            self.is_animated = False
            if self.animation_id:
                self.root.after_cancel(self.animation_id)
        else:
            self.is_animated = True
            self.animate()

    def animate(self):
        if not self.is_animated:
            return
        self.redraw_deformed_lines()
        self.deformation_offset += 0.05
        self.animation_id = self.root.after(50, self.animate)

    def redraw_deformed_lines(self):
        self.canvas.delete("all")
        for line, color, width in self.lines:
            deformed_line = self.apply_deformation(line)
            for i in range(len(deformed_line) - 1):
                x1, y1 = deformed_line[i]
                x2, y2 = deformed_line[i+1]
                self.canvas.create_line(x1, y1, x2, y2, fill=color, width=width)

        # Рисуем текущую линию
        if self.current_line and len(self.current_line) > 1:
            deformed_current = self.apply_deformation(self.current_line)
            for i in range(len(deformed_current) - 1):
                x1, y1 = deformed_current[i]
                x2, y2 = deformed_current[i+1]
                self.canvas.create_line(x1, y1, x2, y2, fill=self.current_color, width=self.brush_size.get())

    def apply_deformation(self, points):
        pattern = self.pattern_var.get()
        deformed = []
        for x, y in points:
            if pattern == "Синусоидальный":
                dx = 20 * math.sin((y + self.deformation_offset) * 0.02)
                dy = 0
            elif pattern == "Круговой":
                dx = 15 * math.cos(x * 0.02 + self.deformation_offset)
                dy = 15 * math.sin(y * 0.02 + self.deformation_offset)
            elif pattern == "Спиральный":
                dx = 10 * math.cos(math.sqrt(x**2 + y**2) * 0.02 + self.deformation_offset)
                dy = 10 * math.sin(math.sqrt(x**2 + y**2) * 0.02 + self.deformation_offset)
            elif pattern == "Волны":
                dx = 10 * math.sin(x * 0.03 + self.deformation_offset) * math.cos(y * 0.03)
                dy = 10 * math.cos(x * 0.03) * math.sin(y * 0.03 + self.deformation_offset)
            # Новые шаблоны
            elif pattern == "Вихрь":
                r = math.sqrt((x - 400)**2 + (y - 300)**2) # Относительно центра холста
                theta = math.atan2(y - 300, x - 400)
                dx = r * 0.01 * math.cos(theta + self.deformation_offset)
                dy = r * 0.01 * math.sin(theta + self.deformation_offset)
            elif pattern == "Кристалл":
                dx = 15 * math.sin(x * 0.05 + self.deformation_offset) * math.cos(y * 0.05)
                dy = 15 * math.cos(x * 0.05) * math.sin(y * 0.05 + self.deformation_offset)
            elif pattern == "Клетка":
                grid_size = 50
                grid_x = (x // grid_size) * grid_size
                grid_y = (y // grid_size) * grid_size
                dx = (grid_x - x) * 0.1 * math.sin(self.deformation_offset)
                dy = (grid_y - y) * 0.1 * math.cos(self.deformation_offset)
            elif pattern == "Фрактал":
                dx = 8 * math.sin(0.02 * x + math.sin(0.05 * y + self.deformation_offset))
                dy = 8 * math.cos(0.02 * y + math.cos(0.05 * x + self.deformation_offset))
            elif pattern == "Пульсар":
                center_x, center_y = 400, 300
                dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                angle = math.atan2(y - center_y, x - center_x)
                pulse_freq = 0.05
                pulse = math.sin(pulse_freq * dist - 2 * self.deformation_offset)
                dx = 15 * pulse * math.cos(angle)
                dy = 15 * pulse * math.sin(angle)
            elif pattern == "Хаос":
                dx = (
                    5 * math.sin(0.03 * x + self.deformation_offset) +
                    7 * math.cos(0.02 * y - 1.3 * self.deformation_offset) +
                    4 * math.sin(0.01 * (x + y) + 0.7 * self.deformation_offset)
                )
                dy = (
                    6 * math.cos(0.025 * x - 0.8 * self.deformation_offset) +
                    5 * math.sin(0.015 * y + 1.1 * self.deformation_offset) +
                    3 * math.cos(0.01 * (x - y) - 0.5 * self.deformation_offset)
                )
            elif pattern == "Нет":
                dx, dy = 0, 0
            else:
                dx, dy = 0, 0
            deformed.append((x + dx, y + dy))
        return deformed

    def save_line_on_release(self, event):
        if self.current_line and len(self.current_line) > 1:
            self.lines.append((self.current_line[:], self.current_color, self.brush_size.get()))
        self.current_line = None
        self.previous_point = None # Сброс при отпускании

    def clear_canvas(self):
        """Очищает холст и сбрасывает все линии."""
        self.lines = []
        self.current_line = None
        self.previous_point = None
        self.canvas.delete("all")
        if self.is_animated:
            self.toggle_animation() # Выключить анимацию, если она была включена

    def save_as_png(self):
        # Создаём PIL-изображение
        img = Image.new("RGB", (800, 600), "white")
        draw = ImageDraw.Draw(img)

        # Рисуем линии на изображении
        for line, color, width in self.lines:
            deformed_line = self.apply_deformation(line)
            if len(deformed_line) > 1:
                draw.line(deformed_line, fill=color, width=width)

        # Сохраняем
        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")])
        if file_path:
            img.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = DeformableCanvasApp(root)
    root.mainloop()