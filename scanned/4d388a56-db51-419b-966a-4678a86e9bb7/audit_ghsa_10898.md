# [M] Grafana public dashboards disclose all direct mode datasources

## Summary
Severity: Medium
Advisory: GHSA-3q27-7qjq-p9c5
CVE: CVE-2026-27877
CWE: CWE-200, CWE-312
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-03-27
Source: https://github.com/advisories/GHSA-3q27-7qjq-p9c5
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=9.3.0
- Go: `github.com/grafana/grafana` — affected >=12.0.0
- Go: `github.com/grafana/grafana` — affected >=12.2.0
- Go: `github.com/grafana/grafana` — affected >=12.3.0
- Go: `github.com/grafana/grafana` — affected >=12.4.0
- Go: `github.com/grafana/grafana` — affected >=1.9.2-0.20221116104934-4ee83a5f2bf4 <1.9.2-0.20260325055210-3522153e07b4

## Details
When using public dashboards and direct data-sources, all direct data-sources' passwords are exposed despite not being used in dashboards.

No passwords of proxied data-sources are exposed. We encourage all direct data-sources to be converted to proxied data-sources as far as possible to improve your deployments' security.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-27877
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/cve-2026-27877
