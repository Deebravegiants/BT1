# [M] Grafana-Zabbix ReDoS vulnerability

## Summary
Severity: Medium
Advisory: GHSA-g4rr-88fc-26fj
CVE: CVE-2025-10630
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2025-09-19
Source: https://github.com/advisories/GHSA-g4rr-88fc-26fj
Type: github-advisory

## Affected
- Go: `github.com/alexanderzobnin/grafana-zabbix` — affected >=0 <6.0.0

## Details
Grafana is an open-source platform for monitoring and observability. Grafana-Zabbix is a plugin for Grafana allowing to visualize monitoring data from Zabbix and create dashboards for analyzing metrics and realtime monitoring. 

Versions 5.2.1 and below contained a ReDoS vulnerability via user-supplied regex query which could causes CPU usage to max out. This vulnerability is fixed in version 6.0.0.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-10630
- https://github.com/grafana/grafana-zabbix
- https://github.com/grafana/grafana-zabbix/releases/tag/v6.0.0
- https://grafana.com/security/security-advisories/cve-2025-10630
- https://pkg.go.dev/vuln/GO-2025-3976
