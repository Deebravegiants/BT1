# [M] Improper Validation of Specified Quantity in Input in Kibana Leading to Denial of Service

## Summary
Severity: Medium
Advisory: BIT-elk-2026-26934
Aliases: BIT-kibana-2026-26934, CVE-2026-26934
Ecosystem: Bitnami
Published: 2026-03-03
Source: https://osv.dev/vulnerability/BIT-elk-2026-26934
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.3.0 <9.3.1

## Details
Improper Validation of Specified Quantity in Input (CWE-1284) in Kibana can allow an authenticated attacker with view-only privileges to cause a Denial of Service via Input Data Manipulation (CAPEC-153). An attacker can send a specially crafted, malformed payload causing excessive resource consumption and resulting in Kibana becoming unresponsive or crashing.

## References
- https://discuss.elastic.co/t/kibana-8-19-12-9-2-6-9-3-1-security-update-esa-2026-12/385248
- https://nvd.nist.gov/vuln/detail/CVE-2026-26934
