# [H] pgsql extension does not check for errors during escaping

## Summary
Severity: High
Advisory: BIT-libphp-2025-1735
Aliases: BIT-php-2025-1735, BIT-php-min-2025-1735, CVE-2025-1735, GHSA-hrwm-9436-5mv3
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2025-1735
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.4.0 <8.4.10

## Details
In PHP versions:8.1.* before 8.1.33, 8.2.* before 8.2.29, 8.3.* before 8.3.23, 8.4.* pgsql and pdo_pgsql escaping functions do not check if the underlying quoting functions returned errors. This could cause crashes if Postgres server rejects the string as invalid.

## References
- https://github.com/php/php-src/security/advisories/GHSA-hrwm-9436-5mv3
- https://nvd.nist.gov/vuln/detail/CVE-2025-1735
- http://www.openwall.com/lists/oss-security/2025/07/11/4
- https://lists.debian.org/debian-lts-announce/2025/07/msg00017.html
