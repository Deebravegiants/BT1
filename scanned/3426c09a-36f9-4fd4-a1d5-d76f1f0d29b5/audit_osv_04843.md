# [H] BIT-fluent-bit-2024-23722

## Summary
Severity: High
Advisory: BIT-fluent-bit-2024-23722
Aliases: CVE-2024-23722
Ecosystem: Bitnami
Published: 2024-05-29
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2024-23722
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=2.1.8 <2.2.2

## Details
In Fluent Bit 2.1.8 through 2.2.1, a NULL pointer dereference can be caused via an invalid HTTP payload with the content type of x-www-form-urlencoded. It crashes and does not restart. This could result in logs not being delivered properly.

## References
- https://github.com/fluent/fluent-bit/compare/v2.2.1...v2.2.2
- https://medium.com/%40adurands82/fluent-bit-dos-vulnerability-cve-2024-23722-4e3e74af9d00
- https://nvd.nist.gov/vuln/detail/CVE-2024-23722
