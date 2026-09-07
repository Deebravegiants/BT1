# [M] TYPO3 CMS Stored Cross-Site Scripting via FileDumpController

## Summary
Severity: Medium
Advisory: GHSA-9c6w-55cp-5w25
CVE: CVE-2022-36107
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-9c6w-55cp-5w25
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=7.0.0 <7.6.58
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.48
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.37
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.32
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.16
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.32
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.16

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N/E:F/RL:O/RC:C` (5.0)

### Problem
It has been discovered that the `FileDumpController` (backend and frontend context) is vulnerable to cross-site scripting when malicious files are displayed using this component. A valid backend user account is needed to exploit this vulnerability.

### Solution
Update to TYPO3 version 7.6.58 ELTS, 8.7.48 ELTS, 9.5.37 ELTS, 10.4.32 or 11.5.16 that fix the problem described above.

### Credits
Thanks to Vautia who reported this issue and to TYPO3 core & security team member Oliver Hader who fixed the issue.

### References
* [TYPO3-CORE-SA-2022-009](https://typo3.org/security/advisory/typo3-core-sa-2022-009)
* [Vulnerability Report on huntr.dev](https://huntr.dev/bounties/51e9b709-193c-41fd-bd4a-833aaca0bd4e/) (embargoed +30 days)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-9c6w-55cp-5w25
- https://nvd.nist.gov/vuln/detail/CVE-2022-36107
- https://github.com/TYPO3/typo3/commit/546208428c861a09d62b86cde141eb19a81fae66
- https://github.com/TYPO3/typo3/commit/bd58d2ff2eeef89e63ef754a2389597d22622a39
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2022-36107.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-36107.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2022-009
