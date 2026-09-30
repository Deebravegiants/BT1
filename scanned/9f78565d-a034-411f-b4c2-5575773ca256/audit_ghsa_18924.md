# [C] Grafana Incorrect Privilege Assignment vulnerability

## Summary
Severity: Critical
Advisory: GHSA-w62r-7c53-fmc5
CVE: CVE-2025-41115
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2025-11-21
Source: https://github.com/advisories/GHSA-w62r-7c53-fmc5
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=12.0.0 <12.0.7
- Go: `github.com/grafana/grafana` — affected >=12.1.0 <12.1.4
- Go: `github.com/grafana/grafana` — affected >=12.2.0 <12.2.2
- Go: `github.com/grafana/grafana` — affected >=1.9.2-0.20250310110405-e6fdb746f235 <1.9.2-0.20251106142618-ca5d89812015

## Details
SCIM provisioning was introduced in Grafana Enterprise and Grafana Cloud in April to improve how organizations manage users and teams in Grafana by introducing automated user lifecycle management.

In Grafana versions 12.x where SCIM provisioning is enabled and configured, a vulnerability in user identity handling allows a malicious or compromised SCIM client to provision a user with a numeric externalId, which in turn could allow to override internal user IDs and lead to impersonation or privilege escalation.

This vulnerability applies only if all of the following conditions are met:
- `enableSCIM` feature flag set to true
- `user_sync_enabled` config option in the `[auth.scim]` block set to true

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-41115
- https://github.com/grafana/grafana/commit/ca5d89812015ef2db3acc62826f73650450b331e
- https://github.com/advisories/GHSA-w62r-7c53-fmc5
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/releases/tag/v12.0.7
- https://github.com/grafana/grafana/releases/tag/v12.1.4
- https://github.com/grafana/grafana/releases/tag/v12.2.2
- https://github.com/grafana/grafana/releases/tag/v12.3.0
- https://grafana.com/security/security-advisories/CVE-2025-41115
