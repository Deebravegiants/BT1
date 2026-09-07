# [M] TYPO3 is vulnerable to Mass Assignment in the Extension table administration library

## Summary
Severity: Medium
Advisory: GHSA-5fj8-wh3g-qvq2
CVE: CVE-2013-7080
Ecosystem: Packagist
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-5fj8-wh3g-qvq2
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=4.5.0 <4.5.31
- Packagist: `typo3/cms-core` — affected >=4.6.0 <4.7.16
- Packagist: `typo3/cms-core` — affected >=6.0.0 <6.0.11

## Details
The creating record functionality in Extension table administration library (feuser_adminLib.inc) in TYPO3 4.5.0 through 4.5.31, 4.7.0 through 4.7.16, and 6.0.0 through 6.0.11 allows remote attackers to write to arbitrary fields in the configuration database table via crafted links, aka "Mass Assignment."

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7080
- https://github.com/TYPO3-CMS/core
- http://seclists.org/oss-sec/2013/q4/473
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2013-004
- http://www.debian.org/security/2014/dsa-2834
