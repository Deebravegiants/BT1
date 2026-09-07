# [M] Elasticsearch vulnerable to stack overflow in the search API

## Summary
Severity: Medium
Advisory: GHSA-qwrx-45xf-jjf7
CVE: CVE-2023-31419
CWE: CWE-121, CWE-787
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-26
Source: https://github.com/advisories/GHSA-qwrx-45xf-jjf7
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.0.0 <7.17.13
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.0.0 <8.9.1

## Details
A flaw was discovered in Elasticsearch affecting the `_search` API that allowed a specially crafted query string to cause a stack overflow and ultimately a denial of service.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31419
- https://discuss.elastic.co/t/elasticsearch-8-9-1-7-17-13-security-update/343297
- https://security.netapp.com/advisory/ntap-20231116-0010
- https://www.elastic.co/community/security
