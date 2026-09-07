# [M] Open WebUI Vulnerable to Cross-Site Scripting (XSS) via Chat File Upload

## Summary
Severity: Medium
Advisory: GHSA-j274-m559-cj4j
CVE: CVE-2024-7044
CWE: CWE-79
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:R/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-03-20
Source: https://github.com/advisories/GHSA-j274-m559-cj4j
Type: github-advisory

## Affected
- PyPI: `open-webui` — affected >=0

## Details
A Stored Cross-Site Scripting (XSS) vulnerability exists in the chat file upload functionality of open-webui/open-webui version 0.3.8. An attacker can inject malicious content into a file, which, when accessed by a victim through a URL or shared chat, executes JavaScript in the victim's browser. This can lead to user data theft, session hijacking, malware distribution, and phishing attacks.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-7044
- https://github.com/open-webui/open-webui
- https://huntr.com/bounties/c25a885c-d6e2-4169-9ee8-4d33bcbb5ef6
