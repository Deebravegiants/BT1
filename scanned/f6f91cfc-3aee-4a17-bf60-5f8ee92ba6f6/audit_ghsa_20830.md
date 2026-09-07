# [M] TYPO3 CMS vulnerable to User Enumeration via Response Timing

## Summary
Severity: Medium
Advisory: GHSA-m392-235j-9r7r
CVE: CVE-2022-36105
CWE: CWE-203
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-09-16
Source: https://github.com/advisories/GHSA-m392-235j-9r7r
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
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N/E:F/RL:O/RC:C` (4.9)

### Problem
It has been discovered that observing response time during user authentication (backend and frontend) can be used to distinguish between existing and non-existing user accounts.

Extension authors of 3rd party TYPO3 extensions providing a custom authentication service should check if the extension is affected by the described problem. Affected extensions must implement new `MimicServiceInterface::mimicAuthUser`, which simulates corresponding times regular processing would usually take.

### Solution
Update to TYPO3 version 7.6.58 ELTS, 8.7.48 ELTS, 9.5.37 ELTS, 10.4.32 or 11.5.16 that fix the problem described above.

### Credits
Thanks to Vautia who reported this issue and to TYPO3 core & security team members Oliver Hader who fixed the issue.

### References
* [TYPO3-CORE-SA-2022-007](https://typo3.org/security/advisory/typo3-core-sa-2022-007)
* [Vulnerability Report on huntr.dev](https://huntr.dev/bounties/7d519735-2877-4fad-bd77-accde3e290a7/) (embargoed +30 days)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-m392-235j-9r7r
- https://nvd.nist.gov/vuln/detail/CVE-2022-36105
- https://github.com/TYPO3/typo3/commit/f0fc9c4cd7c38207c30dd158de53ee5d9d6f41a2
- https://github.com/TYPO3/typo3/commit/f8b83ce15d4ea275a5a5e564e5d324242f7937b6
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2022-36105.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-36105.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2022-007
