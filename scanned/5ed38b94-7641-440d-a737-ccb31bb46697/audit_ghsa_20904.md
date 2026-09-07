# [M] TYPO3 CMS vulnerable to Cross-Site Scripting in <f:asset.css> view helper

## Summary
Severity: Medium
Advisory: GHSA-fv2m-9249-qx85
CVE: CVE-2022-36108
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-fv2m-9249-qx85
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=10.3.0 <10.4.32
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.16
- Packagist: `typo3/cms` — affected >=10.3.0 <10.4.32
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.16

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:C/C:L/I:L/A:N/E:F/RL:O/RC:C` (4.1)

### Problem
It has been discovered that the `f:asset.css` view helper is vulnerable to cross-site scripting when user input is passed as variables to the CSS. 

### Solution
Update to TYPO3 version 10.4.32 or 11.5.16 that fix the problem described above.

### Credits
Thanks to TYPO3 contributor member Frank Nägler who reported this issue and to TYPO3 core & security team member Oliver Hader who fixed the issue.

### References
* [TYPO3-CORE-SA-2022-010](https://typo3.org/security/advisory/typo3-core-sa-2022-010)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-fv2m-9249-qx85
- https://nvd.nist.gov/vuln/detail/CVE-2022-36108
- https://github.com/TYPO3/typo3/commit/6863f73818c36b0b88c677ba533765c8074907b4
- https://github.com/TYPO3/typo3/commit/c62e16fac031c270d9759c7261e504c7e25405df
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2022-36108.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-36108.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2022-010
