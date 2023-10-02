#!/usr/bin/env python3

# script to limit io of lxc instance
# usage: put this file to /usr/bin/limit_io.py, chmod u+x /usr/bin/limit_io.py
# then, add following to crontab
# SHELL=/bin/bash
# PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin
# *       *       *       *       *       flock -xn /tmp/limit_io.lock -c "/usr/lib/limit_io.py  300 200" &>> /var/log/limit_io.log

import subprocess
import time
import sys


def get_container_io_stats(container_name):
    io_stats_file = f"/sys/fs/cgroup/lxc.payload.{container_name}/io.stat"

    try:
        with open(io_stats_file, 'r') as f:
            stats = f.readline().strip()
            return stats
    except FileNotFoundError:
        return None


def extract_value_from_stats(stats, key):
    value = "-"
    try:
        value = int(stats.split(f" {key}=")[1].split()[0])
    except (IndexError, ValueError):
        pass
    return value


def calculate_rate(initial_value, final_value, interval):
    if initial_value == "-" or final_value == "-":
        return "-"
    return (final_value - initial_value) // interval


def stop_container(container_name):
    subprocess.run(["lxc", "stop", "-f", container_name])


def print_colored(text, color):
    colors = {
        "white_bold": "\033[1;97m",
        "reset": "\033[0m"
    }
    print(f"{colors[color]}{text}{colors['reset']}")


# 获取所有容器的名称
container_names = subprocess.check_output(["lxc", "list", "--format", "csv", "-c", "n"]).decode().strip().split("\n")

# 获取命令行参数
if len(sys.argv) != 3:
    print("Please provide sleep time and iops limit as arguments")
    print("Example: python3 monitor_io.py 5 1000")
    sys.exit(1)

sleep_time = int(sys.argv[1])
iops_threshold = int(sys.argv[2])

# 获取初始IO统计信息
initial_stats = {}
for container_name in container_names:
    stats = get_container_io_stats(container_name)
    if stats:
        initial_stats[container_name] = stats

# 休眠一段时间
time.sleep(sleep_time)

# 获取最终IO统计信息
final_stats = {}
for container_name in container_names:
    stats = get_container_io_stats(container_name)
    if stats:
        final_stats[container_name] = stats

# 分别计算每个实例的IO速率
# print_colored("容器\t读取速率\t写入速率\t读取操作速率\t写入操作速率", "white_bold")
print_colored("container\tread rate\twrite rate\tread iops\twrite iops", "white_bold")
for container_name in container_names:
    if container_name in initial_stats and container_name in final_stats:
        initial_io_stats = initial_stats[container_name]
        final_io_stats = final_stats[container_name]

        initial_read_bytes = extract_value_from_stats(initial_io_stats, "rbytes")
        initial_write_bytes = extract_value_from_stats(initial_io_stats, "wbytes")
        initial_read_ops = extract_value_from_stats(initial_io_stats, "rios")
        initial_write_ops = extract_value_from_stats(initial_io_stats, "wios")

        final_read_bytes = extract_value_from_stats(final_io_stats, "rbytes")
        final_write_bytes = extract_value_from_stats(final_io_stats, "wbytes")
        final_read_ops = extract_value_from_stats(final_io_stats, "rios")
        final_write_ops = extract_value_from_stats(final_io_stats, "wios")

        read_bytes_per_sec = calculate_rate(initial_read_bytes, final_read_bytes, sleep_time)
        write_bytes_per_sec = calculate_rate(initial_write_bytes, final_write_bytes, sleep_time)
        read_ops_per_sec = calculate_rate(initial_read_ops, final_read_ops, sleep_time)
        write_ops_per_sec = calculate_rate(initial_write_ops, final_write_ops, sleep_time)

        print(f"{container_name}\t{read_bytes_per_sec}\t{write_bytes_per_sec}\t{read_ops_per_sec}\t{write_ops_per_sec}")

        # 判断是否超过阈值，超过则停止实例
        if (read_ops_per_sec != "-" and read_ops_per_sec > iops_threshold) or (write_ops_per_sec != "-" and write_ops_per_sec > iops_threshold):
            print_colored(f"container{container_name} read iops is over {iops_threshold}, will be force stopped", "white_bold")
            stop_container(container_name)
    else:
        print_colored(f"{container_name}\t-\t-\t-\t-", "white_bold")
