# [M] TYPO3 Install Tool vulnerable to Information Disclosure of Encryption Key

## Summary
Severity: Medium
Advisory: GHSA-h47m-3f78-qp9g
CVE: CVE-2024-25119
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-h47m-3f78-qp9g
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
The plaintext value of `$GLOBALS['SYS']['encryptionKey']` was displayed in the editing forms of the TYPO3 Install Tool user interface. This allowed attackers to utilize the value to generate cryptographic hashes used for verifying the authenticity of HTTP request parameters. Exploiting this vulnerability requires an administrator-level backend user account with system maintainer permissions.

### Solution
Update to TYPO3 versions 8.7.57 ELTS, 9.5.46 ELTS, 10.4.43 ELTS, 11.5.35 LTS, 12.4.11 LTS, 13.0.1 that fix the problem described.

### Credits
Thanks to TYPO3 core & security team member Benjamin Franzke who fixed the issue.

### References
* [TYPO3-CORE-SA-2024-004](https://typo3.org/security/advisory/typo3-core-sa-2024-004)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-h47m-3f78-qp9g
- https://nvd.nist.gov/vuln/detail/CVE-2024-25119
- https://github.com/TYPO3/typo3/commit/14d101359c71ee963cf51ad0c8ae777b7b9ec9a1
- https://github.com/TYPO3/typo3/commit/df486372ea56fac241d3c96ad43a7729fee64557
- https://github.com/TYPO3/typo3/commit/fa12667c046342ebfd9b159c646aeafdbc52fcfd
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2024-004
