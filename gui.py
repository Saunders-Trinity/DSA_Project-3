import tkinter as tk
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk
import os
from graph import loadEdgesCSV, dijkstra, bellman_ford

class MainScreen:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Main Screen")

        # 1) Load & scale your MainScreen.png
        self.max_w, self.max_h = 800, 800
        script_dir = os.path.dirname(__file__)
        img_path = os.path.join(script_dir, "MainScreen.png")
        try:
            img = Image.open(img_path)
        except Exception as e:
            messagebox.showerror("Error", f"Unable to load background image:\n{e}")
            self.root.destroy()
            return

        sf = min(self.max_w / img.width, self.max_h / img.height, 1.0)
        self.W, self.H = int(img.width * sf), int(img.height * sf)
        img = img.resize((self.W, self.H), Image.LANCZOS)
        self.photo = ImageTk.PhotoImage(img)

        # 2) Load graph data
        csv_path = os.path.join(script_dir, "edges.csv")
        self.graph = loadEdgesCSV(csv_path)

        # 3) Draw background + invisible next-area
        c = tk.Canvas(self.root, width=self.W, height=self.H)
        c.pack()
        c.create_image(0, 0, image=self.photo, anchor="nw")
        rect = c.create_rectangle(0, self.H - 200, 300, self.H, fill="", outline="")
        c.tag_bind(rect, "<Button-1>", self.show_menu)

    def show_menu(self, event=None):
        # Hide main window and show algorithm choice
        self.root.withdraw()
        menu = tk.Toplevel()
        menu.title("Pick an Algorithm")
        menu.geometry(f"{self.W}x{self.H}")

        # Bellman-Ford button
        bf = tk.Button(
            menu,
            text="Bellman-Ford",
            width=20,
            command=lambda m=menu: self.launch_viz(m, 'bf')
        )
        bf.place(x=50, y=50)

        # Dijkstra button
        dj = tk.Button(
            menu,
            text="Dijkstra's",
            width=20,
            command=lambda m=menu: self.launch_viz(m, 'dijkstra')
        )
        dj.place(x=50, y=120)

        # Return to main on close
        menu.protocol("WM_DELETE_WINDOW", lambda: [menu.destroy(), self.root.deiconify()])

    def launch_viz(self, menu_window, algo):
        # Ask user for start and target
        nodes = list(self.graph.keys())
        if not nodes:
            messagebox.showerror("Error", "Graph data is empty.")
            return
        start = simpledialog.askinteger("Start Node", "Enter start node ID:", parent=menu_window)
        if start is None:
            return
        target = simpledialog.askinteger("Target Node", "Enter target node ID:", parent=menu_window)
        if target is None:
            return

        # Run algorithm safely
        try:
            if algo == 'bf':
                edges = bellman_ford(self.graph, start, target)
                title = "Bellman-Ford"
            else:
                edges = dijkstra(self.graph, start, target)
                title = "Dijkstra's"
        except Exception as e:
            messagebox.showerror("Algorithm Error", str(e))
            return

        # Compute a human-readable path: convert edges to node sequence
        if edges:
            edges_rev = list(reversed(edges))
            path_nodes = [edges_rev[0][0]] + [v for _, v in edges_rev]
            path_str = " -> ".join(map(str, path_nodes))
        else:
            path_str = "No path found."

        # Show results in a new window
        viz = tk.Toplevel()
        viz.title(f"{title} Visualization")
        viz.geometry(f"{self.W}x{self.H}")

        tk.Label(
            viz,
            text=f"{title} path:\n{path_str}",
            wraplength=self.W - 40,
            justify="left"
        ).pack(padx=20, pady=20, anchor="w")

        viz.protocol("WM_DELETE_WINDOW", viz.destroy)

    def run(self):
        """Start the Tk event loop."""
        self.root.mainloop()

if __name__ == "__main__":
    MainScreen().run()
