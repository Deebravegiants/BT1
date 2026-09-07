# [M] Elasticsearch Uncontrolled Resource Consumption vulnerability

## Summary
Severity: Medium
Advisory: GHSA-w5gg-2q56-6h4f
CVE: CVE-2024-23450
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-03-27
Source: https://github.com/advisories/GHSA-w5gg-2q56-6h4f
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.0.0 <7.17.19
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.0.0 <8.13.0

## Details
A flaw was discovered in Elasticsearch, where processing a document in a deeply nested pipeline on an ingest node could cause the Elasticsearch node to crash.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-23450
- https://discuss.elastic.co/t/elasticsearch-8-13-0-7-17-19-security-update-esa-2024-06/356314
- https://github.com/elastic/elasticsearch
- https://security.netapp.com/advisory/ntap-20240517-0010
- https://www.elastic.co/community/security
