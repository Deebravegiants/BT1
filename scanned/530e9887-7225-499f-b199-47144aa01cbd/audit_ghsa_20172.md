# [M] Insufficient Session Expiration in TYPO3's Admin Tool

## Summary
Severity: Medium
Advisory: GHSA-wwjw-r3gj-39fq
CVE: CVE-2022-31050
CWE: CWE-613
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-wwjw-r3gj-39fq
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.35
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.29
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.11
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.29
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.11

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:L/E:F/RL:O/RC:C` (5.6)

### Problem
Admin Tool sessions initiated via the TYPO3 backend user interface have not been revoked even if the corresponding user account was degraded to lower permissions or disabled completely. This way, sessions in the admin tool theoretically could have been prolonged without any limit.

### Solution
Update to TYPO3 versions 9.5.35 ELTS, 10.4.29, 11.5.11 that fix the problem described above.

### Credits
Thanks to Kien Hoang who reported this issue and to TYPO3 framework merger Ralf Zimmermann and TYPO3 security member Oliver Hader who fixed the issue.

### References
* [TYPO3-CORE-SA-2022-005](https://typo3.org/security/advisory/typo3-core-sa-2022-005)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-wwjw-r3gj-39fq
- https://nvd.nist.gov/vuln/detail/CVE-2022-31050
- https://github.com/TYPO3/typo3/commit/592387972912290c135ebecc91768a67f83a3a4d
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-31050.yaml
- https://github.com/TYPO3-CMS/core
- https://typo3.org/security/advisory/typo3-core-sa-2022-005
