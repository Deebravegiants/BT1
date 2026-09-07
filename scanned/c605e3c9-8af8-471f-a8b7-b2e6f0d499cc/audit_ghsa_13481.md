# [H] Elasticsearch vulnerable to Uncontrolled Resource Consumption

## Summary
Severity: High
Advisory: GHSA-2cqf-6xv9-f22w
CVE: CVE-2023-31418
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-26
Source: https://github.com/advisories/GHSA-2cqf-6xv9-f22w
Type: github-advisory

## Affected
- Maven: `org.elasticsearch:elasticsearch` — affected >=0 <7.17.13
- Maven: `org.elasticsearch:elasticsearch` — affected >=8.0.0 <8.9.0

## Details
An issue has been identified with how Elasticsearch handled incoming requests on the HTTP layer. An unauthenticated user could force an Elasticsearch node to exit with an OutOfMemory error by sending a moderate number of malformed HTTP requests. The issue was identified by Elastic Engineering and we have no indication that the issue is known or that it is being exploited in the wild.

## References
- https://nvd.nist.gov/vuln/detail/CVE-2023-31418
- https://discuss.elastic.co/t/elasticsearch-8-9-0-7-17-13-security-update/343616
- https://security.netapp.com/advisory/ntap-20231130-0005
- https://www.elastic.co/community/security
