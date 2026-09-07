# [M] Elasticsearch allocation of resources without limits or throttling leads to crash

## Summary
Severity: Medium
Advisory: GHSA-jgx4-7v3v-vwfm
CVE: CVE-2024-43709
CWE: CWE-770
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-01-21
Source: https://github.com/advisories/GHSA-jgx4-7v3v-vwfm
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=0 <7.17.21
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.0.0 <8.13.3

## Details
An allocation of resources without limits or throttling in Elasticsearch can lead to an OutOfMemoryError exception resulting in a crash via a specially crafted query using an SQL function.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2024-43709
- https://discuss.elastic.co/t/elasticsearch-7-17-21-and-8-13-3-security-update-esa-2024-25/373442
- https://github.com/elastic/elasticsearch
- https://security.netapp.com/advisory/ntap-20250221-0007
