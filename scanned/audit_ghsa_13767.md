# [M] Apache Superset Exposure of Sensitive Information to an Unauthorized Actor vulnerability

## Summary
Severity: Medium
Advisory: GHSA-fgpw-4w69-j256
CVE: CVE-2023-42505
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-11-28
Source: https://github.com/advisories/GHSA-fgpw-4w69-j256
Type: github-advisory

## Affected
- PyPI: `apache-superset` — affected >=0 <3.0.0

## Details
An authenticated user with read permissions on database connections metadata could potentially access sensitive information such as the connection's username.

This issue affects Apache Superset before 3.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-42505
- https://github.com/apache/superset
- https://lists.apache.org/thread/bd0fhtfzrtgo1q8x35tpm8ms144d1t2y
- http://www.openwall.com/lists/oss-security/2023/11/28/5
