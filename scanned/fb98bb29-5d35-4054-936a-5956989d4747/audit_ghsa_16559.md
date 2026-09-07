# [M] TYPO3 vulnerable to Cross-Site Scripting in the ShowImageController

## Summary
Severity: Medium
Advisory: GHSA-hw6c-6gwq-3m3m
CVE: CVE-2024-34357
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-hw6c-6gwq-3m3m
Type: github-advisory

## Affected
- Packagist: `typo3/cms-core` — affected >=9.0.0 <9.5.48
- Packagist: `typo3/cms-core` — affected >=10.0.0 <10.4.45
- Packagist: `typo3/cms-core` — affected >=11.0.0 <11.5.37
- Packagist: `typo3/cms-core` — affected >=12.0.0 <12.4.15
- Packagist: `typo3/cms-core` — affected >=13.0.0 <13.1.1

## Details
### Problem
Failing to properly encode user-controlled values in file entities, the `ShowImageController` (_eID tx_cms_showpic_) is vulnerable to cross-site scripting. Exploiting this vulnerability requires a valid backend user account with access to file entities.

### Solution
Update to TYPO3 versions 9.5.48 ELTS, 10.4.45 ELTS, 11.5.37 LTS, 12.4.15 LTS, 13.1.1 that fix the problem described.

### Credits
Thanks to TYPO3 security team member Torben Hansen who reported this issue and to TYPO3 core & security team member Oliver Hader who fixed the issue.

### References
* [TYPO3-CORE-SA-2024-009](https://typo3.org/security/advisory/typo3-core-sa-2024-009)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-hw6c-6gwq-3m3m
- https://nvd.nist.gov/vuln/detail/CVE-2024-34357
- https://github.com/TYPO3/typo3/commit/376474904f6b9a54dc1b785a2e45277cbd13b0d7
- https://github.com/TYPO3/typo3/commit/b31d05d1da3eeaeead2d19eb43b1c3f9c88e15ee
- https://github.com/TYPO3/typo3/commit/d774642381354d3bf5095a5a26e18acd2767f0b1
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2024-009
