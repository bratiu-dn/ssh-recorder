import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageFont, ImageDraw


class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0
        self.create_tooltip()

    def create_tooltip(self):
        self.widget.bind('<Enter>', self.show_tip)
        self.widget.bind('<Leave>', self.hide_tip)

    def show_tip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# Tkinter GUI with improved styling
class App:
    def __init__(self, root):
        self.root = root
        root.title("SSH Recorder")
        root.geometry("400x250")  # Adjust the size as needed
        root.configure(bg='darkblue')

        # Use a modern theme
        style = ttk.Style()
        style.theme_use('clam')

        # Title Label
        title_label = tk.Label(root, text="SSH Recorder", bg='darkblue', fg='gray30', font=('Helvetica', 30))
        title_label.pack(pady=(10, 5))

        # Customize button style
        style.configure('TButton', borderwidth='4', background='gray25', foreground='white')
        style.map('TButton', background=[('active', 'gray35')])

        # Label for the Entry
        label = tk.Label(root, text="Jira ticket number:", bg='darkblue', fg='white', font=('Helvetica', 25))
        label.pack(pady=(0, 5))

        # Text Box Entry
        self.text = ttk.Entry(root, font=('Helvetica', 25), width=30)
        self.text.pack(pady=(30, 5))

        # Buttons with icons and tooltips
        self.record_button = self.create_icon_button(root, '\uf8d9')
        ToolTip(self.record_button, 'Start recording')
        self.record_button.pack(side='left', expand=True)

        self.pause_button = self.create_icon_button(root, '\uf04c')
        ToolTip(self.pause_button, 'Pause recording')
        self.pause_button.pack(side='left', expand=True)

        self.stop_button = self.create_icon_button(root, '\uf04d')
        ToolTip(self.stop_button, 'Stop recording')
        self.stop_button.pack(side='left', expand=True)


    def create_icon_button(self, parent, icon_text, command=None):
        # Specify the relative path to your Font Awesome .otf file
        font_path = '/Users/bratiu/PycharmProjects/standalone-recorder/fontawesome-free-6.5.1-desktop/otfs/Font Awesome 6 Free-Solid-900.otf'

        # Create an image using PIL and set it on the button
        font = ImageFont.truetype(font_path, 30)
        image = Image.new('RGBA', (30, 30), (255, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), icon_text, font=font, fill="white")
        icon = ImageTk.PhotoImage(image)

        button = ttk.Button(parent, image=icon, command=command, style='TButton')
        button.image = icon  # keep a reference!
        button.pack(side='left', padx=5, pady=5)
        return button



root = tk.Tk()
app = App(root)
root.mainloop()
