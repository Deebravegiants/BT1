# [H] CVE-2026-41113

## Summary
Severity: High
Advisory: CVE-2026-41113
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-04-16
Source: https://osv.dev/vulnerability/CVE-2026-41113
Type: osv

## Details
sagredo qmail before 2026.04.07 allows tls_quit remote code execution because of popen in notlshosts_auto in qmail-remote.c.

## References
- http://www.openwall.com/lists/oss-security/2026/04/18/5
- https://github.com/califio/publications/tree/main/MADBugs/qmail
- https://github.com/sagredo-dev/qmail/releases/tag/v2026.04.07
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/41xxx/CVE-2026-41113.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-41113
- https://github.com/sagredo-dev/qmail/commit/749f607f6885e3d01b36f2647d7a1db88f1ef741
- https://github.com/sagredo-dev/qmail/pull/42
- https://blog.calif.io/p/we-asked-claude-to-audit-sagredos
