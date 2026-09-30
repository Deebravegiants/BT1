# [M] Missing Authorization in Kibana Fleet Plugin Leading to Cross-Space Agent Data Disclosure

## Summary
Severity: Medium
Advisory: BIT-elk-2026-78595
Aliases: BIT-kibana-2026-78595, CVE-2026-78595
Ecosystem: Bitnami
Published: 2026-09-09
Source: https://osv.dev/vulnerability/BIT-elk-2026-78595
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.5.0 <9.5.3

## Details
Missing Authorization in Kibana Leading to Information Disclosure / Missing Authorization (CWE-862) in the Kibana Fleet feature can lead to information disclosure via Privilege Abuse (CAPEC-122). An authenticated user holding read-level Fleet agent privileges in one Kibana space could enumerate agent metadata and access diagnostic content belonging to agents enrolled in other Kibana spaces.

## References
- https://discuss.elastic.co/t/kibana-9-4-6-9-5-3-security-update-esa-2026-153/390160
- https://nvd.nist.gov/vuln/detail/CVE-2026-78595
