import os
import tkinter as tk
from tkinter import filedialog, messagebox
import math
import random


class DirectoryNode:
    def __init__(self, path):
        self.path = path
        self.name = os.path.basename(path) or path
        self.size = 0
        self.children = []

    def add_child(self, child):
        self.children.append(child)
        self.size += child.size


def scan_directory(path):
    """Recursively build directory tree with sizes."""
    node = DirectoryNode(path)
    try:
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    child = scan_directory(entry.path)
                    node.add_child(child)
                else:
                    try:
                        size = entry.stat(follow_symlinks=False).st_size
                    except OSError:
                        size = 0
                    child = DirectoryNode(entry.path)
                    child.size = size
                    node.add_child(child)
    except PermissionError:
        pass
    return node


def random_color():
    return '#%06x' % random.randint(0, 0xFFFFFF)


def draw_sunburst(canvas, node, center, radius, start_angle=0, extent=360):
    if not node.children or radius <= 20:
        return
    angle = start_angle
    for child in node.children:
        if node.size == 0:
            child_extent = 0
        else:
            child_extent = extent * child.size / node.size
        color = random_color()
        tag = child.path
        canvas.create_arc(
            center[0]-radius,
            center[1]-radius,
            center[0]+radius,
            center[1]+radius,
            start=angle,
            extent=child_extent,
            fill=color,
            outline='',
            tags=tag
        )
        canvas.tag_bind(tag, '<Button-1>', lambda e, c=child: show_details(e, c))
        draw_sunburst(canvas, child, center, radius-20, angle, child_extent)
        angle += child_extent


def show_details(event, node):
    messagebox.showinfo(title=node.name, message=f"{node.path}\n{node.size} bytes")


def start_scan(root):
    directory = filedialog.askdirectory()
    if not directory:
        return
    root.title(f"Disk Scan - {directory}")
    node = scan_directory(directory)
    canvas = tk.Canvas(root, width=600, height=600, bg='white')
    canvas.pack(fill='both', expand=True)
    draw_sunburst(canvas, node, center=(300, 300), radius=280)


def main():
    root = tk.Tk()
    root.geometry('620x620')
    root.title('Disk Scan')
    tk.Button(root, text='Choose Directory', command=lambda: start_scan(root)).pack()
    tk.Label(root, text='Click on a segment to see details.').pack()
    root.mainloop()


if __name__ == '__main__':
    main()
