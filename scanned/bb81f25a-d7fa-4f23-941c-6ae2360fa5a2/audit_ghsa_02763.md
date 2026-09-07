# [M] Cross-Site Scripting in Query Generator & Query View

## Summary
Severity: Medium
Advisory: GHSA-6mh3-j5r5-2379
CVE: CVE-2021-32668
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-07-22
Source: https://github.com/advisories/GHSA-6mh3-j5r5-2379
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.41
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.28
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.18
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.3.1
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.18
- Packagist: `typo3/cms` — affected >=11.0.0 <11.3.1
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.28

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:H/UI:R/S:C/C:L/I:L/A:N/E:F/RL:O/RC:C` (4.5)

### Problem
Failing to properly encode error messages, the components _QueryGenerator_ and _QueryView_ are vulnerable to both reflected and persistent cross-site scripting. A valid backend user account having administrator privileges is needed to exploit this vulnerability.

### Solution
Update to TYPO3 versions 8.7.41 ELTS, 9.5.28, 10.4.18, 11.3.1 that fix the problem described.

### Credits
Thanks to Richie Lee who reported this issue and to TYPO3 security team member Oliver Hader who fixed the issue.

### References
* [TYPO3-CORE-SA-2021-010](https://typo3.org/security/advisory/typo3-core-sa-2021-010)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-6mh3-j5r5-2379
- https://github.com/TYPO3/typo3/security/advisories/GHSA-6mh3-j5r5-2379
- https://nvd.nist.gov/vuln/detail/CVE-2021-32668
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-32668.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-32668.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2021-010
