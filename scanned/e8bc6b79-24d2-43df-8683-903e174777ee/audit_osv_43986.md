# [C] Paperclip before 0.3.1 Remote Code Execution via DNS Rebinding

## Summary
Severity: Critical
Advisory: CVE-2026-77087
Aliases: GHSA-x8hx-rhr2-9rf7
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:P/VC:H/VI:H/VA:H/SC:H/SI:H/SA:H)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/CVE-2026-77087
Type: osv

## Details
Paperclip before 0.3.1 in default local_trusted mode fails to validate Host headers, allowing attackers to execute arbitrary commands via DNS rebinding. An attacker can craft a malicious webpage that, when visited by a developer running Paperclip locally, uses DNS rebinding to make authenticated API requests and execute commands through the process adapter.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/77xxx/CVE-2026-77087.json
- https://github.com/paperclipai/paperclip/security/advisories/GHSA-x8hx-rhr2-9rf7
- https://nvd.nist.gov/vuln/detail/CVE-2026-77087
- https://www.vulncheck.com/advisories/paperclip-before-remote-code-execution-via-dns-rebinding
