# [H] Zend-Captcha Information Disclosure and Insufficient Entropy vulnerability

## Summary
Severity: High
Advisory: GHSA-mg4x-prh7-g4mx
CWE: CWE-331
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-mg4x-prh7-g4mx
Type: github-advisory

## Affected
- Packagist: `zendframework/zend-captcha` — affected >=2.0.0 <2.4.9
- Packagist: `zendframework/zend-captcha` — affected >=2.5.0 <2.5.2

## Details
In Zend Framework, `Zend_Captcha_Word` (v1) and `Zend\Captcha\Word` (v2) generate a "word" for a CAPTCHA challenge by selecting a sequence of random letters from a character set. Prior to this advisory, the selection was performed using PHP's internal `array_rand()` function. This function does not generate sufficient entropy due to its usage of rand() instead of more cryptographically secure methods such as `openssl_pseudo_random_bytes()`. This could potentially lead to information disclosure should an attacker be able to brute force the random number generation.

## References
- https://github.com/zendframework/zend-captcha/commit/43c276df6e94e498bf530538aea53876a24fc47c
- https://github.com/zendframework/zend-captcha/commit/5561ef813bb4ad814e835343289dc5077d2eb262
- https://framework.zend.com/security/advisory/ZF2015-09
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zend-captcha/ZF2015-09.yaml
- https://github.com/zendframework/zend-captcha
