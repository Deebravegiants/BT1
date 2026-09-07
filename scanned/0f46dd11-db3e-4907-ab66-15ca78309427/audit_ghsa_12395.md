# [M] Elasticsearch-hadoop Unsafe Deserialization

## Summary
Severity: Medium
Advisory: GHSA-rv74-m283-5j95
CVE: CVE-2023-46674
CWE: CWE-502
Ecosystem: Maven
CVSS: CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:U/C:L/I:H/A:H (CVSS_V3)
Published: 2023-12-05
Source: https://github.com/advisories/GHSA-rv74-m283-5j95
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch-hadoop` — affected >=0 <7.17.11
- Maven: `org.elasticsearch:elasticsearch-hadoop` — affected >=8.0.0 <8.9.0

## Details
An issue was identified that allowed the unsafe deserialization of java objects from hadoop or spark configuration properties that could have been modified by authenticated users. Elastic would like to thank Yakov Shafranovich, with Amazon Web Services for reporting this issue.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-46674
- https://discuss.elastic.co/t/elasticsearch-hadoop-7-17-11-8-9-0-security-update-esa-2023-28/348663
- https://github.com/elastic/elasticsearch-hadoop
