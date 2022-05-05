import subprocess

# from IPython.display import clear_output,display


def run_command(command, split=True):
    """Downloaded a file from the internet.

    :param command: _description_
    :type command: _type_
    :param split: _description_, defaults to True
    :type split: bool, optional
    :param command: _description_
    """
    if split:
        command = list(command.split())
    process = subprocess.Popen(
        command,
        bufsize=1,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        encoding="utf-8",
    )
    while True:
        realtime_output = process.stdout.readline()
        if realtime_output == "" and process.poll() is not None:
            break
        if realtime_output:
            x = realtime_output.strip()
            print(x)
