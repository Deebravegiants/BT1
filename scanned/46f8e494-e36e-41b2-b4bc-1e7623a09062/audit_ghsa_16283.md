# [M] Path Traversal in TYPO3 File Abstraction Layer Storages

## Summary
Severity: Medium
Advisory: GHSA-w6x2-jg8h-p6mp
CVE: CVE-2023-30451
CWE: CWE-22
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-w6x2-jg8h-p6mp
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=8.0.0 <8.7.57
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.46
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.43
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.35
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.11
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.0.1

## Details
### Problem
Configurable storages using the local driver of the File Abstraction Layer (FAL) could be configured to access directories outside of the root directory of the corresponding project. The system setting in `BE/lockRootPath` was not evaluated by the file abstraction layer component. An administrator-level backend user account is required to exploit this vulnerability.

### Solution
Update to TYPO3 versions 8.7.57 ELTS, 9.5.46 ELTS, 10.4.43 ELTS, 11.5.35 LTS, 12.4.11 LTS, 13.0.1 that fix the problem described.

#### ℹ️ **Strong security defaults - Manual actions required**

_see [Important: #102800 changelog](https://docs.typo3.org/c/typo3/cms-core/main/en-us/Changelog/11.5.x/Important-102800-FileAbstractionLayerEnforcesAbsolutePathsToMatchProjectRootOrLockRootPath.html)_

Assuming that a web project is located in the directory `/var/www/example.org` (the "project root path" for Composer-based projects) and the publicly accessible directory is located at `/var/www/example.org/public` (the "public root path"), accessing resources via the File Abstraction Layer component is limited to the mentioned directories.

To grant additional access to directories, they must be explicitly configured in the system settings of `$GLOBALS['TYPO3_CONF_VARS']['BE']['lockRootPath']` - either using the Install Tool or according to deployment techniques. The existing setting has been extended to support multiple directories configured as an array of strings.

Example:
```php
$GLOBALS['TYPO3_CONF_VARS']['BE']['lockRootPath'] = [
  ‘/var/shared/documents/’,
  ‘/var/shared/images/’,
];
```

❗ **Storages that reference directories not explicitly granted will be marked as "offline" internally - no resources can be used in the website's frontend and backend context.**

### Credits
Thanks to TYPO3 core & security team members Oliver Hader and Benjamin Franzke who fixed the issue.

### References
* [TYPO3-CORE-SA-2024-001](https://typo3.org/security/advisory/typo3-core-sa-2024-001)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-w6x2-jg8h-p6mp
- https://nvd.nist.gov/vuln/detail/CVE-2023-30451
- https://github.com/TYPO3/typo3/commit/205115cca3d67594a12d0195c937da0e51eb494a
- https://github.com/TYPO3/typo3/commit/78fb9287a2f0487c39288070cb0493a5265f1789
- https://github.com/TYPO3/typo3/commit/accf537c7379b4359bc0f957c4d0c07baddd710a
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2024-001
- http://packetstormsecurity.com/files/176274/TYPO3-11.5.24-Path-Traversal.html
