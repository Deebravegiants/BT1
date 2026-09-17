# [H] phpseclib Infinite Loop vulnerability

## Summary
Severity: High
Advisory: GHSA-hm7p-r324-hhf3
CVE: CVE-2023-27560
CWE: CWE-835
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-03-03
Source: https://github.com/advisories/GHSA-hm7p-r324-hhf3
Type: github-advisory

## Affected
- Packagist: `phpseclib/phpseclib` — affected >=3.0.0 <3.0.19

## Details
Math/PrimeField.php in phpseclib has an infinite loop with composite primefields. This vulnerability was introduced in version 3.0.0, and has been patched in 3.0.19. The CVE for this issue originally identified the the vulnerable version as 2.x, however, the vulnerable functionality was not introduced until version 3.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-27560
- https://github.com/phpseclib/phpseclib/commit/6298d1cd55c3ffa44533bd41906caec246b60440
- https://github.com/phpseclib/phpseclib/commit/6298d1cd55c3ffa44533bd41906caec246b60440#commitcomment-103226722
- https://github.com/FriendsOfPHP/security-advisories/blob/master/phpseclib/phpseclib/CVE-2023-27560.yaml
- https://github.com/phpseclib/phpseclib
- https://github.com/phpseclib/phpseclib/releases/tag/3.0.19
