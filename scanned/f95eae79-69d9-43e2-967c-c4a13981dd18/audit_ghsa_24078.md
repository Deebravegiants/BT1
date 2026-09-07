# [H] TYPO3 Color Picker Wizard component allows remote authenticated editors to execute arbitrary PHP code

## Summary
Severity: High
Advisory: GHSA-55g3-fjwm-w2c8
CVE: CVE-2014-3942
CWE: CWE-94
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2022-05-14
Source: https://github.com/advisories/GHSA-55g3-fjwm-w2c8
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=4.5.0 <4.5.34
- Packagist: `typo3/cms` — affected >=4.7.0 <4.7.19
- Packagist: `typo3/cms` — affected >=6.0.0 <6.0.14
- Packagist: `typo3/cms` — affected >=6.1.0 <6.1.9

## Details
The Color Picker Wizard component in TYPO3 4.5.0 before 4.5.34, 4.7.0 before 4.7.19, 6.0.0 before 6.0.14, and 6.1.0 before 6.1.9 allows remote authenticated editors to execute arbitrary PHP code via a serialized PHP object.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2014-3942
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2014-001
- http://lists.opensuse.org/opensuse-updates/2014-06/msg00037.html
- http://www.debian.org/security/2014/dsa-2942
- http://www.openwall.com/lists/oss-security/2014/06/03/2
