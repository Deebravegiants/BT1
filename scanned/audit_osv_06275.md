# [C] SoapServer session-persisted object use-after-free via SOAP header fault

## Summary
Severity: Critical
Advisory: BIT-libphp-2026-7261
Aliases: BIT-php-2026-7261, BIT-php-min-2026-7261, CVE-2026-7261
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-libphp-2026-7261
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.5.0 <8.5.6

## Details
In PHP versions 8.2.* before 8.2.31, 8.3.* before 8.3.31, 8.4.* before 8.4.21, and 8.5.* before 8.5.6, when SoapServer is configured with SOAP_PERSISTENCE_SESSION, the handler object is persisted across requests via session storage. However, in the case SOAP requests results in an error, the persistance is handled incorrectly, resulting in freeing the object while keeping a pointer to it, which may lead to use-after-free. This may lead to memory corruption, information disclosure, or process crashes, with confidentiality, integrity, and availability impact on the vulnerable system.

## References
- https://github.com/php/php-src/security/advisories/GHSA-m33r-qmcv-p97q
- https://nvd.nist.gov/vuln/detail/CVE-2026-7261
