# [H] CVE-2025-12970

## Summary
Severity: High
Advisory: BIT-fluent-bit-2025-12970
Aliases: CVE-2025-12970
Ecosystem: Bitnami
Published: 2025-12-01
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2025-12970
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=4.1.0 <4.1.1

## Details
The extract_name function in Fluent Bit in_docker input plugin copies container names into a fixed size stack buffer without validating length. An attacker who can create containers or control container names, can supply a long name that overflows the buffer, leading to process crash or arbitrary code execution.

## References
- https://fluentbit.io/blog/2025/10/28/security-vulnerabilities-addressed-in-fluent-bit-v4.1-and-backported-to-v4.0/
- https://nvd.nist.gov/vuln/detail/CVE-2025-12970
- https://www.oligo.security/blog/critical-vulnerabilities-in-fluent-bit-expose-cloud-environments-to-remote-takeover
