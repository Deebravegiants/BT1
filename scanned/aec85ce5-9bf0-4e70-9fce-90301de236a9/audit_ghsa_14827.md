# [M] ZendFramework Information Disclosure and Insufficient Entropy vulnerability

## Summary
Severity: Medium
Advisory: GHSA-2fhr-8r8r-qp56
CWE: CWE-200, CWE-331
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-2fhr-8r8r-qp56
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework` — affected >=2.0.0 <2.4.9

## Details
In Zend Framework, `Zend_Captcha_Word` (v1) and `Zend\Captcha\Word` (v2) generate a "word" for a CAPTCHA challenge by selecting a sequence of random letters from a character set. Prior to this advisory, the selection was performed using PHP's `internal array_rand()` function. This function does not generate sufficient entropy due to its usage of `rand()` instead of more cryptographically secure methods such as `openssl_pseudo_random_bytes()`. This could potentially lead to information disclosure should an attacker be able to brute force the random number generation.

## References
- https://github.com/zendframework/zendframework/commit/ced8ff93ef892a64885c03f5dfab3f788a219709
- https://framework.zend.com/security/advisory/ZF2015-09
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework/ZF2015-09.yaml
- https://github.com/zendframework/zendframework
