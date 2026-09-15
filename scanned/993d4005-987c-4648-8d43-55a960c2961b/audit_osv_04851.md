# [M] CVE-2025-12978

## Summary
Severity: Medium
Advisory: BIT-fluent-bit-2025-12978
Aliases: CVE-2025-12978
Ecosystem: Bitnami
Published: 2025-12-01
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2025-12978
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=4.1.0 <4.1.1

## Details
Fluent Bit in_http, in_splunk, and in_elasticsearch input plugins contain a flaw in the tag_key validation logic that fails to enforce exact key-length matching. This allows crafted inputs where a tag prefix is incorrectly treated as a full match. A remote attacker with authenticated or exposed access to these input endpoints can exploit this behavior to manipulate tags and redirect records to unintended destinations. This compromises the authenticity of ingested logs and can allow injection of forged data, alert flooding and routing manipulation.

## References
- https://fluentbit.io/announcements/v4.1.0/
- https://nvd.nist.gov/vuln/detail/CVE-2025-12978
