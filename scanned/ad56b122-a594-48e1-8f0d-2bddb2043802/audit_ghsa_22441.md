# [H] Improper Privilege Management in Elasticsearch

## Summary
Severity: High
Advisory: GHSA-gfv5-grx2-9jw2
CVE: CVE-2020-7009
CWE: CWE-266, CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2022-05-24
Source: https://github.com/advisories/GHSA-gfv5-grx2-9jw2
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=6.7.0 <6.8.8
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.0.0 <7.6.2

## Details
Elasticsearch versions from 6.7.0 to 6.8.7 and 7.0.0 to 7.6.1 contain a privilege escalation flaw if an attacker is able to create API keys. An attacker who is able to generate an API key can perform a series of steps that result in an API key being generated with elevated privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7009
- https://discuss.elastic.co/t/elastic-stack-6-8-8-and-7-6-2-security-update/225920
- https://github.com/elastic/elasticsearch
- https://security.netapp.com/advisory/ntap-20200403-0004
- https://www.elastic.co/community/security
