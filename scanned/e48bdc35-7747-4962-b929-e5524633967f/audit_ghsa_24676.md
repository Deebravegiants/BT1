# [M] Roundup sensitive data disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-j556-q367-2gw6
CVE: CVE-2014-6276
CWE: CWE-200
Ecosystem: PyPI
CVSS: CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-j556-q367-2gw6
Type: github-advisory

## Affected
- PyPI: `roundup` — affected >=0 <1.5.1

## Details
schema.py in Roundup before 1.5.1 does not properly limit attributes included in default user permissions, which might allow remote authenticated users to obtain sensitive user information by viewing user details.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-6276
- https://github.com/pypa/advisory-database/tree/main/vulns/roundup/PYSEC-2016-33.yaml
- https://github.com/roundup-tracker/roundup
- https://sourceforge.net/p/roundup/code/ci/tip/tree/CHANGES.txt
- http://hg.code.sf.net/p/roundup/code/rev/a403c29ffaf9
- http://www.debian.org/security/2016/dsa-3502
