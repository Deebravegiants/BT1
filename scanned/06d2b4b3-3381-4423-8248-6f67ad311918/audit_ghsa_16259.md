# [H] TYPO3 vulnerable to Improper Access Control Persisting File Abstraction Layer Entities via Data Handler

## Summary
Severity: High
Advisory: GHSA-rj3x-wvc6-5j66
CVE: CVE-2024-25121
CWE: CWE-200, CWE-284
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-rj3x-wvc6-5j66
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
Entities of the File Abstraction Layer (FAL) could be persisted directly via `DataHandler`. This allowed attackers to reference files in the fallback storage directly and retrieve their file names and contents. The fallback storage ("zero-storage") is used as a backward compatibility layer for files located outside properly configured file storages and within the public web root directory. Exploiting this vulnerability requires a valid backend user account.


### Solution
Update to TYPO3 versions 8.7.57 ELTS, 9.5.46 ELTS, 10.4.43 ELTS, 11.5.35 LTS, 12.4.11 LTS, 13.0.1 that fix the problem described.

#### ℹ️ Strong security defaults - Manual actions required

When persisting entities of the File Abstraction Layer directly via DataHandler, `sys_file` entities are now denied by default, and `sys_file_reference` & `sys_file_metadata` entities are not permitted to reference files in the fallback storage anymore.

When importing data from secure origins, this must be explicitly enabled in the corresponding DataHandler instance by using `$dataHandler->isImporting = true;`.

### Credits
Thanks to TYPO3 core & security team member Oliver Hader who reported and fixed the issue.

### References
* [TYPO3-CORE-SA-2024-006](https://typo3.org/security/advisory/typo3-core-sa-2024-006)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-rj3x-wvc6-5j66
- https://nvd.nist.gov/vuln/detail/CVE-2024-25121
- https://github.com/TYPO3/typo3/commit/38f0bf9a61e10365be26eb75bc23a81184dbed07
- https://github.com/TYPO3/typo3/commit/71e652bf84b16fd3592205f61f36750ab03db74c
- https://github.com/TYPO3/typo3/commit/b47b6ddf5a5f3f852c6e43f837360780c12e3c47
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2024-006
