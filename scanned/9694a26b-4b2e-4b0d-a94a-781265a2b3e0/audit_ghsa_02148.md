# [M] Denial of Service in Elasticsearch

## Summary
Severity: Medium
Advisory: GHSA-3393-hvrj-w7v3
CVE: CVE-2021-22144
CWE: CWE-674
Ecosystem: Maven
CVSS: CVSS:3.1/AV:A/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2021-08-09
Source: https://github.com/advisories/GHSA-3393-hvrj-w7v3
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=0 <6.8.17
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.0.0-alpha1 <7.13.3

## Details
In Elasticsearch versions before 7.13.3 and 6.8.17 an uncontrolled recursion vulnerability that could lead to a denial of service attack was identified in the Elasticsearch Grok parser. A user with the ability to submit arbitrary queries to Elasticsearch could create a malicious Grok query that will crash the Elasticsearch node.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22144
- https://discuss.elastic.co/t/elasticsearch-7-13-3-and-6-8-17-security-update/278100
- https://security.netapp.com/advisory/ntap-20210827-0006
- https://www.oracle.com/security-alerts/cpuapr2022.html
