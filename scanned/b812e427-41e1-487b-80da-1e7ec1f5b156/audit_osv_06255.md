# [M] libxml streams use wrong content-type header when requesting a redirected resource

## Summary
Severity: Medium
Advisory: BIT-libphp-2025-1219
Aliases: BIT-php-2025-1219, BIT-php-min-2025-1219, CVE-2025-1219, GHSA-p3x9-6h7p-cgfc
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2025-1219
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.4.0 <8.4.5

## Details
In PHP from 8.1.* before 8.1.32, from 8.2.* before 8.2.28, from 8.3.* before 8.3.19, from 8.4.* before 8.4.5, when requesting a HTTP resource using the DOM or SimpleXML extensions, the wrong content-type header is used to determine the charset when the requested resource performs a redirect. This may cause the resulting document to be parsed incorrectly or bypass validations.

## References
- https://github.com/php/php-src/security/advisories/GHSA-p3x9-6h7p-cgfc
- https://nvd.nist.gov/vuln/detail/CVE-2025-1219
- https://security.netapp.com/advisory/ntap-20250523-0007/
- https://lists.debian.org/debian-lts-announce/2025/03/msg00014.html
