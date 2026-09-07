# [M] Elasticsearch Improper Handling of Exceptional Conditions

## Summary
Severity: Medium
Advisory: GHSA-285m-vhfq-xx4h
CVE: CVE-2023-46673
CWE: CWE-755
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-11-22
Source: https://github.com/advisories/GHSA-285m-vhfq-xx4h
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.0.0 <7.17.14
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.0.0 <8.10.3

## Details
It was identified that malformed scripts used in the script processor of an Ingest Pipeline could cause an Elasticsearch node to crash when calling the Simulate Pipeline API.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46673
- https://discuss.elastic.co/t/elasticsearch-7-17-14-8-10-3-security-update-esa-2023-24/347708
- https://github.com/elastic/elasticsearch
- https://www.elastic.co/community/security
