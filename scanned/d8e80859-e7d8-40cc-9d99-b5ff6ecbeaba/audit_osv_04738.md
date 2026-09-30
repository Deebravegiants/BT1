# [M] Incorrect Authorization in Kibana Leading to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-elk-2026-82298
Aliases: BIT-kibana-2026-82298, CVE-2026-82298
Ecosystem: Bitnami
Published: 2026-09-09
Source: https://osv.dev/vulnerability/BIT-elk-2026-82298
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.3

## Details
Incorrect Authorization (CWE-863) in Kibana can lead to denial of service via Exploiting Incorrectly Configured Access Control Security Levels (CAPEC-180).

## References
- https://discuss.elastic.co/t/kibana-8-19-21-9-4-6-9-5-3-security-update-esa-2026-174/390162
- https://nvd.nist.gov/vuln/detail/CVE-2026-82298
