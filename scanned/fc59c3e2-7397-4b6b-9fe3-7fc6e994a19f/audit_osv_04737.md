# [M] Incorrect Authorization in Kibana Leading to Unauthorized Resource Consumption

## Summary
Severity: Medium
Advisory: BIT-elk-2026-82293
Aliases: BIT-kibana-2026-82293, CVE-2026-82293
Ecosystem: Bitnami
Published: 2026-09-08
Source: https://osv.dev/vulnerability/BIT-elk-2026-82293
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.2

## Details
Incorrect Authorization (CWE-863) in the Kibana machine learning feature can lead to unauthorized resource consumption via Exploiting Incorrectly Configured Access Control Security Levels (CAPEC-180). An authenticated user could invoke machine learning functionality beyond their authorization scope, consuming cluster resources they should not be able to reach.

## References
- https://discuss.elastic.co/t/kibana-8-19-21-9-4-6-9-5-2-security-update-esa-2026-169/390119
- https://nvd.nist.gov/vuln/detail/CVE-2026-82293
