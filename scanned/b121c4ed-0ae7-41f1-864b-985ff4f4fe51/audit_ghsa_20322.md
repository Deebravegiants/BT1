# [M] Information Disclosure via Export Module

## Summary
Severity: Medium
Advisory: GHSA-8gmv-9hwg-w89g
CVE: CVE-2022-31046
CWE: CWE-200, CWE-319
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2022-06-17
Source: https://github.com/advisories/GHSA-8gmv-9hwg-w89g
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=7.0.0 <7.6.57
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.47
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.35
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.29
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.11
- Packagist: `typo3/cms` — affected >=10.0.0 <10.4.29
- Packagist: `typo3/cms` — affected >=11.0.0 <11.5.11

## Details
> ### Meta
> * CVSS: `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N/E:F/RL:O/RC:C` (4.0)

### Problem
The export functionality fails to limit the result set to allowed columns of a particular database table. This allows authenticated users to export internal details of database tables to which they already have access.

### Solution
Update to TYPO3 versions 7.6.57 ELTS, 8.7.47 ELTS, 9.5.35 ELTS, 10.4.29, 11.5.11 that fix the problem described above.

In order to address this issue, access to mentioned export functionality is completely denied for regular backend users.

ℹ️  **Strong security defaults - Manual actions required**
Following User TSconfig setting would allow using the export functionality for particular users:
```
options.impexp.enableExportForNonAdminUser = 1
```

### Credits
Thanks to TYPO3 core merger Lina Wolf who reported this issue and to TYPO3 security member Torben Hansen  who fixed the issue.

### References
* [TYPO3-CORE-SA-2022-001](https://typo3.org/security/advisory/typo3-core-sa-2022-001)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-8gmv-9hwg-w89g
- https://nvd.nist.gov/vuln/detail/CVE-2022-31046
- https://github.com/TYPO3/typo3/commit/7447a3d1283017d2ee08737a7972c720001a93e9
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2022-31046.yaml
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/CVE-2022-31046.yaml
- https://github.com/TYPO3-CMS/core
- https://typo3.org/security/advisory/typo3-core-sa-2022-001
