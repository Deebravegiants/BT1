# [H] Grafana's users with permissions to create a data source can CRUD all data sources

## Summary
Severity: High
Advisory: GHSA-5mxf-42f5-j782
CVE: CVE-2024-1442
CWE: CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2024-03-07
Source: https://github.com/advisories/GHSA-5mxf-42f5-j782
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=8.5.0 <9.5.7
- Go: `github.com/grafana/grafana` — affected >=10.0.0 <10.0.12
- Go: `github.com/grafana/grafana` — affected >=10.1.0 <10.1.8
- Go: `github.com/grafana/grafana` — affected >=10.2.0 <10.2.5
- Go: `github.com/grafana/grafana` — affected >=10.3.0 <10.3.4

## Details
A user with the permissions to create a data source can use Grafana API to create a data source with UID set to *.
Doing this will grant the user access to read, query, edit and delete all data sources within the organization.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-1442
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/cve-2024-1442
- https://security.netapp.com/advisory/ntap-20241122-0007
