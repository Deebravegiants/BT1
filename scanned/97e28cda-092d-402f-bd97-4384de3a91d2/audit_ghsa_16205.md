# [H] TYPO3 Install Tool vulnerable to Code Execution

## Summary
Severity: High
Advisory: GHSA-5w2h-59j3-8x5w
CVE: CVE-2024-22188
CWE: CWE-77, CWE-94
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-5w2h-59j3-8x5w
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
Several settings in the Install Tool for configuring the path to system binaries were vulnerable to code execution. Exploiting this vulnerability requires an administrator-level backend user account with system maintainer permissions.

The corresponding change for this advisory involves enforcing the known disadvantages described in [TYPO3-PSA-2020-002: Protecting Install Tool with Sudo Mode](https://typo3.org/security/advisory/typo3-psa-2020-002).

### Solution
Update to TYPO3 versions 8.7.57 ELTS, 9.5.46 ELTS, 10.4.43 ELTS, 11.5.35 LTS, 12.4.11 LTS, 13.0.1 that fix the problem described.

### Credits
Thanks to Rickmer Frier & Daniel Jonka who reported this issue and to TYPO3 core & security team member Benjamin Franzke who fixed the issue.

### References
* [TYPO3-CORE-SA-2024-002](https://typo3.org/security/advisory/typo3-core-sa-2024-002)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-5w2h-59j3-8x5w
- https://nvd.nist.gov/vuln/detail/CVE-2024-22188
- https://github.com/TYPO3/typo3/commit/47e897f8c7668ef299ecc9ce93f52cafbb3497ed
- https://github.com/TYPO3/typo3/commit/6cc11761b8e2434fa4ccc9f096c65ca82569cfdf
- https://github.com/TYPO3/typo3/commit/84e07e35b880a544b517868432c56987d05d46d4
- https://github.com/TYPO3/typo3
- https://typo3.org/help/security-advisories
- https://typo3.org/security/advisory/typo3-core-sa-2024-002
- https://typo3.org/security/advisory/typo3-psa-2020-002
