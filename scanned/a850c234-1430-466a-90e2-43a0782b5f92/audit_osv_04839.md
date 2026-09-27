# [H] BIT-fluent-bit-2021-27186

## Summary
Severity: High
Advisory: BIT-fluent-bit-2021-27186
Aliases: CVE-2021-27186
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-fluent-bit-2021-27186
Type: osv

## Affected
- Bitnami: `fluent-bit` — affected >=1.6.10 <1.6.11

## Details
Fluent Bit 1.6.10 has a NULL pointer dereference when an flb_malloc return value is not validated by flb_avro.c or http_server/api/v1/metrics.c.

## References
- https://github.com/fluent/fluent-bit/issues/3044
- https://github.com/fluent/fluent-bit/pull/3045
- https://github.com/fluent/fluent-bit/pull/3047
- https://nvd.nist.gov/vuln/detail/CVE-2021-27186
