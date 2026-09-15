# [C] Koodo Reader: Remote code execution via malicious epub file

## Summary
Severity: Critical
Advisory: CVE-2026-55408
Aliases: GHSA-mjr7-w4jq-2rq9
CVSS: 9.0 (CVSS:4.0/AV:L/AC:L/AT:N/PR:N/UI:A/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-07-07
Source: https://osv.dev/vulnerability/CVE-2026-55408
Type: osv

## Details
Koodo Reader is an ebook reader. In version 2.3.0 and earlier, Koodo Reader is vulnerable to remote code execution through malicious EPUB files because the open-book IPC handler enables nodeIntegrationInSubFrames and EPUB chapter content is rendered with unsanitized innerHTML. An attacker can craft an EPUB book that, when imported and opened by the victim, instantiates a hidden iframe with Node.js API access and executes arbitrary operating system commands with the victim user's privileges. This issue is fixed in version 2.3.1.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/55xxx/CVE-2026-55408.json
- https://github.com/koodo-reader/koodo-reader/security/advisories/GHSA-mjr7-w4jq-2rq9
- https://nvd.nist.gov/vuln/detail/CVE-2026-55408
