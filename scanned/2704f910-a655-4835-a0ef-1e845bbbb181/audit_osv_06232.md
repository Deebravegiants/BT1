# [H] password_verify() always returns true for some invalid hashes

## Summary
Severity: High
Advisory: BIT-libphp-2023-0567
Aliases: BIT-php-2023-0567, BIT-php-min-2023-0567, CVE-2023-0567, GHSA-7fj2-8x79-rjf4
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2023-0567
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.2.0 <8.2.3

## Details
In PHP 8.0.X before 8.0.28, 8.1.X before 8.1.16 and 8.2.X before 8.2.3, password_verify() function may accept some invalid Blowfish hashes as valid. If such invalid hash ever ends up in the password database, it may lead to an application allowing any password for this entry as valid.

## References
- https://bugs.php.net/bug.php?id=81744
- https://github.com/php/php-src/security/advisories/GHSA-7fj2-8x79-rjf4
- https://nvd.nist.gov/vuln/detail/CVE-2023-0567
- https://security.netapp.com/advisory/ntap-20230331-0008/
