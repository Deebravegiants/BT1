# [M] TYPO3 CMS has Insecure Deserialization via Core API

## Summary
Severity: Medium
Advisory: GHSA-c78m-c52x-jgwp
CVE: CVE-2026-49740
CWE: CWE-502
Ecosystem: Packagist
CVSS: CVSS:4.0/AV:L/AC:L/AT:N/PR:L/UI:N/VC:N/VI:L/VA:N/SC:H/SI:H/SA:H (CVSS_V4)
Published: 2026-06-12
Source: https://github.com/advisories/GHSA-c78m-c52x-jgwp
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=0 <10.4.57
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.51
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.46
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.4.31
- Packagist: `typo3/cms-core` — affected >=14.0.0 <14.3.3

## Details
### Problem
TYPO3's cache frontend (`VariableFrontend`) and persistent key-value store (`Registry`) deserialized PHP payloads without integrity validation or class restrictions. An attacker with write access to the underlying storage backend (cache store or sys_registry database table) could inject a crafted serialized payload to trigger PHP Object Injection, potentially exploiting a gadget chain to achieve Remote Code Execution or other high-impact effects.

Exploiting this vulnerability requires direct local write access to the storage, such as the SQL database or file system.

### Solution
Update to TYPO3 versions 10.4.57 ELTS, 11.5.51 ELTS, 12.4.46 ELTS, 13.4.31 LTS, 14.3.3 LTS that fix the problem described.

### Credits
TYPO3 CMS thanks “z3rco”, Chowdhury Faizal Ahammed, Rick Larabee, Vitaly Simonovich, Nozomu Sasaki, Mert Akdag, “tikket”, Shafi Almutairi for reporting this issue, and to TYPO3 core & security team member Oliver Hader for fixing it.

### Resources
* [TYPO3-CORE-SA-2026-018](https://typo3.org/security/advisory/typo3-core-sa-2026-018)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-c78m-c52x-jgwp
- https://nvd.nist.gov/vuln/detail/CVE-2026-49740
- https://github.com/TYPO3/typo3/commit/48bcf24f31f52cc0b43d3bea4984634bd2cf85c7
- https://github.com/TYPO3/typo3/commit/87cd7c5b710c44d3606fed277b040a75dc6a9c02
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms-core/CVE-2026-49740.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2026-018
