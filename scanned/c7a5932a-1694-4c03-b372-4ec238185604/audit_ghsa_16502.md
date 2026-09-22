# [M] PHP Censor uses a weak hashing algorithm for the remember me key

## Summary
Severity: Medium
Advisory: GHSA-fqw7-839j-hvxj
CVE: CVE-2024-34914
CWE: CWE-327
Ecosystem: Packagist
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2024-05-14
Source: https://github.com/advisories/GHSA-fqw7-839j-hvxj
Type: github-advisory

## Affected
- Packagist: `php-censor/php-censor` — affected >=2.1.0 <2.1.5
- Packagist: `php-censor/php-censor` — affected >=0 <2.0.13

## Details
php-censor v2.1.4 and fixed in v.2.1.5 was discovered to utilize a weak hashing algorithm for its remember_key value. This allows attackers to bruteforce to bruteforce the remember_key value to gain access to accounts that have checked "remember me" when logging in.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-34914
- https://github.com/php-censor/php-censor/commit/7b011d1b60f543e6ed814315a285cc80074d12e5
- https://chmod744.super.site/redacted-vulnerability
- https://github.com/php-censor/php-censor
