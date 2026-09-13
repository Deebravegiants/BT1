# [M] Kibana Insufficiently Protected Credentials in the CrowdStrike Connector

## Summary
Severity: Medium
Advisory: BIT-elk-2025-37728
Aliases: BIT-kibana-2025-37728, CVE-2025-37728
Ecosystem: Bitnami
Published: 2025-10-09
Source: https://osv.dev/vulnerability/BIT-elk-2025-37728
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.1.0 <9.1.5

## Details
Insufficiently Protected Credentials in the Crowdstrike connector can lead to Crowdstrike credentials being leaked. A malicious user can access cached credentials from a Crowdstrike connector in another space by creating and running a Crowdstrike connector in a space to which they have access.

## References
- https://discuss.elastic.co/t/kibana-crowdstrike-connector-8-18-8-8-19-5-9-0-8-and-9-1-5-security-update-esa-2025-19/382455
- https://nvd.nist.gov/vuln/detail/CVE-2025-37728
