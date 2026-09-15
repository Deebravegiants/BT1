# [C] OpenBullet2 0.3.2 Path Traversal via Wordlist Endpoint

## Summary
Severity: Critical
Advisory: CVE-2026-25559
CVSS: 9.0 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N)
Published: 2026-06-08
Source: https://osv.dev/vulnerability/CVE-2026-25559
Type: osv

## Details
OpenBullet2 through version 0.3.2 contains a path traversal vulnerability in the wordlist endpoint that allows authenticated attackers to perform arbitrary file read, write, and delete operations by supplying unsanitized absolute paths to the upload handler and wordlist functions. Attackers can chain the file write and delete primitives to achieve remote code execution by manipulating critical system files such as /etc/passwd, with full system impact since the application runs as root by default.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/25xxx/CVE-2026-25559.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-25559
- https://www.vulncheck.com/advisories/openbullet2-path-traversal-via-wordlist-endpoint
- https://github.com/openbullet/openbullet2
- https://hackernoon.com/one-empty-header-to-admin-how-an-auth-bypass-breaks-openbullet2
