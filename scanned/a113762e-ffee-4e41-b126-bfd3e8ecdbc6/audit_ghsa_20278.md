# [H] Improper Check for Unusual or Exceptional Conditions in Elasticsearch

## Summary
Severity: High
Advisory: GHSA-wh6w-69xc-5rq5
CVE: CVE-2022-23712
CWE: CWE-754
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-06-07
Source: https://github.com/advisories/GHSA-wh6w-69xc-5rq5
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.0.0 <8.2.1

## Details
A Denial of Service flaw was discovered in Elasticsearch 8.0.0 through 8.2.0. Using this vulnerability, an unauthenticated attacker could forcibly shut down an Elasticsearch node with a specifically formatted network request. Version 8.2.1 contains a patch.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2022-23712
- https://discuss.elastic.co/t/elastic-stack-7-17-4-and-8-2-1-security-update/305530
- https://github.com/elastic/elasticsearch
- https://security.netapp.com/advisory/ntap-20220707-0010
- https://www.elastic.co/community/security
