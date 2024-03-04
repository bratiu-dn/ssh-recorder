import os
import shutil
import subprocess
import time
from datetime import datetime
from contextlib import contextmanager
import paramiko
import logging
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
        logging.info("Creating Jira connection")
        USERNAME = 'dn-jira-auto01'
        PASSWORD = 'PGIs3QjCuouxFcbtUvaf27A1'

        jira_options = {
            'server': "https://drivenets.atlassian.net/",
        }

        self._jira = JIRA(options=jira_options, basic_auth=(USERNAME + '@drivenets.com', PASSWORD))

        yield self._jira

        logging.info("Closing Jira connection")
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
        logging.info("creating the destination dir")

        self.destination_path = f"{self.source_path}{self.jira_ticket}/"
        shutil.rmtree(self.destination_path, ignore_errors=True)
        os.makedirs(self.destination_path)

        logging.info("start recording!")
        logging.debug("get the existing files to ignore them")
        for file in os.listdir(self.source_path):
            if file.endswith(".log"):
                self._existing_sessions.append(file)

    def pause_recording(self):
        """
        pause recording the SSH session
        :return:
        """
        logging.info("pause recording!")
        logging.debug("getting the list of new files")

        self._paused = True
        self._new_sessions = [f for f in os.listdir(self.source_path) if f.endswith(".log") and f not in self._existing_sessions]
        logging.debug(f"new sessions: {self._new_sessions}")
        for session in self._new_sessions[:]:
            try:
                # copy the contents on top of the original file
                with open(f"{self.source_path}{session}", 'rb') as source_file:
                    with open(f"{self.destination_path}{session}", 'ab') as destination_file:
                        destination_file.write(source_file.read())
                # check if the file is zero bytes, remove it
                if os.path.getsize(f"{self.destination_path}{session}") == 0:
                    logging.debug("removing the file")
                    os.remove(f"{self.destination_path}{session}")
                    self._new_sessions.remove(session)
            except OSError as e:
                logging.error(f"Failed to copy file: {e}")

    def resume_recording(self):
        """
        resume recording the SSH session
        :return:
        """
        self._paused = False
        self._new_sessions = [f for f in os.listdir(self.source_path) if f.endswith(".log") and f not in self._existing_sessions]
        logging.info("resume recording!")
        for session in self._new_sessions:
            open(f"{self.source_path}{session}", 'w').close()

    def stop_recording(self):
        """
        stop recording the SSH session
        :return:
        """
        logging.info("stop recording!")
        if not self._paused:
            self.pause_recording()
        logging.info(f"Here is the list of files that were recorded: {self._new_sessions}")

    def call_show_system_end(self):
        """
        Call the show system end on all the devices
        :return:
        """
        logging.info("calling show system end on all devices")
        devices = [session for session in self._new_sessions if '_dn_' in session and 'pass' not in session]
        if not devices:
            return
        for device in devices:
            logging.debug(f"Calling show system end on {device}")
            userhost = device.split("_")[0]
            user, host = userhost.split("@")
            with open(f'{self.destination_path}pass_{device}') as fp:
                password = fp.read().rstrip()

            # Command to execute
            command = 'show system | no-more'

            # Create an SSH client instance
            client = paramiko.SSHClient()

            # Automatically add untrusted hosts (make sure okay for security policy)
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                client.connect(host, 22, user, password, timeout=60, banner_timeout=60)
                client._transport.window_size = 2147483647
                # Invoke an interactive shell session
                shell = client.invoke_shell(width=1500, height=1000)
                time.sleep(15)  # Wait a bit for the initial prompt
                # Clear any welcome messages or prompts
                if shell.recv_ready():
                    shell.recv(65535)
                # Send the command
                shell.send(command + "\n")
                time.sleep(5)  # Adjust this sleep time as necessary to allow command execution
                # Capture the command output
                output = ""
                while shell.recv_ready():
                    buffer = shell.recv(65535)
                    output += buffer.decode('utf-8')
                    time.sleep(1)  # Adjust as necessary based on testing

                logging.debug("\nGot show system\n\n\n")
                logging.debug(output)

                with open(f"{self.destination_path}/{device}", "a") as f:
                    f.write("# Final show system\n")
                    f.write(output)
            except Exception as e:
                logging.warning(f"Failed to call show system end on {device} due to {e}")
                continue
            finally:
                # Close the SSH connection
                client.close()

    def upload_to_jira(self):
        """
        Upload the recordings to Jira
        :return name of the file uploaded or None if nothing was uploaded
        """

        clean_script = "LC_ALL=C tr -d '\\000' < {0} | perl -0777 -pe 's/\\e\\[[0-9;?]*[nmlhHfGJKF]//g; s/.\\x08//g while /\\x08/' > {0}.txt"
        # do nothing if there are no files to upload
        if not self._new_sessions:
            return

        # need to call the show system on all devices before uploading the logs
        self.call_show_system_end()

        all_files = [f for f in os.listdir(self.destination_path)]
        for f in all_files:
            os.system(clean_script.format(f"{self.destination_path}{f}"))
        # Update the list of files to include the new txt files
        all_files = [f for f in os.listdir(self.destination_path)]
        # Filter files to exclude any that contain "pass" in their name and are .txt files
        files_to_zip = [file for file in all_files if "pass" not in file and file.endswith('.txt')]
        files_to_zip_str = " ".join(f'"{self.destination_path}{file}"' for file in files_to_zip)

        # zip all the txt files
        date = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"{self.destination_path}{date}-logs.zip"
        os.system(f"zip -j {filename} {files_to_zip_str}")

        # attach the zip file to the jira ticket
        retries = 3
        exception = None
        for i in range(1, retries + 1):
            try:
                with self.jira() as jira:
                    jira.add_attachment(issue=self.jira_ticket, attachment=filename)
                    break
            except Exception as e:
                logging.warning(f"Failed to upload the file to Jira, retrying {i}/{retries}")
                exception = e
                time.sleep(1)
                continue
        else:
            logging.error(f"Failed to upload the file to Jira after {retries} retries")
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
    filename = "source.log"
    clean_script = "LC_ALL=C tr -d '\\000' < {0} | perl -0777 -pe 's/\\e\\[[0-9;?]*[nmlhHfGJKF]//g; s/.\\x08//g while /\\x08/' > {0}.txt"
    os.system(clean_script.format("source.log"))
