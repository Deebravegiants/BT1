# [H] BIT-fluent-bit-2020-35963

## Summary
Severity: High
Advisory: BIT-fluent-bit-2020-35963
Aliases: CVE-2020-35963
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2020-35963
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=0 <1.6.4

## Details
flb_gzip_compress in flb_gzip.c in Fluent Bit before 1.6.4 has an out-of-bounds write because it does not use the correct calculation of the maximum gzip data-size expansion.

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=27261
- https://fluentbit.io/announcements/v1.6.4/
- https://github.com/fluent/fluent-bit/commit/cadff53c093210404aed01c4cf586adb8caa07af
- https://nvd.nist.gov/vuln/detail/CVE-2020-35963
