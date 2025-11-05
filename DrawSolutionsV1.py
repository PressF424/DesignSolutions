import tkinter as tk
import math

class DeformableCanvasApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Деформируемый Paint")
        self.canvas = tk.Canvas(root, bg="white", width=800, height=600)
        self.canvas.pack()

        self.lines = []
        self.current_line = None
        self.deformation_offset = 0

        self.canvas.bind("<Button-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.root.bind("<Key>", self.on_key)

    def start_draw(self, event):
        self.current_line = [(event.x, event.y)]

    def draw(self, event):
        if self.current_line is None:
            return
        self.current_line.append((event.x, event.y))
        if len(self.current_line) >= 2:
            x1, y1 = self.current_line[-2]
            x2, y2 = self.current_line[-1]
            self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)

    def on_key(self, event):
        if event.char.lower() == 'd':
            self.deform_and_redraw()

    def deform_and_redraw(self):
        self.canvas.delete("all")
        self.deformation_offset += 10

        for line in self.lines:
            deformed_line = self.apply_deformation(line)
            for i in range(len(deformed_line) - 1):
                x1, y1 = deformed_line[i]
                x2, y2 = deformed_line[i+1]
                self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)

        if self.current_line and len(self.current_line) > 1:
            deformed_current = self.apply_deformation(self.current_line)
            for i in range(len(deformed_current) - 1):
                x1, y1 = deformed_current[i]
                x2, y2 = deformed_current[i+1]
                self.canvas.create_line(x1, y1, x2, y2, fill="black", width=2)

    def apply_deformation(self, points):
        deformed = []
        for x, y in points:
            dx = 20 * math.sin((y + self.deformation_offset) * 0.02)
            deformed.append((x + dx, y))
        return deformed

    def save_line_on_release(self, event=None):
        if self.current_line and len(self.current_line) > 1:
            self.lines.append(self.current_line[:])
        self.current_line = None

if __name__ == "__main__":
    root = tk.Tk()
    app = DeformableCanvasApp(root)
    root.bind("<ButtonRelease-1>", app.save_line_on_release)
    root.mainloop()