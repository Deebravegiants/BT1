# [M] Incorrect Authorization in Kibana Leading to Unauthorized Deletion of Synthetics Private Locations

## Summary
Severity: Medium
Advisory: BIT-elk-2026-72673
Aliases: BIT-kibana-2026-72673, CVE-2026-72673
Ecosystem: Bitnami
Published: 2026-08-19
Source: https://osv.dev/vulnerability/BIT-elk-2026-72673
Type: osv

## Affected
- Bitnami: `elk` — affected >=9.0.0 <9.4.4

## Details
Incorrect Authorization (CWE-863) in Kibana can lead to unauthorized deletion of Synthetics private locations via Accessing Functionality Not Properly Constrained by ACLs (CAPEC-1). Synthetics private locations can be shared with more than one space, and deleting one removes it from every space it is shared with. The safeguard that prevented the deletion of a private location still in use evaluated only the monitors visible in the requesting user's own space, so monitors that depend on the private location in other spaces were not taken into account. As a result, an authenticated Kibana user holding the Synthetics write privilege in a single space could delete a private location that other spaces still depend on, even where the user has no access to those spaces. Deleting the private location removes the shared configuration and stops the monitors in the other spaces from running, which suppresses the availability monitoring those spaces rely on.

## References
- https://discuss.elastic.co/t/kibana-8-19-20-and-9-4-4-security-update-esa-2026-90/389518
- https://nvd.nist.gov/vuln/detail/CVE-2026-72673
