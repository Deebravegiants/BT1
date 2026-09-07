# [H] Insecure Deserialization in Backend User Settings in TYPO3 CMS

## Summary
Severity: High
Advisory: GHSA-2wj9-434x-9hvp
CVE: CVE-2020-11067
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2020-05-13
Source: https://github.com/advisories/GHSA-2wj9-434x-9hvp
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.17
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.2
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.2
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.17

## Details
It has been discovered that backend user settings (in $BE_USER->uc) are vulnerable to insecure deserialization. In combination with vulnerabilities of 3rd party components this can lead to remote code execution. A valid backend user account is needed to exploit this vulnerability.

Update to TYPO3 versions 9.5.17 or 10.4.2 that fix the problem described.

### References
* https://typo3.org/security/advisory/typo3-core-sa-2020-005

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-2wj9-434x-9hvp
- https://nvd.nist.gov/vuln/detail/CVE-2020-11067
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2020-11067.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2020-11067.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2020-005
