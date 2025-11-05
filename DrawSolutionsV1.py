import tkinter as tk
from tkinter import colorchooser, filedialog
from PIL import Image, ImageDraw
import math
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
from opensimplex import OpenSimplex

class DeformableCanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Деформируемый Paint (с OpenGL)")
        self.root.geometry("900x800")

        # Верхняя панель
        top_frame = tk.Frame(root)
        top_frame.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

        tk.Label(top_frame, text="Шаблон:").pack(side=tk.LEFT)
        self.pattern_var = tk.StringVar(value="Синусоидальный")
        pattern_options = [
            "Синусоидальный", "Круговой", "Спиральный", "Волны", "Шум Перлина", "Нет"
        ]
        self.pattern_menu = tk.OptionMenu(top_frame, self.pattern_var, *pattern_options)
        self.pattern_menu.pack(side=tk.LEFT, padx=5)

        tk.Label(top_frame, text="Цвет:").pack(side=tk.LEFT, padx=(10, 0))
        self.color_button = tk.Button(top_frame, bg="black", width=3, height=1, command=self.choose_color)
        self.color_button.pack(side=tk.LEFT, padx=5)
        self.current_color = "black"

        tk.Label(top_frame, text="Толщина:").pack(side=tk.LEFT, padx=(10, 0))
        self.brush_size = tk.Scale(top_frame, from_=1, to=10, orient=tk.HORIZONTAL, length=100)
        self.brush_size.set(2)
        self.brush_size.pack(side=tk.LEFT, padx=5)

        # Кнопки
        save_btn = tk.Button(top_frame, text="Сохранить PNG", command=self.save_as_png)
        save_btn.pack(side=tk.RIGHT, padx=5)

        clear_btn = tk.Button(top_frame, text="Очистить", command=self.clear_canvas)
        clear_btn.pack(side=tk.RIGHT, padx=5)

        # Холст Tkinter
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Состояния
        self.lines = []
        self.current_line = None
        self.is_animated = False
        self.animation_id = None
        self.deformation_offset = 0
        self.noise_gen = OpenSimplex()  # инициализируем шум Перлина

        # Привязка событий
        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw_smoothly)
        self.root.bind("<Key>", self.on_key)

    def choose_color(self):
        color = colorchooser.askcolor(color=self.current_color)[1]
        if color:
            self.current_color = color
            self.color_button.config(bg=color)

    def start_draw(self, event):
        self.current_line = [(event.x, event.y)]

    def draw_smoothly(self, event):
        if self.current_line is None:
            return
        x, y = event.x, event.y
        last_x, last_y = self.current_line[-1]

        # Интерполируем точки между событиями мыши для плавности
        dx = x - last_x
        dy = y - last_y
        dist = max(abs(dx), abs(dy))
        steps = int(dist)

        if steps > 0:
            for i in range(1, steps + 1):
                ix = int(last_x + dx * i / steps)
                iy = int(last_y + dy * i / steps)
                self.current_line.append((ix, iy))
                self.canvas.create_line(ix, iy, ix, iy, fill=self.current_color, width=self.brush_size.get())

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
            elif pattern == "Шум Перлина":
                scale = 0.02
                dx = 30 * self.noise_gen.noise2(x * scale, y * scale, octaves=3, persistence=0.5, lacunarity=2.0) + self.deformation_offset
                dy = 30 * self.noise_gen.noise2(x * scale + 100, y * scale + 100, octaves=3, persistence=0.5, lacunarity=2.0) + self.deformation_offset
            elif pattern == "Нет":
                dx, dy = 0, 0
            else:
                dx, dy = 0, 0
            deformed.append((x + dx, y + dy))
        return deformed

    def save_line_on_release(self, event=None):
        if self.current_line and len(self.current_line) > 1:
            self.lines.append((self.current_line[:], self.current_color, self.brush_size.get()))
        self.current_line = None

    def clear_canvas(self):
        self.lines.clear()
        self.current_line = None
        self.canvas.delete("all")
        if self.is_animated:
            self.toggle_animation()

    def save_as_png(self):
        img = Image.new("RGB", (800, 600), "white")
        draw = ImageDraw.Draw(img)

        for line, color, width in self.lines:
            deformed_line = self.apply_deformation(line)
            if len(deformed_line) > 1:
                draw.line(deformed_line, fill=color, width=width)

        file_path = filedialog.asksaveasfilename(defaultextension=".png",
                                                 filetypes=[("PNG files", "*.png")])
        if file_path:
            img.save(file_path)

if __name__ == "__main__":
    root = tk.Tk()
    app = DeformableCanvasApp(root)
    root.bind("<ButtonRelease-1>", app.save_line_on_release)
    root.mainloop()