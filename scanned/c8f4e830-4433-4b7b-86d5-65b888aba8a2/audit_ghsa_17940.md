# [M] Grafana Infinity Datasource Plugin SSRF Vulnerability

## Summary
Severity: Medium
Advisory: GHSA-3c93-92r7-j934
CVE: CVE-2025-8341
CWE: CWE-918
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:L/I:N/A:N (CVSS_V3)
Published: 2025-08-04
Source: https://github.com/advisories/GHSA-3c93-92r7-j934
Type: github-advisory

## Affected
- Go: `github.com/grafana/grafana-infinity-datasource` — affected >=0 <1.4.2-0.20250731100004-9c736aa21b3a

## Details
Grafana is an open-source platform for monitoring and observability. The Infinity datasource plugin, maintained by Grafana Labs, allows visualizing data from JSON, CSV, XML, GraphQL, and HTML endpoints.


If the plugin was configured to allow only certain URLs, an attacker could bypass this restriction using a specially crafted URL. This vulnerability is fixed in version 3.4.1.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2025-8341
- https://github.com/grafana/grafana-infinity-datasource/commit/9c736aa21b3a669d3070d3f5f80d949326fafa77
- https://github.com/grafana/grafana-infinity-datasource
- https://github.com/grafana/grafana-infinity-datasource/releases/tag/v3.4.1
- https://grafana.com/security/security-advisories/cve-2025-8341
