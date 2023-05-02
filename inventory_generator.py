import sys
import os
from typing import List

configs = {
    "masters": "1",
    "workers": "1:10",
    "etcd": "1",
    "nfs": "1",
    "calico": "",
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


def generate_ips(ip: str, steps: int) -> List[str]:
    # Split the IP address into octets and convert each octet to an integer
    octets = [int(octet) for octet in ip.split(".")]
    # Convert the octets to a single integer
    start_ip = (octets[0] << 24) + (octets[1] << 16) + (octets[2] << 8) + octets[3]
    # Generate a list of `steps` IP addresses
    ips = []
    for i in range(start_ip, start_ip + steps):
        # Convert the integer IP address back to a string
        octet1 = (i >> 24) & 0xff
        octet2 = (i >> 16) & 0xff
        octet3 = (i >> 8) & 0xff
        octet4 = i & 0xff
        ips.append(f"{octet1}.{octet2}.{octet3}.{octet4}")
    return ips


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
