# [M] Grafana's datasource proxy API allows authorization checks to be bypassed

## Summary
Severity: Medium
Advisory: GHSA-9j65-rv5x-4vrf
CVE: CVE-2025-3454
CWE: CWE-285
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-06-02
Source: https://github.com/advisories/GHSA-9j65-rv5x-4vrf
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana` — affected >=0.0.0-20210414170620-dadccdda06e6 <0.0.0-20250424191517-1f707d16ed5d

## Details
This vulnerability in Grafana's datasource proxy API allows authorization checks to be bypassed by adding an extra slash character in the URL path.

Users with minimal permissions could gain unauthorized read access to GET endpoints in Alertmanager and Prometheus datasources.

The issue primarily affects datasources that implement route-specific permissions, including Alertmanager and certain Prometheus-based datasources.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-3454
- https://github.com/grafana/grafana
- https://github.com/grafana/grafana/blob/be8d153dc33734caba4f617ff571d18253e68fa0/CHANGELOG.md#10417security-01-2025-04-22
- https://grafana.com/blog/2025/04/22/grafana-security-release-medium-and-high-severity-fixes-for-cve-2025-3260-cve-2025-2703-cve-2025-3454
- https://grafana.com/security/security-advisories/cve-2025-3454
