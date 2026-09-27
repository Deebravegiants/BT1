# [H] Dashboard Import Overwrites ACL — Editor Privilege Escalation to Dashboard Admin

## Summary
Severity: High
Advisory: BIT-grafana-2026-33377
Aliases: CVE-2026-33377
Ecosystem: Bitnami
Published: 2026-05-15
Source: https://osv.dev/vulnerability/BIT-grafana-2026-33377
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.0.1

## Details
An Editor can overwrite a dashboard not owned by them to acquire admin on that specific dashboard. The user must have write access to the dashboard to escalate privilege.

## References
- https://grafana.com/security/security-advisories/cve-2026-33377
- https://nvd.nist.gov/vuln/detail/CVE-2026-33377
