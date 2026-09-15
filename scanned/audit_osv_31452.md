# [M] wcurl path traversal with percent-encoded slashes

## Summary
Severity: Medium
Advisory: CVE-2025-11563
CVSS: 4.6 (CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:L/I:L/A:N)
Published: 2026-02-25
Source: https://osv.dev/vulnerability/CVE-2025-11563
Type: osv

## Details
URLs containing percent-encoded slashes (`/` or `\`) can trick wcurl into
saving the output file outside of the current directory without the user
explicitly asking for it.

This flaw only affects the wcurl command line tool.

## References
- http://www.openwall.com/lists/oss-security/2025/11/04/1
- https://curl.se/docs/CVE-2025-11563.html
- https://curl.se/docs/CVE-2025-11563.json
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/11xxx/CVE-2025-11563.json
- https://lists.debian.org/debian-release/2025/11/msg00504.html
- https://nvd.nist.gov/vuln/detail/CVE-2025-11563
