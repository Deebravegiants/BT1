# [M] Exposure of sensitive information in Elasticsearch

## Summary
Severity: Medium
Advisory: GHSA-45h5-r968-5xr7
CVE: CVE-2021-22147
CWE: CWE-732, CWE-862
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-45h5-r968-5xr7
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=7.11.0 <7.14.0

## Details
A flaw was discovered in Elasticsearch where document and field level security was not applied to searchable snapshots. This could lead to an authenticated user gaining access to information that they are unauthorized to view.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2021-22147
- https://discuss.elastic.co/t/elastic-stack-7-14-0-security-update/280344
- https://security.netapp.com/advisory/ntap-20211008-0002
- https://www.elastic.co/community/security
