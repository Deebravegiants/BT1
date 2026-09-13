# [M] Unintended Proxy or Intermediary ('Confused Deputy') in Kibana Leading to Unauthorized Information Exposure

## Summary
Severity: Medium
Advisory: BIT-elk-2026-49092
Aliases: BIT-kibana-2026-49092, CVE-2026-49092
Ecosystem: Bitnami
Published: 2026-07-28
Source: https://osv.dev/vulnerability/BIT-elk-2026-49092
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.4.0 <9.4.3

## Details
Unintended Proxy or Intermediary ('Confused Deputy') (CWE-441) in Kibana can lead to unauthorized information exposure via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). Under certain conditions, a lower-privileged user can cause data from sources they are not authorized to access to be processed using another user's privileges.

## References
- https://discuss.elastic.co/t/kibana-9-4-3-security-update-esa-2026-54/388553
- https://nvd.nist.gov/vuln/detail/CVE-2026-49092
