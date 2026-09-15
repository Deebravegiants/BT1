# [M] Broken access control in dashboard snapshots

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-19197
Aliases: CVE-2026-19197
Ecosystem: Bitnami
Published: 2026-09-02
Source: https://osv.dev/vulnerability/BIT-grafana-2026-19197
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.1.0 <13.1.3

## Details
A user with organization administrator permissions can delete dashboard snapshots belonging to other organizations on the same Grafana instance, and can recover a snapshot's secret delete key using only its public share key (broken access control).

## References
- https://grafana.com/security/security-advisories/cve-2026-19197
- https://nvd.nist.gov/vuln/detail/CVE-2026-19197
