# [C] Typo3 SQL injection due to faulty prepared statements

## Summary
Severity: Critical
Advisory: GHSA-gx4p-6w86-f8jx
CVE: CVE-2011-3583
CWE: CWE-89
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-04-22
Source: https://github.com/advisories/GHSA-gx4p-6w86-f8jx
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.5.0

## Details
It was found that Typo3 Core versions 4.5.0 - 4.5.5 uses prepared statements that, if the parameter values are not properly replaced, could lead to a SQL Injection vulnerability. This issue can only be exploited if two or more parameters are bound to the query and at least two come from user input.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2011-3583
- https://access.redhat.com/security/cve/cve-2011-3583
- https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=641682
- https://github.com/TYPO3/typo3
- https://security-tracker.debian.org/tracker/CVE-2011-3583
- https://typo3.org/security/advisory/typo3-core-sa-2011-002
