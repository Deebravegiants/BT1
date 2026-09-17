# [M] BIT-varnish-2025-47905

## Summary
Severity: Medium
Advisory: BIT-varnish-2025-47905
Aliases: CVE-2025-47905
Ecosystem: Bitnami
Published: 2025-05-28
Source: https://osv.dev/vulnerability/BIT-varnish-2025-47905
Type: osv

## Affected
- Bitnami: `varnish` — affected >=7.0.0 <6.6.2

## Details
Varnish Cache before 7.6.3 and 7.7 before 7.7.1, and Varnish Enterprise before 6.0.13r14, allow client-side desync via HTTP/1 requests, because the product incorrectly permits CRLF to be skipped to delimit chunk boundaries.

## References
- http://www.openwall.com/lists/oss-security/2025/05/15/2
- https://nvd.nist.gov/vuln/detail/CVE-2025-47905
- https://varnish-cache.org/security/VSV00016.html
- https://lists.debian.org/debian-lts-announce/2025/05/msg00040.html
