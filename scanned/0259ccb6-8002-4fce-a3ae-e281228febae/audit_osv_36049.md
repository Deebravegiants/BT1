# [H] Missing Authorization in Execute Monitor API in OpenSearch Alerting Plugin

## Summary
Severity: High
Advisory: CVE-2026-19311
Aliases: GHSA-xxpg-q3wh-685q
CVSS: 7.5 (CVSS:4.0/AV:N/AC:L/AT:N/PR:L/UI:N/VC:H/VI:H/VA:N/SC:N/SI:N/SA:N)
Published: 2026-08-12
Source: https://osv.dev/vulnerability/CVE-2026-19311
Type: osv

## Details
Missing authorization in the Execute Monitor API in Amazon OpenSearch Alerting plugin might allow an authenticated remote user to read, modify, or delete arbitrary index data via a crafted inline monitor request with unintentional data source and input index parameters.

## References
- https://aws.amazon.com/about-aws/whats-new/2026/03/amazon-opensearch-service-version-3-5/
- https://aws.amazon.com/security/security-bulletins/2026-078-aws/
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/19xxx/CVE-2026-19311.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-19311
- https://github.com/opensearch-project/alerting/security/advisories/GHSA-xxpg-q3wh-685q
