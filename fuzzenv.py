#!/usr/bin/python3

"""Simple env fuzzer."""

import json
import os
import signal
import socket
import sys

from argparse import ArgumentParser
from pathlib import Path
from threading import Thread

DEFAULT_LIBRARY = Path('./hook.so')
DEFAULT_UNIX_SOCK = Path('/tmp/fuzzsock')


def start_server(sockpath, config_path, envp):
    """Start the unix socket server."""
    try:
        sockpath.unlink()
    except OSError:
        pass

    var_map = {}

    if config_path is not None:
        with config_path.open() as fobj:
            for line in fobj:
                line = line.rstrip()
                (key, value) = line.split('=')
                var_map[key] = value

    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(bytes(sockpath))
    sock.listen(1)

    while True:
        conn = sock.accept()[0]
        data = conn.recv(1024).decode('utf-8')

        if data:
            try:
                resp = var_map[data]
            except KeyError:
                resp = 'A' * 10000

            envp[data] = resp
            conn.send(resp.encode('utf-8'))

        conn.shutdown(socket.SHUT_RDWR)
        conn.close()


def start_fuzzer(args):
    """Start the main fuzzer."""
    try:
        args.output_dir.mkdir()
    except FileExistsError as excep:
        pass

    env_map = {}

    server_thread = Thread(
        target=start_server,
        args=(args.unix_socket, args.config_file, env_map)
    )

    server_thread.daemon = True
    server_thread.start()

    child_pid = os.fork()

    if child_pid == 0:
        argv = [args.target_app.stem]
        argv.extend(args.target_args)

        envp = {
            'LD_PRELOAD': './' + str(args.library),
        }

        for entry in args.environment:
            (key, value) = entry.split('=')
            envp[key] = value

        os.closerange(0, 3)
        os.execve(str(args.target_app), argv, envp)
    else:
        status = os.waitpid(child_pid, 0)[1]

        signals = (
            signal.SIGILL.value,
            signal.SIGABRT.value,
            signal.SIGSEGV.value,
        )

        status -= 128

        if status in signals:
            print('PID {} crashed with signal {}'.format(child_pid, status))
            fname = args.output_dir / '{}'.format(child_pid)
            fname.write_text(json.dumps(env_map))

    return 0


def main(argv=sys.argv):
    """main."""
    parser = ArgumentParser(description='Environment variable fuzzer')

    parser.add_argument(
        '-v',
        '--verbose',
        action='store_true',
        help='Run in verbose mode'
    )

    parser.add_argument(
        '-l',
        '--library',
        action='store',
        type=Path,
        default=DEFAULT_LIBRARY,
        help='Library to inject into created processes'
    )

    parser.add_argument(
        '-u',
        '--unix-socket',
        action='store',
        type=Path,
        default=DEFAULT_UNIX_SOCK,
        help='Unix socket path'
    )

    parser.add_argument(
        '-e',
        '--environment',
        action='append',
        default=[],
        help='Extra vars to pass into app'
    )

    parser.add_argument(
        '-c',
        '--config-file',
        dest='config_file',
        action='store',
        default=None,
        type=Path,
        help='Config file for environment variables'
    )

    parser.add_argument(
        'output_dir',
        type=Path,
        help='Output for interesting fuzz cases'
    )

    parser.add_argument(
        'target_app',
        type=Path,
        help='Path to target application to fuzz'
    )

    parser.add_argument(
        'target_args',
        nargs='*',
        help='Arguments to pass to the target app'
    )

    args = parser.parse_args()
    start_fuzzer(args)
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
