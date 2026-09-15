# [M] Insufficiently Protected Credentials in Elasticsearch

## Summary
Severity: Medium
Advisory: GHSA-5fvx-2jj3-6mff
CVE: CVE-2021-22132
CWE: CWE-522
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-03-18
Source: https://github.com/advisories/GHSA-5fvx-2jj3-6mff
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.7.0 <7.10.2

## Details
Elasticsearch versions 7.7.0 to 7.10.1 contain an information disclosure flaw in the async search API. Users who execute an async search will improperly store the HTTP headers. An Elasticsearch user with the ability to read the .tasks index could obtain sensitive request headers of other users in the cluster. This issue is fixed in Elasticsearch 7.10.2

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22132
- https://discuss.elastic.co/t/elasticsearch-7-10-2-security-update/261164
- https://security.netapp.com/advisory/ntap-20210219-0004
- https://www.oracle.com/security-alerts/cpuapr2022.html
