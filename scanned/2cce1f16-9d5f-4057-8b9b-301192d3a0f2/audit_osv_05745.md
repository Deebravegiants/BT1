# [M] Grafana Alerting Editors can edit destination of webhooks they did not create

## Summary
Severity: Medium
Advisory: BIT-grafana-2025-12141
Aliases: CVE-2025-12141
Ecosystem: Bitnami
Published: 2026-04-18
Source: https://osv.dev/vulnerability/BIT-grafana-2025-12141
Type: osv

## Affected
- Bitnami: `grafana` — affected >=8.0.0 <12.3.1

## Details
In Grafana's alerting system, users with edit permissions for a contact point, specifically the permissions “alert.notifications:write” or “alert.notifications.receivers:test” that are granted as part of the fixed role "Contact Point Writer", which is part of the basic role Editor - can edit contact points created by other users, modify the endpoint URL to a controlled server. By invoking the test functionality, attackers can capture and extract redacted secure settings, such as authentication credentials for third-party services (e.g., Slack tokens). This leads to unauthorized access and potential compromise of external integrations.

## References
- https://grafana.com/security/security-advisories/cve-2025-12141/
- https://nvd.nist.gov/vuln/detail/CVE-2025-12141
