# [M] Cross-Site Scripting in TYPO3 CMS Form Engine

## Summary
Severity: Medium
Advisory: GHSA-43gj-mj2w-wh46
CVE: CVE-2020-11064
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-05-13
Source: https://github.com/advisories/GHSA-43gj-mj2w-wh46
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.17
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.2
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.2
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.17

## Details
In TYPO3 CMS greater than or equal to 9.0.0 and less than 9.5.17 and greater than or equal to 10.0.0 and less than 10.4.2, it has been discovered that HTML `placeholder` attributes containing data of other database records are vulnerable to cross-site scripting. A valid backend user account is needed to exploit this vulnerability.

Update to TYPO3 versions 9.5.17 or 10.4.2 that fix the problem described.

### References
* https://typo3.org/security/advisory/typo3-core-sa-2020-002

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-43gj-mj2w-wh46
- https://nvd.nist.gov/vuln/detail/CVE-2020-11064
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2020-11064.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2020-11064.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2020-002
