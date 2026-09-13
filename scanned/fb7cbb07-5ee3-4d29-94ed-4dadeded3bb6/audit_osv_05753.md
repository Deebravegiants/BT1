# [M] CVE-2026-17033 CVE Record

## Summary
Severity: Medium
Advisory: BIT-grafana-2026-17033
Aliases: CVE-2026-17033
Ecosystem: Bitnami
Published: 2026-08-28
Source: https://osv.dev/vulnerability/BIT-grafana-2026-17033
Type: osv

## Affected
- Bitnami: `grafana` — affected >=13.0.0 <13.1.0

## Details
An authenticated attacker with Editor access or alert.instances.external:write can submit an external Alertmanager alert containing a controlled generatorURL. The attacker is authorized to create the alert, but not to execute script in another user's Grafana session.

Grafana renders alert.generatorURL directly as the Alert Details See source LinkButton href without URL-scheme sanitization or a safe-protocol allowlist. The click interceptor's :// heuristic can be bypassed by placing :// inside a JavaScript comment. When a user with read access clicks See source, the browser executes attacker-controlled JavaScript in the Grafana origin with the clicking user's permissions.

## References
- https://grafana.com/security/security-advisories/cve-2026-17033
- https://nvd.nist.gov/vuln/detail/CVE-2026-17033
