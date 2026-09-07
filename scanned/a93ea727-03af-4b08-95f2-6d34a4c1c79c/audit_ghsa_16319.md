# [M] TYPO3 Backend Forms vulnerable to Information Disclosure of Hashed Passwords

## Summary
Severity: Medium
Advisory: GHSA-38r2-5695-334w
CVE: CVE-2024-25118
CWE: CWE-200
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-02-13
Source: https://github.com/advisories/GHSA-38r2-5695-334w
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
Password hashes were being reflected in the editing forms of the TYPO3 backend user interface. This allowed attackers to crack the plaintext password using brute force techniques. Exploiting this vulnerability requires a valid backend user account.

### Solution
Update to TYPO3 versions 8.7.57 ELTS, 9.5.46 ELTS, 10.4.43 ELTS, 11.5.35 LTS, 12.4.11 LTS, 13.0.1 that fix the problem described.

### Credits
Thanks to the TYPO3 framework merger Christian Kuhn and external security researchers Maximilian Beckmann, Klaus-Günther Schmidt who reported this issue, and TYPO3 security team member Oliver Hader who fixed the issue.

### References
* [TYPO3-CORE-SA-2024-003](https://typo3.org/security/advisory/typo3-core-sa-2024-003)

## References
- https://github.com/TYPO3/typo3/security/advisories/GHSA-38r2-5695-334w
- https://nvd.nist.gov/vuln/detail/CVE-2024-25118
- https://github.com/TYPO3/typo3/commit/1186b2fec8a665a8f228ed66e6d60abf8407c17b
- https://github.com/TYPO3/typo3/commit/c7a135c25a14b852eebe4335f21ba3c606188f3a
- https://github.com/TYPO3/typo3/commit/cafc5af7fdce7734e6c8f9ecf2efd17b246fc049
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2024-003
