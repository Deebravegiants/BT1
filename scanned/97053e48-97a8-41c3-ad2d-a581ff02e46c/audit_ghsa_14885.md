# [M] Elasticsearch StackOverflow vulnerability

## Summary
Severity: Medium
Advisory: GHSA-4q22-422g-m4pj
CVE: CVE-2024-37280
CWE: CWE-122, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-06-13
Source: https://github.com/advisories/GHSA-4q22-422g-m4pj
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.13.1 <8.14.0

## Details
A flaw was discovered in Elasticsearch, affecting document ingestion when an index template contains a dynamic field mapping of “passthrough” type. Under certain circumstances, ingesting documents in this index would cause a StackOverflow exception to be thrown and ultimately lead to a Denial of Service. Note that passthrough fields is an experimental feature.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-37280
- https://discuss.elastic.co/t/elasticsearch-8-14-0-security-update-esa-2024-14/361007
- https://github.com/elastic/elasticsearch
