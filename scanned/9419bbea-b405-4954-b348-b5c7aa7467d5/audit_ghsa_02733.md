# [M] Information Disclosure in User Authentication

## Summary
Severity: Medium
Advisory: GHSA-34fr-fhqr-7235
CVE: CVE-2021-32767
CWE: CWE-532
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-07-26
Source: https://github.com/advisories/GHSA-34fr-fhqr-7235
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=7.0.0 <7.6.52
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.41
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.28
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.18
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.3.1
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.18
- Packagist: `typo3/cms` — affected >=11.0.0 <11.3.1
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.28

## Details
> ### Meta
> * CVSS: `AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N/E:F/RL:O/RC:C` (4.9)

### Problem
It has been discovered that user credentials have been logged as plaintext when explicitly using log level debug, which is not the _default_ configuration.

### Solution
Update to TYPO3 versions 7.6.52 ELTS, 8.7.41 ELTS, 9.5.28, 10.4.18, 11.3.1 that fix the problem described.

### Credits
Thanks to Ingo Schmitt who reported this issue, and to TYPO3 core & security team member Benni Mack who fixed the issue.

### References
* [TYPO3-CORE-SA-2021-012](https://typo3.org/security/advisory/typo3-core-sa-2021-012)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-34fr-fhqr-7235
- https://github.com/TYPO3/typo3/security/advisories/GHSA-34fr-fhqr-7235
- https://nvd.nist.gov/vuln/detail/CVE-2021-32767
- https://github.com/TYPO3/typo3/commit/0b4950163b8919451964133febc65bcdfcec721c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-32767.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-32767.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2021-012
- https://typo3.org/security/advisory/typo3-core-sa-2021-013
