# [H] BIT-fluent-bit-2021-46878

## Summary
Severity: High
Advisory: BIT-fluent-bit-2021-46878
Aliases: CVE-2021-46878
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2021-46878
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=1.7.1 <1.7.2

## Details
An issue was discovered in Treasure Data Fluent Bit 1.7.1, erroneous parsing in flb_pack_msgpack_to_json_format leads to type confusion bug that interprets whatever is on the stack as msgpack maps and arrays, leading to use-after-free. This can be used by an attacker to craft a specially craft file and trick the victim opening it using the affect software, triggering use-after-free and execute arbitrary code on the target system.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=27742
- https://github.com/fluent/fluent-bit/pull/3115
- https://nvd.nist.gov/vuln/detail/CVE-2021-46878
