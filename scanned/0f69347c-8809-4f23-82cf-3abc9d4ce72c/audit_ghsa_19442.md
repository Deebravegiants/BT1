# [M] Elasticsearch Potential Node Crash due to Large Recursion in `innerForbidCircularReferences` Function

## Summary
Severity: Medium
Advisory: GHSA-ghfh-p92w-j4mg
CVE: CVE-2024-52980
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-08
Source: https://github.com/advisories/GHSA-ghfh-p92w-j4mg
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.17.0 <8.15.1

## Details
A flaw was discovered in Elasticsearch, where a large recursion using the innerForbidCircularReferences function of the PatternBank class could cause the Elasticsearch node to crash.

A successful attack requires a malicious user to have read_pipeline Elasticsearch cluster privilege assigned to them.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52980
- https://github.com/elastic/elasticsearch/commit/4e5c6801f4d60f100f122072f6bf35b21fd722a5
- https://github.com/elastic/elasticsearch/commit/a02dc7165c75f12701f8d47a2bdefe5283735267
- https://discuss.elastic.co/t/elasticsearch-8-15-1-security-update-esa-2024-34/376919
- https://github.com/elastic/elasticsearch
