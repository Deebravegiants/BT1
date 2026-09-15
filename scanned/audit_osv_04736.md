# [M] Missing Authorization in Kibana Leading to Unauthorized Cross-Space Write Operations

## Summary
Severity: Medium
Advisory: BIT-elk-2026-78596
Aliases: BIT-kibana-2026-78596, CVE-2026-78596
Ecosystem: Bitnami
Published: 2026-09-09
Source: https://osv.dev/vulnerability/BIT-elk-2026-78596
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.3

## Details
Missing Authorization in Kibana Leading to Unauthorized Modification of Data / Missing Authorization (CWE-862) in Kibana can lead to unauthorized modification of data via Privilege Abuse (CAPEC-122). An authenticated user holding Security read-level access in a single Kibana space could trigger Entity Analytics migration operations that perform privileged writes across all Kibana spaces, regardless of that user's actual access scope.

## References
- https://discuss.elastic.co/t/kibana-8-19-21-9-4-6-9-5-3-security-update-esa-2026-154/390161
- https://nvd.nist.gov/vuln/detail/CVE-2026-78596
