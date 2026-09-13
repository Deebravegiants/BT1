# [H] ZendFramework1 Potential Insufficient Entropy Vulnerability

## Summary
Severity: High
Advisory: GHSA-8xhv-gqm4-3w99
CWE: CWE-331
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-06-07
Source: https://github.com/advisories/GHSA-8xhv-gqm4-3w99
Type: github-advisory

## Affected
- Packagist: `zendframework/zendframework1` — affected >=1.12.0 <1.12.18

## Details
We discovered several methods used to generate random numbers in ZF1 that potentially used insufficient entropy. These random number generators are used in the following method calls:
```
Zend_Ldap_Attribute::createPassword
Zend_Form_Element_Hash::_generateHash
Zend_Gdata_HttpClient::filterHttpRequest
Zend_Filter_Encrypt_Mcrypt::_srand
Zend_OpenId::randomBytes
```
In each case, the methods were using rand() or mt_rand(), neither of which can generate cryptographically secure values. This could potentially lead to information disclosure should an attacker be able to brute force the random number generation.

Moreover, we discovered a potential security issue in the usage of the [openssl_random_pseudo_bytes()](http://php.net/manual/en/function.openssl-random-pseudo-bytes.php) function in Zend_Crypt_Math::randBytes, reported in PHP BUG [#70014](https://bugs.php.net/bug.php?id=70014), and the security implications reported in a discussion [on the random_compat library.](https://github.com/paragonie/random_compat/issues/96)

## References
- https://framework.zend.com/security/advisory/ZF2016-01
- https://github.com/FriendsOfPHP/security-advisories/blob/master/zendframework/zendframework1/ZF2016-01.yaml
- https://github.com/zendframework/zf1
