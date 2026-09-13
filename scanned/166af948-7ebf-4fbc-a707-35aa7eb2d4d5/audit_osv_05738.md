# [H] BIT-grafana-2022-32276

## Summary
Severity: High
Advisory: BIT-grafana-2022-32276
Aliases: CVE-2022-32276
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-grafana-2022-32276
Type: osv

## Affected
- Bitnami: `grafana` — affected >=8.4.3 <8.4.4

## Details
Grafana 8.4.3 allows unauthenticated access via (for example) a /dashboard/snapshot/*?orgId=0 URI. NOTE: the vendor considers this a UI bug, not a vulnerability

## References
- https://github.com/BrotherOfJhonny/grafana/blob/main/README.md
- https://github.com/grafana/grafana/issues/50336
- https://nvd.nist.gov/vuln/detail/CVE-2022-32276
