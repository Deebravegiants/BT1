# [M] Null byte termination in hostnames

## Summary
Severity: Medium
Advisory: BIT-libphp-2025-1220
Aliases: BIT-php-2025-1220, BIT-php-min-2025-1220, CVE-2025-1220, GHSA-3cr5-j632-f35r
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2025-1220
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.4.0 <8.4.10

## Details
In PHP versions:8.1.* before 8.1.33, 8.2.* before 8.2.29, 8.3.* before 8.3.23, 8.4.* before 8.4.10 some functions like fsockopen() lack validation that the hostname supplied does not contain null characters. This may lead to other functions like parse_url() treat the hostname in different way, thus opening way to security problems if the user code implements access checks before access using such functions.

## References
- https://github.com/php/php-src/security/advisories/GHSA-3cr5-j632-f35r
- https://nvd.nist.gov/vuln/detail/CVE-2025-1220
- http://www.openwall.com/lists/oss-security/2025/07/11/4
- https://lists.debian.org/debian-lts-announce/2025/07/msg00017.html
