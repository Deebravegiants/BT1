# [M] Whatsapp-Chat-Exporter has Cross-Site Scripting vulnerability in HTML output of chats.

## Summary
Severity: Medium
Advisory: GHSA-8c6x-g4fw-8rf4
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2023-07-10
Source: https://github.com/advisories/GHSA-8c6x-g4fw-8rf4
Type: github-advisory

## Affected
- PyPI: `Whatsapp-Chat-Exporter` — affected >=0 <0.9.5

## Details
### Impact
A Cross-Site Scripting (XSS) vulnerability was found in the HTML output of chats. XSS is intended to be mitigated by Jinja's escape function. However, `autoescape=True` was missing when setting the environment. Although the actual impact is low, considering the HTML file is being viewed offline, an adversary may still be able to inject malicious payloads into the chat through WhatsApp. All users are affected.

### Patches
The vulnerability is patched in 0.9.5. All users are strongly advised to update the exporter to the latest version.

### Workarounds
No workaround is available. Please update the exporter to the latest version.

### References
https://github.com/KnugiHK/WhatsApp-Chat-Exporter/commit/bfdc68cd6ad53ceecf132773f9aaba50dd80fe79
https://owasp.org/www-community/attacks/xss/

## References
- https://github.com/KnugiHK/WhatsApp-Chat-Exporter/security/advisories/GHSA-8c6x-g4fw-8rf4
- https://github.com/KnugiHK/WhatsApp-Chat-Exporter/commit/bfdc68cd6ad53ceecf132773f9aaba50dd80fe79
- https://github.com/KnugiHK/WhatsApp-Chat-Exporter
