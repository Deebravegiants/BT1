# [M] Privilege Escalation Flaw in Elasticsearch

## Summary
Severity: Medium
Advisory: GHSA-hqqv-9x3v-mp7w
CVE: CVE-2020-7014
CWE: CWE-266, CWE-269
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H (CVSS_V3)
Published: 2021-03-18
Source: https://github.com/advisories/GHSA-hqqv-9x3v-mp7w
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=6.7.0 <6.8.8
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.0.0 <7.6.2

## Details
The fix for CVE-2020-7009 was found to be incomplete. Elasticsearch versions from 6.7.0 to 6.8.7 and 7.0.0 to 7.6.1 contain a privilege escalation flaw if an attacker is able to create API keys and also authentication tokens. An attacker who is able to generate an API key and an authentication token can perform a series of steps that result in an authentication token being generated with elevated privileges.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2020-7014
- https://security.netapp.com/advisory/ntap-20200619-0003
- https://www.elastic.co/community/security
