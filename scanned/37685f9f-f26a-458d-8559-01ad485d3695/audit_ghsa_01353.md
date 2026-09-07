# [H] Heap Overflow in PyMiniRacer

## Summary
Severity: High
Advisory: GHSA-vwcg-7xqw-qcxw
CVE: CVE-2020-25489
CWE: CWE-119
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-09-18
Source: https://github.com/advisories/GHSA-vwcg-7xqw-qcxw
Type: github-advisory

## Affected
- PyPI: `py-mini-racer` — affected >=0 <0.3.0

## Details
A heap overflow in Sqreen PyMiniRacer (aka Python Mini Racer) before 0.3.0 allows remote attackers to potentially exploit heap corruption.

More details on https://blog.sqreen.com/vulnerability-disclosure-finding-a-vulnerability-in-sqreens-php-agent-and-how-we-fixed-it/.

## References
- https://github.com/sqreen/PyMiniRacer/security/advisories/GHSA-vwcg-7xqw-qcxw
- https://nvd.nist.gov/vuln/detail/CVE-2020-25489
- https://github.com/sqreen/PyMiniRacer/commit/627b54768293ec277f1adb997c888ec524f4174d
- https://blog.sqreen.com/vulnerability-disclosure-finding-a-vulnerability-in-sqreens-php-agent-and-how-we-fixed-it
- https://github.com/pypa/advisory-database/tree/main/vulns/py-mini-racer/PYSEC-2020-93.yaml
- https://github.com/sqreen/PyMiniRacer
- https://github.com/sqreen/PyMiniRacer/compare/v0.2.0...v0.3.0
