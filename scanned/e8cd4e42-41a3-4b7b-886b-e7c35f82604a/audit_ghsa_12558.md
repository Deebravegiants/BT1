# [H] Grafana Missing Synchronization vulnerability

## Summary
Severity: High
Advisory: GHSA-x2w4-c67p-g44j
CVE: CVE-2023-2801
CWE: CWE-662, CWE-820
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-06-06
Source: https://github.com/advisories/GHSA-x2w4-c67p-g44j
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0 <9.4.12
- Go: `github.com/grafana/grafana` — affected >=9.5.0 <9.5.3

## Details
Grafana is an open-source platform for monitoring and observability. 

Using public dashboards users can query multiple distinct data sources using mixed queries. However such query has a possibility of crashing a Grafana instance.

The only feature that uses mixed queries at the moment is public dashboards, but it's also possible to cause this by calling the query API directly.

This might enable malicious users to crash Grafana instances through that endpoint.

Users may upgrade to version 9.4.12 and 9.5.3 to receive a fix.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-2801
- https://github.com/grafana/grafana
- https://grafana.com/security/security-advisories/cve-2023-2801
- https://security.netapp.com/advisory/ntap-20230706-0002
