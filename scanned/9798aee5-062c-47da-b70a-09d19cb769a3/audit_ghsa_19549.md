# [M] Elasticsearch Vulnerable to Stack Overflow due to a Large Recursion

## Summary
Severity: Medium
Advisory: GHSA-5xm9-x7x4-4j5x
CVE: CVE-2024-52981
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-08
Source: https://github.com/advisories/GHSA-5xm9-x7x4-4j5x
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.17.0 <7.17.24
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.0.0-alpha1 <8.15.1

## Details
An issue was discovered in Elasticsearch, where a large recursion using the Well-KnownText formatted string with nested GeometryCollection objects could cause a stackoverflow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-52981
- https://github.com/elastic/elasticsearch/commit/097fc0654f9305e01402a06c82926bb04ebe5495
- https://github.com/elastic/elasticsearch/commit/91ddb124219a5be992644fcf78d7d061e4b7d44c
- https://github.com/elastic/elasticsearch/commit/f0948d38fdc811eca4a4b71dcb81a9b7dbb654b3
- https://discuss.elastic.co/t/elasticsearch-7-17-24-and-8-15-1-security-update-esa-2024-37/376924
- https://github.com/elastic/elasticsearch
