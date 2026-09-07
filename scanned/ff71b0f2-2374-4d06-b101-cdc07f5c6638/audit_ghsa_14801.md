# [M] TYPO3 Cross-Site Scripting in Backend Modal Component

## Summary
Severity: Medium
Advisory: GHSA-7q33-hxwj-7p8v
CWE: CWE-79
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-7q33-hxwj-7p8v
Type: github-advisory

## Affected
- Packagist: `typo3/cms` — affected >=7.0.0 <7.6.32
- Packagist: `typo3/cms` — affected >=8.0.0 <8.7.21
- Packagist: `typo3/cms` — affected >=9.0.0 <9.5.2

## Details
Failing to properly encode user input, notifications shown in modal windows in the TYPO3 backend are vulnerable to cross-site scripting. A valid backend user account is needed in order to exploit this vulnerability.

## References
- https://github.com/TYPO3/typo3/commit/02cd5c97228cba477d16c68e28309ce25c433ce9
- https://github.com/TYPO3/typo3/commit/89a38ad0ef9411745954f53f29bea5b8ce81cd32
- https://github.com/TYPO3/typo3/commit/c35646c3f7795a4a7b0046a88f146b490fa4883c
- https://github.com/FriendsOfPHP/security-advisories/blob/master/typo3/cms/2018-12-11-2.yaml
- https://github.com/TYPO3/typo3
- https://typo3.org/security/advisory/typo3-core-sa-2018-007
