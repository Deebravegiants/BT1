# [M] TYPO3 Cross-Site Scripting in Form Framework validation handling

## Summary
Severity: Medium
Advisory: GHSA-v8m4-3w37-ghxx
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-v8m4-3w37-ghxx
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=10.0.0 <10.2.1
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.30
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.12

## Details
It has been discovered that the output of field validation errors in the Form Framework is vulnerable to cross-site scripting.

## References
- https://github.com/TYPO3/typo3/commit/966a0038c16c04d484c1703fba9fdc13f3e7a95c
- https://github.com/TYPO3/typo3/commit/9692bf83f8310cca17c9a968c4fe92ffe0deb59d
- https://github.com/TYPO3/typo3/commit/e971b012c837f1e64c1498b567ef6eec304febe5
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2019-12-17-1.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2019-021
