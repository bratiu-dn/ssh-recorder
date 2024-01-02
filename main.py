import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk, ImageFont, ImageDraw
from write import SSHRecorder


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
        def entry_callback(*args):
            if self.text_var.get().strip():
                self.record_button['state'] = 'normal'
            else:
                self.record_button['state'] = 'disabled'
            self.update_button_image(self.record_button)

        self.root = root
        self.recorded_started = False
        self._recorder = None
        root.resizable(False, False)
        root.title("SSH Recorder")
        root.geometry("450x280")  # Adjust the size as needed
        root.configure(bg='white')

        # Use a modern theme
        style = ttk.Style()
        style.theme_use('clam')
        # Customize button style
        style.configure('TButton', borderwidth='0', background='white', foreground='white')
        style.map('TButton', background=[('active', 'gray90')])

        # Title Label
        original_image = Image.open("./DN-Logo.png")

        # Define the new size
        new_width = 150
        new_height = 30

        # Resize the image using the resize method
        resized_image = original_image.resize((new_width, new_height), Image.ANTIALIAS)

        # Convert the Image object to a PhotoImage object
        photo = ImageTk.PhotoImage(resized_image)

        self.picture_label = tk.Label(root, image=photo)
        self.picture_label.image = photo
        self.picture_label.grid(row=1, column=0, padx=20, pady=20)

        self.title_label = tk.Label(root, text="SSH Recorder", bg='white', fg='blue', font=('Helvetica', 25))
        self.title_label.grid(row=1, column=1, columnspan=2, pady=20)

        # Label for the Entry
        self.label = tk.Label(root, text="Jira ticket number:", bg='white', fg='gray30', font=('Helvetica', 20))
        self.label.grid(row=2, column=0, columnspan=2, padx=20, pady=20)

        # Text Box Entry
        self.text_var = tk.StringVar()
        self.text = tk.Entry(root, textvariable=self.text_var, font=('Helvetica', 20), width=10)
        self.text.grid(row=2, column=2, padx=20, pady=20)
        self.text_var.trace("w", entry_callback)

        # Buttons with icons and tooltips
        self.record_button = self.create_icon_button(root, '\uf8d9', self.start_resume_recording)
        ToolTip(self.record_button, 'Start recording')
        self.record_button.grid(row=3, column=0, padx=20, pady=20)
        entry_callback()

        self.pause_button = self.create_icon_button(root, '\uf04c', self.pause_recording, enabled=False)
        self.pause_button['state'] = 'disabled'
        ToolTip(self.pause_button, 'Pause recording')
        self.pause_button.grid(row=3, column=1, padx=20, pady=20)

        self.stop_button = self.create_icon_button(root, '\uf04d', self.stop_recording, enabled=False)
        self.stop_button['state'] = 'disabled'
        ToolTip(self.stop_button, 'Stop recording')
        self.stop_button.grid(row=3, column=2, padx=20, pady=20)

        # status text
        self.status_text = tk.StringVar()
        self.status_text.set("Status: Idle")
        self.status_label = tk.Label(root, textvariable=self.status_text, bg='white', fg='gray30',
                                     font=('Helvetica', 10))
        self.status_label.grid(row=4, column=0, columnspan=1, padx=20, pady=20, sticky=tk.W)


    @property
    def recorder(self):
        """
        get the SSHRecorder object
        :return:
        """
        if self._recorder is None:
            self._recorder = SSHRecorder()
        return self._recorder

    def create_icon_button(self, parent, icon_text, command=None, enabled=True):
        # Specify the relative path to your Font Awesome .otf file
        font_path = '/Users/bratiu/PycharmProjects/standalone-recorder/fontawesome-free-6.5.1-desktop/otfs/Font Awesome 6 Free-Solid-900.otf'

        # Create an image using PIL and set it on the button
        font = ImageFont.truetype(font_path, 28)
        image = Image.new('RGBA', (30, 30), (255, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), icon_text, font=font, fill="red")
        icon_enabled = ImageTk.PhotoImage(image)

        font = ImageFont.truetype(font_path, 28)
        image = Image.new('RGBA', (30, 30), (255, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        draw.text((0, 0), icon_text, font=font, fill="gray")
        icon_disabled = ImageTk.PhotoImage(image)

        button = ttk.Button(parent, image=icon_enabled if enabled else icon_disabled, command=command, style='TButton')
        # button = tk.Button(parent, image=icon, command=command)
        button.image_enabled = icon_enabled  # keep a reference!
        button.image_disabled = icon_disabled
        return button

    def update_button_image(self, button):
        if str(button['state']) == 'disabled':
            button.configure(image=button.image_disabled)
        else:
            button.configure(image=button.image_enabled)

    def start_resume_recording(self):
        """
        start/resume recording the SSH session
        :return:
        """
        if self.recorded_started:
            self.recorder.resume_recording()
        else:
            self.recorder.set_jira_ticket(self.text.get())
            self.recorder.start_recording()
            self.recorded_started = True
            self.text['state'] = 'disabled'
        self.record_button['state'] = 'disabled'
        self.pause_button['state'] = 'normal'
        self.stop_button['state'] = 'normal'
        self.update_button_image(self.pause_button)
        self.update_button_image(self.stop_button)
        self.update_button_image(self.record_button)
        self.status_text.set("Status: Recording")

    def pause_recording(self):
        """
        pause recording the SSH session
        :return:
        """
        self.recorder.pause_recording()
        self.record_button['state'] = 'normal'
        self.pause_button['state'] = 'disabled'
        self.update_button_image(self.pause_button)
        self.update_button_image(self.record_button)
        self.status_text.set("Status: Paused    ")

    def stop_recording(self):
        """
        stop recording the SSH session
        :return:
        """
        # Create a custom dialog
        self.dialog = tk.Toplevel(self.root)
        self.dialog.title("Stop Recording")

        # Dialog body
        tk.Label(self.dialog, text="Do you want to stop the recording and upload the results?").grid(row=0, column=0,
                                                                                                     columnspan=3,
                                                                                                     pady=10)

        # Button for "Stop and Upload to Jira"
        tk.Button(self.dialog, text="Stop and Upload to Jira",
                  command=self.confirm_stop_upload).grid(row=1, column=0, padx=10, pady=20)

        # Button for "Stop but Don't Upload"
        tk.Button(self.dialog, text="Stop but Don't Upload",
                  command=self.confirm_stop_no_upload).grid(row=1, column=1, padx=10, pady=20)

        # Button for "Cancel"
        tk.Button(self.dialog, text="Cancel",
                  command=self.cancel_stop).grid(row=1, column=2, padx=10, pady=20)

        # Make the dialog modal
        self.dialog.transient(self.root)
        self.dialog.grab_set()

        # Now that all widgets are added, we can start the modal loop
        self.root.wait_window(self.dialog)  # Wait for the dialog to be closed

    def confirm_stop_upload(self):
        """
        stop recording the SSH session and upload to jira
        :return:
        """
        self.confirm_stop_no_upload()
        # upload to jira

    def confirm_stop_no_upload(self):
        """
        stop recording the SSH session
        :return:
        """
        self.dialog.destroy()
        self.recorded_started = False
        self.recorder.stop_recording()
        self._recorder = None
        self.record_button['state'] = 'normal'
        self.pause_button['state'] = 'disabled'
        self.stop_button['state'] = 'disabled'
        self.update_button_image(self.pause_button)
        self.update_button_image(self.stop_button)
        self.update_button_image(self.record_button)
        self.text['state'] = 'normal'
        self.status_text.set("Status: Idle")

    def cancel_stop(self):
        self.dialog.destroy()


root = tk.Tk()
app = App(root)
root.mainloop()
