# [C] SQL injection without credentials in ming-soft MCMS

## Summary
Severity: Critical
Advisory: GHSA-h3hw-g4hm-7gr4
CVE: CVE-2020-23262
CWE: CWE-89
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-02-09
Source: https://github.com/advisories/GHSA-h3hw-g4hm-7gr4
Type: github-advisory

## Affected
- Maven: `net.mingsoft:ms-mcms` — affected >=0 <5.1

## Details
An issue was discovered in ming-soft MCMS v5.0, where a malicious user can exploit SQL injection without logging in through /mcms/view.do.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-23262
- https://github.com/ming-soft/MCMS/issues/45
