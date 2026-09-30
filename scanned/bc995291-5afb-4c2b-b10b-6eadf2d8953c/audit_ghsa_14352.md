# [M] sqlparse contains a regular expression that is vulnerable to Regular Expression Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-rrm6-wvj7-cwh2
CVE: CVE-2023-30608
CWE: CWE-1333
Ecosystem: PyPI
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-04-21
Source: https://github.com/advisories/GHSA-rrm6-wvj7-cwh2
Type: github-advisory

## Affected
- PyPI: `sqlparse` — affected >=0.1.15 <0.4.4

## Details
### Impact
The SQL parser contains a regular expression that is vulnerable to [ReDoS](https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS) (Regular Expression Denial of Service). The vulnerability may lead to Denial of Service (DoS).

### Patches
This issues has been fixed in sqlparse 0.4.4.

### Workarounds
None. 

### References
This issue was discovered and reported by GHSL team member [@erik-krogh (Erik Krogh Kristensen)](https://github.com/erik-krogh).
- Commit that introduced the vulnerability: e75e35869473832a1eb67772b1adfee2db11b85a

## References
- https://github.com/andialbrecht/sqlparse/security/advisories/GHSA-rrm6-wvj7-cwh2
- https://nvd.nist.gov/vuln/detail/CVE-2023-30608
- https://github.com/andialbrecht/sqlparse/commit/c457abd5f097dd13fb21543381e7cfafe7d31cfb
- https://github.com/andialbrecht/sqlparse/commit/e75e35869473832a1eb67772b1adfee2db11b85a
- https://github.com/andialbrecht/sqlparse
- https://github.com/pypa/advisory-database/tree/main/vulns/sqlparse/PYSEC-2023-87.yaml
- https://lists.debian.org/debian-lts-announce/2023/05/msg00017.html
- https://lists.debian.org/debian-lts-announce/2024/12/msg00022.html
- https://owasp.org/www-community/attacks/Regular_expression_Denial_of_Service_-_ReDoS
