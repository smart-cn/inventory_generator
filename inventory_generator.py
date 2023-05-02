import sys
import os
from typing import List

configs = {
    "masters": "1",
    "workers": "1",
    "etcd": "1",
    "nfs": "1",
    "calico": "",
    "total": "1",
    "file": "hosts.ini",
    "start_ip": "172.18.8.10"
}


def parse_args(arguments: List[str]):
    for arg in arguments:
        if "=" not in arg:
            raise ValueError(f"Invalid argument format: {arg}")
        key, value = arg.split("=")
        configs[key] = value


def generate_ips(ip: str, steps: int):
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


def parse_numbers(input_str: str):
    numbers = []
    if input_str:
        for part in input_str.split(','):  # split the input string by comma-separated parts
            if ':' in part:  # if the part contains a colon, it represents a range
                start, end = part.split(':')  # split the part into start and end values
                numbers += list(range(int(start), int(end) + 1))  # add the range of numbers to the numbers list
            elif '-' in part:  # if the part contains a minus, it represents a range
                start, end = part.split('-')  # split the part into start and end values
                numbers += list(range(int(start), int(end) + 1))  # add the range of numbers to the numbers list
            else:
                numbers.append(int(part))  # otherwise, parse the part as a single integer and add it to the list
    return numbers


def generate_nodes_list(input_str: str, total_nodes: int):
    nodes_list = []
    for item in parse_numbers(input_str):
        if item <= total_nodes:
            nodes_list.append(f"node{item}")
    return nodes_list


def generate_ansible_hosts(ip: str, steps: int):
    ips = generate_ips(ip, steps)  # get the list of IP addresses
    hosts = [f"node{i + 1} ansible_host={ip}" for i, ip in
             enumerate(ips)]  # generate a list of strings with ord. numbers
    return hosts


def generate_configfile(**kwargs):
    if os.path.isfile(kwargs['file']):
        print(f"Error: File {kwargs['file']} already exists.")
        sys.exit(1)
    with open(kwargs['file'], "w") as f:
        for ip in generate_ansible_hosts(kwargs['start_ip'], int(kwargs['total'])):
            f.write(f"{ip}\n")
        f.write(f"\n[kube_control_plane]\n")
        for node in generate_nodes_list(kwargs['masters'], kwargs['total']):
            f.write(f"{node}\n")
        f.write(f"\n[etcd]\n")
        for node in generate_nodes_list(kwargs['etcd'], kwargs['total']):
            f.write(f"{node}\n")
        f.write(f"\n[kube_node]\n")
        for node in generate_nodes_list(kwargs['workers'], kwargs['total']):
            f.write(f"{node}\n")
        f.write(f"\n[calico_rr]\n")
        for node in generate_nodes_list(kwargs['calico'], kwargs['total']):
            f.write(f"{node}\n")
        f.write(f"\n[k8s_cluster:children]\n")
        f.write(f"kube_control_plane\n")
        f.write(f"kube_node\n")
        f.write(f"calico_rr\n")


if __name__ == "__main__":
    try:
        args = sys.argv[1:]
        parse_args(args)
        generate_configfile(**configs)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)
