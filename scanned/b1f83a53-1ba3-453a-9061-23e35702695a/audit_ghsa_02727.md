# [M] Cross-Site Scripting in Backend Grid View

## Summary
Severity: Medium
Advisory: GHSA-rgcg-28xm-8mmw
CVE: CVE-2021-32669
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2021-07-22
Source: https://github.com/advisories/GHSA-rgcg-28xm-8mmw
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.41
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.28
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.18
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.3.1
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.18
- Packagist: `typo3/cms` — affected >=11.0.0 <11.3.1
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.28

## Details
### Problem
Failing to properly encode settings for _backend layouts_, the corresponding grid view is vulnerable to persistent cross-site scripting. A valid backend user account is needed to exploit this vulnerability.

### Solution
Update to TYPO3 versions 8.7.41 ELTS, 9.5.28, 10.4.18, 11.3.1 that fix the problem described.

### Credits
Thanks to TYPO3 core merger Oliver Bartsch who reported and fixed the issue.

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-rgcg-28xm-8mmw
- https://nvd.nist.gov/vuln/detail/CVE-2021-32669
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2021-32669.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2021-32669.yaml
- https://typo3.org/security/advisory/typo3-core-sa-2021-011
