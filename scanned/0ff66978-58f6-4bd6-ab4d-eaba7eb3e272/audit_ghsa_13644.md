# [M] Google Sheets data source plugin for Grafana information disclosure vulnerability

## Summary
Severity: Medium
Advisory: GHSA-37x5-qpm8-53rq
CVE: CVE-2023-4457
CWE: CWE-209
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:N (CVSS_V3)
Published: 2023-10-16
Source: https://github.com/advisories/GHSA-37x5-qpm8-53rq
Type: github-advisory

## Affected
- Go: `github.com/grafana/google-sheets-datasource` — affected >=0.9.0 <1.2.2

## Details
Grafana is an open-source platform for monitoring and observability.

The Google Sheets data source plugin for Grafana, versions 0.9.0 to 1.2.2 are vulnerable to an information disclosure vulnerability.

The plugin did not properly sanitize error messages, making it potentially expose the Google Sheet API-key that is configured for the data source.

This vulnerability was fixed in version 1.2.2.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-4457
- https://github.com/grafana/google-sheets-datasource
- https://grafana.com/security/security-advisories/cve-2023-4457
