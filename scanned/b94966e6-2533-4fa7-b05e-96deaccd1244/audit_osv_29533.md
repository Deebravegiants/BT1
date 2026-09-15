# [M] OpenSearch Dashboards Security Plugin improper validation of nextUrl can lead to external redirect

## Summary
Severity: Medium
Advisory: CVE-2024-43794
Aliases: GHSA-3fph-6cqp-5mfc
CVSS: 6.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:C/C:L/I:L/A:N)
Published: 2024-08-23
Source: https://osv.dev/vulnerability/CVE-2024-43794
Type: osv

## Details
OpenSearch Dashboards Security Plugin adds a configuration management UI for the OpenSearch Security features to OpenSearch Dashboards. Improper validation of the nextUrl parameter can lead to external redirect on login to OpenSearch-Dashboards for specially crafted parameters. A patch is available in 1.3.19 and 2.16.0 for this issue.

## References
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2024/43xxx/CVE-2024-43794.json
- https://github.com/opensearch-project/security-dashboards-plugin/security/advisories/GHSA-3fph-6cqp-5mfc
- https://nvd.nist.gov/vuln/detail/CVE-2024-43794
- https://github.com/opensearch-project/security-dashboards-plugin/commit/fc4f6a27c0c80881be9e8ed6b9259a25c3fa0e13
