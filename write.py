import shutil

source_path = '/Users/bratiu/ssh_logs/ssh_session_20231229_103625.log'
destination_path = '/Users/bratiu/ssh_logs/ssh_session_final.log'


def start_recording():
    print("start recording!")
    open(destination_path, 'w').close()
    open(source_path, 'w').close()


def pause_recording():
    print("pause recording!")
    # copy the contents on top of the original file
    with open(source_path, 'r') as source_file:
        with open(destination_path, 'a') as destination_file:
            destination_file.write(source_file.read())


def resume_recording():
    print("resume recording!")
    open(source_path, 'w').close()


if __name__ == '__main__':
    # start_recording()
    pause_recording()
    # resume_recording()
