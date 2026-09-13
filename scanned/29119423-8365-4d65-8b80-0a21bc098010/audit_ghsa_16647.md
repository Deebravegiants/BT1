# [C] PyMySQL SQL Injection vulnerability

## Summary
Severity: Critical
Advisory: GHSA-v9hf-5j83-6xpp
CVE: CVE-2024-36039
CWE: CWE-89
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-05-21
Source: https://github.com/advisories/GHSA-v9hf-5j83-6xpp
Type: github-advisory

## Affected
- PyPI: `pymysql` — affected >=0 <1.1.1

## Details
PyMySQL through 1.1.0 allows SQL injection if used with untrusted JSON input because keys are not escaped by `escape_dict`.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-36039
- https://github.com/PyMySQL/PyMySQL/commit/521e40050cb386a499f68f483fefd144c493053c
- https://github.com/PyMySQL/PyMySQL
- https://github.com/PyMySQL/PyMySQL/releases/tag/v1.1.1
- https://lists.debian.org/debian-lts-announce/2024/05/msg00017.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/23VXBV34GFRICCVYZ6KFMSSWY5UEXCF5
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/35VOJS3SRJNLQIO7YTZFNM6RWHIHWTMK
