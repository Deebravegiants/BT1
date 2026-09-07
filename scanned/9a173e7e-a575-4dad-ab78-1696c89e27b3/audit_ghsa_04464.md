# [H] TYPO3 CMS has Privilege Escalation & SQL Injection in its Form Framework

## Summary
Severity: High
Advisory: GHSA-jh32-v29g-68pq
CVE: CVE-2026-49741
CWE: CWE-862, CWE-89
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:L/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-jh32-v29g-68pq
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=14.0.0 <14.3.3
- Packagist: `typo3/cms-form` — affected >=14.0.0 <14.3.3

## Details
### Problem
Backend users with write access to the `form_definition` database table were able to directly create, update, or delete form definition records via `DataHandler`, bypassing the Form Framework's persistence validation and permission checks. This allowed injecting arbitrary form configurations, re-enabling attack vectors originally addressed in [TYPO3-CORE-SA-2018-003](https://typo3.org/security/advisory/typo3-core-sa-2018-003), including SQL injection and privilege escalation.

### Solution
Update to TYPO3 version 14.3.3 LTS that fixes the problem described.

### Credits
TYPO3 CMS thanks Selçuk Güney for reporting this issue, and to TYPO3 core & security team member Oliver Hader for fixing it.

### Resources
* [TYPO3-CORE-SA-2026-017](https://typo3.org/security/advisory/typo3-core-sa-2026-017)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-jh32-v29g-68pq
- https://nvd.nist.gov/vuln/detail/CVE-2026-49741
- https://github.com/TYPO3/typo3/commit/c90493c13b633f328cf2c066182c90a1655ff0fc
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2026-49741.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2018-003
- https://typo3.org/security/advisory/typo3-core-sa-2026-017
