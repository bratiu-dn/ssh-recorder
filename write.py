import os
import shutil


class SSHRecorder:
    """
    Records the SSH sessions and saves then to files
    """

    def __init__(self):
        """
        initialize the SSHRecorder
        """
        self.sessions = []
        self.source_path = "/tmp/ssh_logs/"
        self.destination_path = ""
        self.jira_ticket = None
        self._existing_sessions = []
        self._new_sessions = []
        self._paused = False

    def set_jira_ticket(self, jira_ticket):
        """
        set the jira ticket number
        :param jira_ticket: the jira ticket number
        """
        self.jira_ticket = jira_ticket

    def start_recording(self):
        """
        start recording the SSH session
        :return:
        """
        print("creating the destination dir")

        self.destination_path = f"{self.source_path}{self.jira_ticket}/"
        shutil.rmtree(self.destination_path, ignore_errors=True)
        os.makedirs(self.destination_path)

        print("start recording!")
        print("get the existing files to ignore them")
        for file in os.listdir(self.source_path):
            if file.endswith(".log"):
                self._existing_sessions.append(file)

    def pause_recording(self):
        """
        pause recording the SSH session
        :return:
        """
        print("pause recording!")
        print("getting the list of new files")

        self._paused = True
        self._new_sessions = [f for f in os.listdir(self.source_path) if f.endswith(".log") and f not in self._existing_sessions]
        print(f"new sessions: {self._new_sessions}")
        for session in self._new_sessions:
            # copy the contents on top of the original file
            with open(f"{self.source_path}{session}", 'r') as source_file:
                with open(f"{self.destination_path}{session}", 'a') as destination_file:
                    destination_file.write(source_file.read())

    def resume_recording(self):
        """
        resume recording the SSH session
        :return:
        """
        self._paused = False
        print("resume recording!")
        for session in self._new_sessions:
            open(f"{self.source_path}{session}", 'w').close()

    def stop_recording(self):
        """
        stop recording the SSH session
        :return:
        """
        print("stop recording!")
        if not self._paused:
            self.pause_recording()
        print(f"Here is the list of files that were recorded: {self._new_sessions}")


if __name__ == '__main__':
    ssh_recorder = SSHRecorder()
    # start_recording = ssh_recorder.start_recording
    # pause_recording = ssh_recorder.pause_recording
    # resume_recording = ssh_recorder.resume_recording
