# [M] Improper Neutralization of Input During Web Page Generation ('Cross-site Scripting') in typo3/cms-form

## Summary
Severity: Medium
Advisory: GHSA-x79j-wgqv-g8h2
CVE: CVE-2021-21358
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N/E:F/RL:O/RC:C (CVSS_V3)
Published: 2021-03-23
Source: https://github.com/advisories/GHSA-x79j-wgqv-g8h2
Type: github-advisory

## Affected
- Packagist: `typo3/cms-form` — affected >=10.2.0 <10.4.14
- Packagist: `typo3/cms-form` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms` — affected >=11.0.0 <11.1.1

## Details
### Problem
It has been discovered that the Form Designer backend module of the Form Framework is vulnerable to cross-site scripting. A valid backend user account with access to the form module is needed to exploit this vulnerability.

### Solution
Update to TYPO3 versions 10.4.14 or 11.1.1 that fix the problem described.

### Credits
Thanks to Richie Lee who reported this issue and to TYPO3 framework merger Andreas Fernandez who fixed the issue.

### References
* [TYPO3-CORE-SA-2021-004](https://typo3.org/security/advisory/typo3-core-sa-2021-004)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-x79j-wgqv-g8h2
- https://nvd.nist.gov/vuln/detail/CVE-2021-21358
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-21358.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-21358.yaml
- https://packagist.org/packages/typo3/cms-form
- https://typo3.org/security/advisory/typo3-core-sa-2021-004
