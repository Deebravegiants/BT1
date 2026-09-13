# [H] BIT-elasticsearch-2021-22146

## Summary
Severity: High
Advisory: BIT-elasticsearch-2021-22146
Aliases: CVE-2021-22146
Ecosystem: Bitnami
Published: 2024-03-06
Source: https://osv.dev/vulnerability/BIT-elasticsearch-2021-22146
Type: osv

## Affected
- Bitnami: `elasticsearch` — affected >=7.13.3 <7.13.4

## Details
All versions of Elastic Cloud Enterprise has the Elasticsearch “anonymous” user enabled by default in deployed clusters. While in the default setting the anonymous user has no permissions and is unable to successfully query any Elasticsearch APIs, an attacker could leverage the anonymous user to gain insight into certain details of a deployed cluster.

## References
- http://packetstormsecurity.com/files/163655/Elasticsearch-ECE-7.13.3-Database-Disclosure.html
- https://discuss.elastic.co/t/elastic-cloud-enterprise-security-update/279180
- https://security.netapp.com/advisory/ntap-20210819-0005/
- https://nvd.nist.gov/vuln/detail/CVE-2021-22146
