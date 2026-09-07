# [H] Tryton Directory Traversal vulnerability

## Summary
Severity: High
Advisory: GHSA-qjmc-wwmw-cq9r
CVE: CVE-2013-4510
CWE: CWE-22
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-qjmc-wwmw-cq9r
Type: github-advisory

## Affected
- PyPI: `trytond` — affected 3.0.0

## Details
Directory traversal vulnerability in the client in Tryton 3.0.0, as distributed before 20131104 and earlier, allows remote servers to write arbitrary files via path separators in the extension of a report.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-4510
- https://bugs.tryton.org/issue3446
- https://github.com/pypa/advisory-database/tree/main/vulns/tryton/PYSEC-2013-28.yaml
- http://hg.tryton.org/tryton/rev/357d0a4d9cb8
- http://www.debian.org/security/2013/dsa-2791
- http://www.openwall.com/lists/oss-security/2013/11/04/21
- http://www.tryton.org/posts/security-release-for-issue3446.html
