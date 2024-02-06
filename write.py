import os
import shutil
import time
from datetime import datetime
from contextlib import contextmanager

from jira import JIRA

SOURCE_PATH = "/tmp/ssh_logs/"


class SSHRecorder:
    """
    Records the SSH sessions and saves then to files
    """

    def __init__(self):
        """
        initialize the SSHRecorder
        """
        self.sessions = []
        self.source_path = SOURCE_PATH
        self.destination_path = ""
        self.jira_ticket = None
        self._existing_sessions = []
        self._new_sessions = []
        self._paused = False
        self._jira = None

    @contextmanager
    def jira(self):
        """
        get the jira object
        :return: the jira object
        """
        print("Creating Jira connection")
        USERNAME = 'dn-jira-auto01'
        PASSWORD = 'PGIs3QjCuouxFcbtUvaf27A1'

        jira_options = {
            'server': "https://drivenets.atlassian.net/",
        }

        self._jira = JIRA(options=jira_options, basic_auth=(USERNAME + '@drivenets.com', PASSWORD))

        yield self._jira

        print("Closing Jira connection")
        self._jira.close()
        self._jira = None

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
        for session in self._new_sessions[:]:
            try:
                # copy the contents on top of the original file
                with open(f"{self.source_path}{session}", 'r', encoding='utf-8') as source_file:
                    with open(f"{self.destination_path}{session}", 'a', encoding='utf-8') as destination_file:
                        destination_file.write(source_file.read())
            except UnicodeDecodeError:
                print(f"Failed to decode the file {session}, so skipping it")
                # check if the file is zero bytes, remove it
                if os.path.getsize(f"{self.destination_path}{session}") == 0:
                    print("removing the file")
                    os.remove(f"{self.destination_path}{session}")
                    self._new_sessions.remove(session)

    def resume_recording(self):
        """
        resume recording the SSH session
        :return:
        """
        self._paused = False
        self._new_sessions = [f for f in os.listdir(self.source_path) if f.endswith(".log") and f not in self._existing_sessions]
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

    def upload_to_jira(self):
        """
        Upload the recordings to Jira
        :return name of the file uploaded or None if nothing was uploaded
        """
        clean_script = "tr -d '\\000' < {0} | perl -0777 -pe 's/\\e\\[[0-9;?]*[nmlhHfGJKF]//g; s/.\\x08//g while /\\x08/' > {0}.txt"
        # do nothing if there are no files to upload
        if not self._new_sessions:
            return
        for f in [f for f in os.listdir(self.destination_path)]:
            os.system(clean_script.format(f"{self.destination_path}{f}"))

        # zip all the txt files
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.destination_path}{date}-logs.zip"
        os.system(f"zip -j {filename} {self.destination_path}*.txt")

        # attach the zip file to the jira ticket
        retries = 3
        exception = None
        for i in range(1, retries + 1):
            try:
                with self.jira() as jira:
                    jira.add_attachment(issue=self.jira_ticket, attachment=filename)
                    break
            except Exception as e:
                print(f"Failed to upload the file to Jira, retrying {i}/{retries}")
                exception = e
                time.sleep(1)
                continue
        else:
            print(f"Failed to upload the file to Jira after {retries} retries")
            if exception:
                raise exception  # Re-raise the original exception
        return filename

    def validate_jira_ticket(self, ticket_id):
        """
        Validate the Jira ticket
        """
        try:
            with self.jira() as jira:
                jira.issue(ticket_id)
                self.set_jira_ticket(ticket_id)
                return True
        except:
            return False


if __name__ == '__main__':
    ssh_recorder = SSHRecorder()
    # start_recording = ssh_recorder.start_recording
    # pause_recording = ssh_recorder.pause_recording
    # resume_recording = ssh_recorder.resume_recording
