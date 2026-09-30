# [H] dpkg-deb: Fix cleanup for control member with restricted directories

## Summary
Severity: High
Advisory: CVE-2025-6297
CVSS: 8.2 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:N)
Published: 2025-07-01
Source: https://osv.dev/vulnerability/CVE-2025-6297
Type: osv

## Details
It was discovered that dpkg-deb does not properly sanitize directory permissions when extracting a control member into a temporary directory, which is
documented as being a safe operation even on untrusted data. This may result in leaving temporary files behind on cleanup. Given automated and repeated execution of dpkg-deb commands on
adversarial .deb packages or with well compressible files, placed
inside a directory with permissions not allowing removal by a non-root
user, this can end up in a DoS scenario due to causing disk quota
exhaustion or disk full conditions.

## References
- https://git.dpkg.org/cgit/dpkg/dpkg.git/commit/?id=ed6bbd445dd8800308c67236ba35d08004c98e82
- https://lists.debian.org/debian-lts-announce/2026/07/msg00015.html
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2025/6xxx/CVE-2025-6297.json
- https://nvd.nist.gov/vuln/detail/CVE-2025-6297
