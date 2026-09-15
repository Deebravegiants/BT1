# [M] MongoDB Server may be susceptible to DoS due to Accumulated Memory Allocation

## Summary
Severity: Medium
Advisory: BIT-mongodb-2025-6712
Aliases: CVE-2025-6712
Ecosystem: Bitnami
Published: 2025-10-05
Source: https://osv.dev/vulnerability/BIT-mongodb-2025-6712
Type: osv

## Affected
- Bitnami: `mongodb` — affected >=8.0.0 <8.0.10

## Details
MongoDB Server may be susceptible to disruption caused by high memory usage, potentially leading to server crash. This condition is linked to inefficiencies in memory management related to internal operations. In scenarios where certain internal processes persist longer than anticipated, memory consumption can increase, potentially impacting server stability and availability. This issue affects MongoDB Server v8.0 versions prior to 8.0.10

## References
- https://jira.mongodb.org/browse/SERVER-106751
- https://nvd.nist.gov/vuln/detail/CVE-2025-6712
