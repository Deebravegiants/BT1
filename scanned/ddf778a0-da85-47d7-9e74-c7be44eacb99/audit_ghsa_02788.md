# [H] Cross-Site-Request-Forgery in Backend

## Summary
Severity: High
Advisory: GHSA-657m-v5vm-f6rw
CVE: CVE-2021-41113
CWE: CWE-309, CWE-352
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-10-05
Source: https://github.com/advisories/GHSA-657m-v5vm-f6rw
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=11.2.0 <11.5.0
- Packagist: `typo3/cms` — affected >=11.2.0 <11.5.0

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H/E:F/RL:O/RC:C` (8.2)

### Problem
It has been discovered that the new TYPO3 v11 feature that allows users to create and share [deep links in the backend user interface](https://typo3.org/article/typo3-version-112-escape-the-orbit#c12178) is vulnerable to cross-site-request-forgery.

The impact is the same as described in [TYPO3-CORE-SA-2020-006 (CVE-2020-11069)](https://typo3.org/security/advisory/typo3-core-sa-2020-006). However, it is not limited to the same site context and does not require the attacker to be authenticated. In a worst case scenario, the attacker could create a new admin user account to compromise the system.

To successfully carry out an attack, an attacker must trick his victim to access a compromised system. The victim must have an active session in the TYPO3 backend at that time.

The following [Same-Site cookie settings](https://docs.typo3.org/c/typo3/cms-core/master/en-us/Changelog/8.7.x/Feature-90351-ConfigureTYPO3-shippedCookiesWithSameSiteFlag.html) in _$GLOBALS[TYPO3_CONF_VARS][BE][cookieSameSite]_ are required for an attack to be successful:

* _SameSite=_***strict***: malicious evil.**example.org** invoking TYPO3 application at good.**example.org**
* _SameSite=_***lax*** or ***none***: malicious **evil.com** invoking TYPO3 application at **example.org**

### Solution
Update your instance to TYPO3 version 11.5.0 which addresses the problem described.

### Credits
Thanks to Richie Lee who reported this issue and to TYPO3 core & security team members Benni Mack and Oliver Hader who fixed the issue.

### References
* [TYPO3-CORE-SA-2021-014](https://typo3.org/security/advisory/typo3-core-sa-2021-014)
* [CVE-2020-11069](https://nvd.nist.gov/vuln/detail/CVE-2020-11069) reintroduced in TYPO3 v11.2.0

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-657m-v5vm-f6rw
- https://nvd.nist.gov/vuln/detail/CVE-2020-11069
- https://nvd.nist.gov/vuln/detail/CVE-2021-41113
- https://github.com/TYPO3/typo3/commit/fa51999203c5e5d913ecae5ea843ccb2b95fa33f
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-41113.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-41113.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2020-006
- https://typo3.org/security/advisory/typo3-core-sa-2021-014
