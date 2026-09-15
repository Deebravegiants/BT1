# [C] BEdita vulnerable to SQL injection

## Summary
Severity: Critical
Advisory: GHSA-9gv2-2m38-j6cx
CVE: CVE-2019-15570
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-9gv2-2m38-j6cx
Type: github-advisory

## Affected
- Packagist: `bedita/bedita` — affected >=0 <4.0.0

## Details
BEdita through 4.0.0-RC2 allows SQL injection during a save operation for a relation with parameters due to a lack of JSON escaping.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2019-15570
- https://github.com/bedita/bedita/pull/1608
- https://github.com/bedita/bedita/commit/0ddcd46d645c773e69369f3ed82c865a4d098454
- https://github.com/bedita/bedita
