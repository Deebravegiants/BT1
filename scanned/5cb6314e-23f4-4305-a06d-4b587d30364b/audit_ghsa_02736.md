# [M] Cross-Site Scripting in Page Preview

## Summary
Severity: Medium
Advisory: GHSA-8mq9-fqv8-59wf
CVE: CVE-2021-32667
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-07-22
Source: https://github.com/advisories/GHSA-8mq9-fqv8-59wf
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.28
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.18
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.3.1
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.18
- Packagist: `typo3/cms` — affected >=11.0.0 <11.3.1
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.28

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N/E:F/RL:O/RC` (5.0)

### Problem
Failing to properly encode _Page TSconfig_ settings, corresponding page preview module (_Web>View_) is vulnerable to persistent cross-site scripting. A valid backend user account is needed to exploit this vulnerability.

### Solution
Update to TYPO3 versions 9.5.28, 10.4.18, 11.3.1 that fix the problem described.

### Credits
Thanks to TYPO3 core merger Oliver Bartsch who reported and fixed the issue.

### References
* [TYPO3-CORE-SA-2021-009](https://typo3.org/security/advisory/typo3-core-sa-2021-009)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-8mq9-fqv8-59wf
- https://github.com/TYPO3/typo3/security/advisories/GHSA-8mq9-fqv8-59wf
- https://nvd.nist.gov/vuln/detail/CVE-2021-32667
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-32667.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-32667.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2021-009
