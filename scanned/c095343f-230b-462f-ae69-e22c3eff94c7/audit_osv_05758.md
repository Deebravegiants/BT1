# [H] Dashboard Permissions Scope Bypass Enables Cross‑Dashboard Privilege Escalation

## Summary
Severity: High
Advisory: BIT-grafana-2026-21721
Aliases: CVE-2026-21721
Ecosystem: Bitnami
Published: 2026-02-20
Source: https://osv.dev/vulnerability/BIT-grafana-2026-21721
Type: osv

## Affected
- Bitnami: `grafana` — affected >=12.3.0 <12.3.1

## Details
The dashboard permissions API does not verify the target dashboard scope and only checks the dashboards.permissions:* action. As a result, a user who has permission management rights on one dashboard can read and modify permissions on other dashboards. This is an organization‑internal privilege escalation.

## References
- https://grafana.com/security/security-advisories/CVE-2026-21721
- https://nvd.nist.gov/vuln/detail/CVE-2026-21721
- https://grafana.com/security/security-advisories/cve-2026-21721
- https://access.redhat.com/errata/RHSA-2026:2914
- https://access.redhat.com/errata/RHSA-2026:2920
- https://access.redhat.com/errata/RHSA-2026:3078
- https://access.redhat.com/errata/RHSA-2026:3529
- https://access.redhat.com/errata/RHSA-2026:5633
- https://access.redhat.com/errata/RHSA-2026:8229
- https://access.redhat.com/security/cve/CVE-2026-21721
- https://bugzilla.redhat.com/show_bug.cgi?id=2433242
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-21721.json
- https://access.redhat.com/errata/RHSA-2026:40138
- https://access.redhat.com/errata/RHSA-2026:41064
