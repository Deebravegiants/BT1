# [H] Uncontrolled Resource Consumption in Kibana Leading to Denial of Service

## Summary
Severity: High
Advisory: BIT-elk-2026-26937
Aliases: BIT-kibana-2026-26937, CVE-2026-26937
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-elk-2026-26937
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.0.0 <9.2.5

## Details
Uncontrolled Resource Consumption (CWE-400) in the Timelion component in Kibana can lead Denial of Service via Input Data Manipulation (CAPEC-153)

## References
- https://discuss.elastic.co/t/kibana-8-19-11-9-2-5-security-update-esa-2026-15/385251
- https://nvd.nist.gov/vuln/detail/CVE-2026-26937
