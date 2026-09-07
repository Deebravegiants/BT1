# [M] Cross-Site Scripting in Fluid view helpers

## Summary
Severity: Medium
Advisory: GHSA-vqqx-jw6p-q3rf
CVE: CVE-2020-26227
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2020-12-21
Source: https://github.com/advisories/GHSA-vqqx-jw6p-q3rf
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.23
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.10
- Packagist: `typo3/cms-core` — affected >=8.7.0 <8.7.38
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.10
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.23
- Packagist: `typo3/cms` — affected >=8.7.0 <8.7.38

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N/E:F/RL:O/RC:C` (5.7)
> * CWE-79

### Problem
It has been discovered that system extension Fluid (`typo3/cms-fluid`) of the TYPO3 core is vulnerable to cross-site scripting passing user-controlled data as argument to Fluid view helpers.

```
<f:form ... fieldNamePrefix="{payload}" />
<f:be.labels.csh ... label="{payload}" />
<f:be.menus.actionMenu ... label="{payload}" />
```

### Solution
Update to TYPO3 versions 9.5.23 or 10.4.10 that fix the problem described.

### Credits
Thanks to TYPO3 security team member Oliver Hader who reported this issue and to TYPO3 security team members Helmut Hummel & Oliver Hader who fixed the issue.

### References
* [TYPO3-CORE-SA-2020-010](https://typo3.org/security/advisory/typo3-core-sa-2020-010)

## References
- https://github.com/TYPO3/TYPO3.CMS/security/advisories/GHSA-vqqx-jw6p-q3rf
- https://nvd.nist.gov/vuln/detail/CVE-2020-26227
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2020-26227.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2020-26227.yaml
- https://packagist.org/packages/typo3/cms-core
- https://typo3.org/security/advisory/typo3-core-sa-2020-010
