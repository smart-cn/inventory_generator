import sys
import os

configs = {
    "masters": "1",
    "workers": "",
    "etcd": "1",
    "nfs": "1",
    "total": 1,
    "file": "hosts.ini",
    "start_ip": "172.18.8.10"
}


def parse_args(arguments):
    for arg in arguments:
        if "=" not in arg:
            raise ValueError(f"Invalid argument format: {arg}")
        key, value = arg.split("=")
        configs[key] = value


def generate_configfile(**kwargs):
    filename = kwargs["file"]
    if os.path.isfile(filename):
        print(f"Error: File {filename} already exists.")
        sys.exit(1)
    with open(filename, "w") as f:
        for key, value in kwargs.items():
            f.write(f"{key}: {value}\n")


if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        parse_args(args)
        generate_configfile(**configs)
    except Exception as e:
        print(f"Error: {str(e)}")
