# [M] Elasticsearch Incorrect Authorization vulnerability

## Summary
Severity: Medium
Advisory: GHSA-5mpw-4546-2wcr
CVE: CVE-2024-12539
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2024-12-17
Source: https://github.com/advisories/GHSA-5mpw-4546-2wcr
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.16.0 <8.16.2

## Details
An issue was discovered where improper authorization controls affected certain queries that could allow a malicious actor to circumvent Document Level Security in Elasticsearch and get access to documents that their roles would normally not allow.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-12539
- https://discuss.elastic.co/t/elasticsearch-8-16-2-8-17-0-security-update/372091
- https://github.com/elastic/elasticsearch
