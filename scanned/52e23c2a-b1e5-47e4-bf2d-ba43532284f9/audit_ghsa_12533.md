# [H] SQL injection when using MySQL/PostgreSQL data checking

## Summary
Severity: High
Advisory: GHSA-4c32-w6c7-77x4
CVE: CVE-2023-33967
CWE: CWE-89
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-4c32-w6c7-77x4
Type: github-advisory

## Affected
- Go: `github.com/megaease/easeprobe` — affected >=0 <2.1.0

## Details
An SQL injection issue was discovered in EaseProbe before 2.1.0 when using MySQL/PostgreSQL data checking. This problem has been fixed in v2.1.0; users should upgrade to this version.

The vulnerability was discovered by the [Oxeye research](https://www.oxeye.io/) team.

## References
- https://github.com/megaease/easeprobe/security/advisories/GHSA-4c32-w6c7-77x4
- https://nvd.nist.gov/vuln/detail/CVE-2023-33967
- https://github.com/megaease/easeprobe/pull/330
- https://github.com/megaease/easeprobe/commit/caaf5860df2aaa76acd29bc40ec9a578d0b1d6e1
- https://github.com/megaease/easeprobe
- https://github.com/megaease/easeprobe/releases/tag/v2.1.0
