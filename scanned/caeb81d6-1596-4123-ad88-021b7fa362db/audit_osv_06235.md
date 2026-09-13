# [M] Missing error check and insufficient random bytes in HTTP Digest authentication for SOAP

## Summary
Severity: Medium
Advisory: BIT-libphp-2023-3247
Aliases: BIT-php-2023-3247, BIT-php-min-2023-3247, CVE-2023-3247, GHSA-76gg-c692-v2mw
Ecosystem: Bitnami
Published: 2025-08-11
Source: https://osv.dev/vulnerability/BIT-libphp-2023-3247
Type: osv

## Affected
- Bitnami: `libphp` — affected >=8.2.0 <8.2.7

## Details
In PHP versions 8.0.* before 8.0.29, 8.1.* before 8.1.20, 8.2.* before 8.2.7 when using SOAP HTTP Digest Authentication, random value generator was not checked for failure, and was using narrower range of values than it should have. In case of random generator failure, it could lead to a disclosure of 31 bits of uninitialized memory from the client to the server, and it also made easier to a malicious server to guess the client's nonce.

## References
- https://github.com/php/php-src/security/advisories/GHSA-76gg-c692-v2mw
- https://nvd.nist.gov/vuln/detail/CVE-2023-3247
