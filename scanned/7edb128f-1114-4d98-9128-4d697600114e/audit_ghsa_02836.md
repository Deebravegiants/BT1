# [M] HTTP Host Header Injection

## Summary
Severity: Medium
Advisory: GHSA-m2jh-fxw4-gphm
CVE: CVE-2021-41114
CWE: CWE-20, CWE-644
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2021-10-05
Source: https://github.com/advisories/GHSA-m2jh-fxw4-gphm
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.0
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.0

## Details
### Meta
* CVSS: `CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:N/E:F/RL:O/RC:C` (3.5)

### Problem
It has been discovered that TYPO3 CMS is susceptible to host spoofing due to improper validation of the HTTP _Host_ header. TYPO3 uses the HTTP _Host_ header, for example, to generate absolute URLs during the frontend rendering process. Since the host header itself is provided by the client, it can be forged to any value, even in a name-based virtual hosts environment.

This vulnerability is the same as described in [TYPO3-CORE-SA-2014-001 (CVE-2014-3941)](https://typo3.org/security/advisory/typo3-core-sa-2014-001/). A regression, introduced during TYPO3 v11 development, led to this situation. The already existing setting _$GLOBALS['TYPO3_CONF_VARS']['SYS']['trustedHostsPattern']_ (used as an effective mitigation strategy in previous TYPO3 versions) was not evaluated anymore, and reintroduced the vulnerability.

### Solution
Update your instance to TYPO3 version 11.5.0 which addresses the problem described.

### Credits
Thanks to TYPO3 framework merger Benjamin Franzke who reported and fixed the issue.

### References
* [TYPO3-CORE-SA-2021-015](https://typo3.org/security/advisory/typo3-core-sa-2021-015)
* [CVE-2014-3941](https://nvd.nist.gov/vuln/detail/CVE-2014-3941) reintroduced in TYPO3 v11.0.0

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-m2jh-fxw4-gphm
- https://nvd.nist.gov/vuln/detail/CVE-2014-3941
- https://nvd.nist.gov/vuln/detail/CVE-2021-41114
- https://github.com/TYPO3/typo3/commit/5cbff85506cebe343e5ae59228977547cf8e3cf4
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-41114.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-41114.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2021-015
