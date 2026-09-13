# [M] CVE-2025-12972

## Summary
Severity: Medium
Advisory: BIT-fluent-bit-2025-12972
Aliases: CVE-2025-12972
Ecosystem: Bitnami
Published: 2025-12-01
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2025-12972
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=4.1.0 <4.1.1

## Details
Fluent Bit out_file plugin does not properly sanitize tag values when deriving output file names. When the File option is omitted, the plugin uses untrusted tag input to construct file paths. This allows attackers with network access to craft tags containing path traversal sequences that cause Fluent Bit to write files outside the intended output directory.

## References
- https://fluentbit.io/blog/2025/10/28/security-vulnerabilities-addressed-in-fluent-bit-v4.1-and-backported-to-v4.0/
- https://nvd.nist.gov/vuln/detail/CVE-2025-12972
- https://www.oligo.security/blog/critical-vulnerabilities-in-fluent-bit-expose-cloud-environments-to-remote-takeover
