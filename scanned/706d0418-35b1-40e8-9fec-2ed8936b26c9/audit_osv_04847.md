# [M] CVE-2025-12969

## Summary
Severity: Medium
Advisory: BIT-fluent-bit-2025-12969
Aliases: CVE-2025-12969
Ecosystem: Bitnami
Published: 2025-12-01
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2025-12969
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=4.1.0 <4.1.1

## Details
Fluent Bit in_forward input plugin does not properly enforce the security.users authentication mechanism under certain configuration conditions. This allows remote attackers with network access to the Fluent Bit instance exposing the forward input to send unauthenticated data. By bypassing authentication controls, attackers can inject forged log records, flood alerting systems, or manipulate routing decisions, compromising the authenticity and integrity of ingested logs.

## References
- https://fluentbit.io/blog/2025/10/28/security-vulnerabilities-addressed-in-fluent-bit-v4.1-and-backported-to-v4.0/
- https://nvd.nist.gov/vuln/detail/CVE-2025-12969
- https://www.oligo.security/blog/critical-vulnerabilities-in-fluent-bit-expose-cloud-environments-to-remote-takeover
