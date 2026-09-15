# [M] CRLF injection in urllib3

## Summary
Severity: Medium
Advisory: GHSA-wqvq-5m8c-6g24
CVE: CVE-2020-26137
CWE: CWE-74
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2021-06-18
Source: https://github.com/advisories/GHSA-wqvq-5m8c-6g24
Type: github-advisory

## Affected
- PyPI: `urllib3` — affected >=0 <1.25.9

## Details
urllib3 before 1.25.9 allows CRLF injection if the attacker controls the HTTP request method, as demonstrated by inserting CR and LF control characters in the first argument of `putrequest()`. NOTE: this is similar to CVE-2020-26116.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-26137
- https://github.com/urllib3/urllib3/pull/1800
- https://github.com/urllib3/urllib3/commit/1dd69c5c5982fae7c87a620d487c2ebf7a6b436b
- https://bugs.python.org/issue39603
- https://github.com/pypa/advisory-database/tree/main/vulns/urllib3/PYSEC-2020-148.yaml
- https://github.com/urllib3/urllib3
- https://lists.debian.org/debian-lts-announce/2021/06/msg00015.html
- https://lists.debian.org/debian-lts-announce/2023/10/msg00012.html
- https://usn.ubuntu.com/4570-1
- https://www.oracle.com/security-alerts/cpujul2022.html
- https://www.oracle.com/security-alerts/cpuoct2021.html
