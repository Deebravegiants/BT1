# [M] BIT-elasticsearch-2021-22145

## Summary
Severity: Medium
Advisory: BIT-elasticsearch-2021-22145
Aliases: CVE-2021-22145, GHSA-q394-h7f5-7f44
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2021-22145
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=7.10.0 <7.13.4

## Details
A memory disclosure vulnerability was identified in Elasticsearch 7.10.0 to 7.13.3 error reporting. A user with the ability to submit arbitrary queries to Elasticsearch could submit a malformed query that would result in an error message returned containing previously used portions of a data buffer. This buffer could contain sensitive information such as Elasticsearch documents or authentication details.

## References
- http://packetstormsecurity.com/files/163648/ElasticSearch-7.13.3-Memory-Disclosure.html
- https://discuss.elastic.co/t/elasticsearch-7-13-4-security-update/279177
- https://security.netapp.com/advisory/ntap-20210827-0006/
- https://www.oracle.com/security-alerts/cpuapr2022.html
- https://nvd.nist.gov/vuln/detail/CVE-2021-22145
- https://gist.github.com/lucasdrufva/f9c5d7c9e26ee087b736d727953afd34
