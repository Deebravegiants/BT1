# [C] BIT-fluent-bit-2021-36088

## Summary
Severity: Critical
Advisory: BIT-fluent-bit-2021-36088
Aliases: CVE-2021-36088
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2021-36088
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=1.7.0 <1.7.5

## Details
Fluent Bit (aka fluent-bit) 1.7.0 through 1.7.4 has a double free in flb_free (called from flb_parser_json_do and flb_parser_do).

## References
- https://bugs.chromium.org/p/oss-fuzz/issues/detail?id=33750
- https://github.com/fluent/fluent-bit/commit/22346a74c07ceb90296be872be2d53eb92252a54
- https://github.com/fluent/fluent-bit/pull/3453
- https://github.com/google/oss-fuzz-vulns/blob/main/vulns/fluent-bit/OSV-2021-702.yaml
- https://nvd.nist.gov/vuln/detail/CVE-2021-36088
