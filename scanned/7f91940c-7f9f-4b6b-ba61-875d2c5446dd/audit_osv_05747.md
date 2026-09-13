# [M] BIT-grafana-2025-3580

## Summary
Severity: Medium
Advisory: BIT-grafana-2025-3580
Aliases: CVE-2025-3580
Ecosystem: Bitnami
Published: 2025-05-28
Source: https://osv.dev/vulnerability/BIT-grafana-2025-3580
Type: osv

## Affected
- Bitnami: `grafana` — affected >=12.0.0 <12.0.1

## Details
An access control vulnerability was discovered in Grafana OSS where an Organization administrator could permanently delete the Server administrator account. This vulnerability exists in the DELETE /api/org/users/ endpoint.

The vulnerability can be exploited when:

1. An Organization administrator exists

2. The Server administrator is either:

   - Not part of any organization, or
   - Part of the same organization as the Organization administrator
Impact:

- Organization administrators can permanently delete Server administrator accounts

- If the only Server administrator is deleted, the Grafana instance becomes unmanageable

- No super-user permissions remain in the system

- Affects all users, organizations, and teams managed in the instance

The vulnerability is particularly serious as it can lead to a complete loss of administrative control over the Grafana instance.

## References
- https://grafana.com/security/security-advisories/cve-2025-3580/
- https://nvd.nist.gov/vuln/detail/CVE-2025-3580
