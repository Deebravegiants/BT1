# [M] Denial of Service in Page Error Handling

## Summary
Severity: Medium
Advisory: GHSA-4p9g-qgx9-397p
CVE: CVE-2021-21359
CWE: CWE-405, CWE-674
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H/E:F/RL:O/RC:C (CVSS_V3)
Published: 2021-03-23
Source: https://github.com/advisories/GHSA-4p9g-qgx9-397p
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.25
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.14
- Packagist: `typo3/cms` — affected >=11.0.0 <11.1.1
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.25

## Details
> ### Meta
> * CVSS:  `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H/E:F/RL:O/RC:C` (5.5)
> * CWE-405, CWE-674
> * Status: **DRAFT**

### Problem
Requesting invalid or non-existing resources via HTTP triggers the page error handler which again could retrieve content  to be shown as error message from another page. This leads to a scenario in which the application is calling itself recursively - amplifying the impact of the initial attack until the limits of the web server are exceeded.

### Solution
Update to TYPO3 versions 9.5.25, 10.4.14, 11.1.1 that fix the problem described.

### Credits
Thanks to Paul Keller, Mathias Bolt Lesniak and Kay Strobach who reported this issue and to TYPO3 framework merger Frank Nägler and to TYPO3 security team member Torben Hansen who fixed the issue.

### References
* [TYPO3-CORE-SA-2021-005](https://typo3.org/security/advisory/typo3-core-sa-2021-005)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-4p9g-qgx9-397p
- https://nvd.nist.gov/vuln/detail/CVE-2021-21359
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-21359.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-21359.yaml
- https://packagist.org/packages/typo3/cms-core
- https://typo3.org/security/advisory/typo3-core-sa-2021-005
