# [M] TYPO3 CMS vulnerable to Weak Authentication in Frontend Login

## Summary
Severity: Medium
Advisory: GHSA-jfp7-79g7-89rf
CVE: CVE-2022-23501
CWE: CWE-287, CWE-302
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2022-12-13
Source: https://github.com/advisories/GHSA-jfp7-79g7-89rf
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=0 <8.7.49
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.38
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.33
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.20
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.1.1
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.33
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.20
- Packagist: `typo3/cms` — affected >=12.0.0 <12.1.1

## Details
### Problem
Restricting frontend login to specific users, organized in different storage folders (partitions), can be bypassed. A potential attacker might use this ambiguity in usernames to get access to a different account - however, credentials must be known to the adversary.

### Solution
Update to TYPO3 versions 8.7.49 ELTS, 9.5.38 ELTS, 10.4.33, 11.5.20, 12.1.1 that fix the problem described above.

### References
* [TYPO3-CORE-SA-2022-013](https://typo3.org/security/advisory/typo3-core-sa-2022-013)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-jfp7-79g7-89rf
- https://nvd.nist.gov/vuln/detail/CVE-2022-23501
- https://github.com/TYPO3/typo3/commit/28be9cdb3fed02ce4cfc6fa2d39f7d8e2266eced
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2022-23501.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-23501.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2022-013
