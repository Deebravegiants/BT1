# [M] TYPO3 vulnerable to Information Disclosure via Content Editing Wizards component

## Summary
Severity: Medium
Advisory: GHSA-4rpv-g4gq-rh4m
CVE: CVE-2013-7073
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-05-17
Source: https://github.com/advisories/GHSA-4rpv-g4gq-rh4m
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.32
- Packagist: `typo3/cms` — affected >=4.7.0 <4.7.17
- Packagist: `typo3/cms` — affected >=6.0.0 <6.0.12
- Packagist: `typo3/cms` — affected >=6.1.0 <6.1.7

## Details
The Content Editing Wizards component in TYPO3 4.5.0 through 4.5.31, 4.7.0 through 4.7.16, 6.0.0 through 6.0.11, and 6.1.0 through 6.1.6 does not check permissions, which allows remote authenticated editors to read arbitrary TYPO3 table columns via unspecified parameters.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2013-7073
- https://github.com/TYPO3/typo3
- http://lists.opensuse.org/opensuse-security-announce/2016-08/msg00028.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00083.html
- http://lists.opensuse.org/opensuse-updates/2016-08/msg00106.html
- http://seclists.org/oss-sec/2013/q4/473
- http://seclists.org/oss-sec/2013/q4/487
- http://typo3.org/teams/security/security-bulletins/typo3-core/typo3-core-sa-2013-004
- http://www.debian.org/security/2014/dsa-2834
