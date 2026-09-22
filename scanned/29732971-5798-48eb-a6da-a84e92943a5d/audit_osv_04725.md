# [M] Improperly Controlled Modification of Dynamically-Determined Object Attributes in Kibana Leading to Unauthorized Data Modification

## Summary
Severity: Medium
Advisory: BIT-elk-2026-72655
Aliases: BIT-kibana-2026-72655, CVE-2026-72655
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72655
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.0.0 <9.4.5

## Details
Improperly Controlled Modification of Dynamically-Determined Object Attributes (CWE-915) in the case management functionality of Elastic Security in Kibana can lead to unauthorized modification of case data by an authenticated user who has not been granted case editing privileges, via Manipulating User-Controlled Variables (CAPEC-77). Object attributes accepted by the case management API were not subject to the same authorization enforcement applied in the user interface, so a low-privileged user could alter case records they were only entitled to view.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-9-4-5-security-update-esa-2026-110/389523
- https://nvd.nist.gov/vuln/detail/CVE-2026-72655
