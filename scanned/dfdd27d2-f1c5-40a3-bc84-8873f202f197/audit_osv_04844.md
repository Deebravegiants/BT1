# [C] Fluent Bit Memory Corruption Vulnerability

## Summary
Severity: Critical
Advisory: BIT-fluent-bit-2024-4323
Aliases: CVE-2024-4323
Ecosystem: Bitnami
Published: 2024-05-24
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2024-4323
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=2.0.7 <3.0.4

## Details
A memory corruption vulnerability in Fluent Bit versions 2.0.7 thru 3.0.3. This issue lies in the embedded http server’s parsing of trace requests and may result in denial of service conditions, information disclosure, or remote code execution.

## References
- https://github.com/fluent/fluent-bit/commit/9311b43a258352797af40749ab31a63c32acfd04
- https://tenable.com/security/research/tra-2024-17
- https://www.vicarius.io/vsociety/posts/linguistic-lumberjack-memory-corruption-in-fluent-bit-cve-2024-4323
- https://nvd.nist.gov/vuln/detail/CVE-2024-4323
- https://fluentbit.io/announcements/v3.0.4/
- https://fluentbit.io/blog/2024/05/21/statement-on-cve-2024-4323-and-its-fix/
