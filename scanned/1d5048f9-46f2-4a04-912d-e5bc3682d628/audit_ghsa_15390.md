# [M] Grafana plugin data sources vulnerable to access control bypass

## Summary
Severity: Medium
Advisory: GHSA-hh8p-374f-qgr5
CVE: CVE-2024-6322
CWE: CWE-266
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:C/C:N/I:L/A:L (CVSS_V3)
Published: 2024-08-20
Source: https://github.com/advisories/GHSA-hh8p-374f-qgr5
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=11.1.0 <11.1.1
- Go: `github.com/grafana/grafana` — affected >=11.1.2 <11.1.3
- Go: `github.com/grafana/grafana` — affected >=0.0.0-20240521130516-0072e4a92d89 <0.0.0-20240725142242-c326d865c58b
- Go: `github.com/grafana/grafana` — affected >=1.9.2-0.20240521130516-0072e4a92d89 <1.9.2-0.20240725142242-c326d865c58b

## Details
Access control for plugin data sources protected by the ReqActions json field of the plugin.json is bypassed if the user or service account is granted associated access to any other data source, as the ReqActions check was not scoped to each specific datasource. The account must have prior query access to the impacted datasource.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-6322
- https://github.com/grafana/grafana/commit/4cb3ba5d1a7ab8b9676034e89dada2fcde1766ef
- https://github.com/grafana/grafana/commit/9cdba084a9100c6b11d32eef9d2bd53656c6964a
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/cve-2024-6322
