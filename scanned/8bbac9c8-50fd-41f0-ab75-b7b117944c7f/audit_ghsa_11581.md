# [M] Metricbeat Allocates Memory with Excessive Size Value Leading to Denial of Service

## Summary
Severity: Medium
Advisory: GHSA-5vrw-qjxw-89r5
CVE: CVE-2026-26931
CWE: CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-19
Source: https://github.com/advisories/GHSA-5vrw-qjxw-89r5
Type: github-advisory

## Affected
- Go: `github.com/elastic/beats/v7` — affected >=0 <7.0.0-alpha2.0.20260112100137-de072c4e371e

## Details
Memory Allocation with Excessive Size Value (CWE-789) in the Prometheus remote_write HTTP handler in Metricbeat can lead Denial of Service via Excessive Allocation (CAPEC-130).

## References
- https://nvd.nist.gov/vuln/detail/CVE-2026-26931
- https://github.com/elastic/beats/commit/de072c4e371eafeb2a42d65b9ad513f666e4ffd7
- https://discuss.elastic.co/t/metricbeat-8-19-13-9-2-5-security-update-esa-2026-09/385532
- https://github.com/elastic/beats
