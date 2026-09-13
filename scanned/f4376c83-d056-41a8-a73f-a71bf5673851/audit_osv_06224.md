# [H] Freeing unallocated memory in php_pgsql_free_params()

## Summary
Severity: High
Advisory: BIT-libphp-2022-31625
Aliases: BIT-php-2022-31625, BIT-php-min-2022-31625, CVE-2022-31625
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2022-31625
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.1.0 <8.1.7

## Details
In PHP versions 7.4.x below 7.4.30, 8.0.x below 8.0.20, and 8.1.x below 8.1.7, when using Postgres database extension, supplying invalid parameters to the parametrized query may lead to PHP attempting to free memory using uninitialized data as pointers. This could lead to RCE vulnerability or denial of service.

## References
- https://bugs.php.net/bug.php?id=81720
- https://lists.debian.org/debian-lts-announce/2022/12/msg00030.html
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/3T4MMEEZYYAEHPQMZDFN44PHORJWJFZQ/
- https://lists.fedoraproject.org/archives/list/package-announce%40lists.fedoraproject.org/message/ZZTZQKRGEYJT5UB4FGG3MOE72SQUHSL4/
- https://nvd.nist.gov/vuln/detail/CVE-2022-31625
- https://security.gentoo.org/glsa/202209-20
- https://security.netapp.com/advisory/ntap-20220722-0005/
- https://www.debian.org/security/2022/dsa-5179
