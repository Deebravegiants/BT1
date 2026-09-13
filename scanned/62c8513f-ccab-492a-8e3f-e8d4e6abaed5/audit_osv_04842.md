# [H] BIT-fluent-bit-2021-46879

## Summary
Severity: High
Advisory: BIT-fluent-bit-2021-46879
Aliases: CVE-2021-46879
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2021-46879
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=1.7.1 <1.7.2

## Details
An issue was discovered in Treasure Data Fluent Bit 1.7.1, a wrong variable is used to get the msgpack data resulting in a heap overflow in flb_msgpack_gelf_value_ext. An attacker can craft a malicious file and tick the victim to open the file with the software, triggering a heap overflow and execute arbitrary code on the target system.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=26851
- https://github.com/fluent/fluent-bit/pull/3100
- https://nvd.nist.gov/vuln/detail/CVE-2021-46879
