# [H] Improper Input Validation in Kibana Leading to Denial of Service

## Summary
Severity: High
Advisory: BIT-kibana-2026-26935
Aliases: BIT-elk-2026-26935, CVE-2026-26935
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-kibana-2026-26935
Type: osv

## Affected
- Bitnami: `kibana` — affected >=9.3.0 <9.3.1

## Details
Improper Input Validation (CWE-20) in the internal Content Connectors search endpoint in Kibana can lead Denial of Service via Input Data Manipulation (CAPEC-153)

## References
- https://discuss.elastic.co/t/kibana-8-19-12-9-2-6-9-3-1-security-update-esa-2026-13/385249
- https://nvd.nist.gov/vuln/detail/CVE-2026-26935
