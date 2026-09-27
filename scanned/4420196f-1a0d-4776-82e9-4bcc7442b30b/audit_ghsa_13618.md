# [H] OpenSearch uncontrolled resource consumption

## Summary
Severity: High
Advisory: GHSA-8wx3-324g-w4qq
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-8wx3-324g-w4qq
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=0 <1.3.14.0
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=2.0.0.0 <2.11.0.0

## Details
### Impact
An issue has been identified with how OpenSearch handled incoming requests on the HTTP layer. An unauthenticated user could force an OpenSearch node to exit with an OutOfMemory error by sending a moderate number of malformed HTTP requests.

The issue was identified by Elastic Engineering and corresponds to security advisory [ESA-2023-13](https://discuss.elastic.co/t/elasticsearch-8-9-0-7-17-13-security-update/343616) (CVE-2023-31418).

### Mitigation
Versions 1.3.14 and 2.11.0 contain a fix for this issue.

### For more information
If you have any questions or comments about this advisory, please contact AWS/Amazon Security via our issue reporting page (https://aws.amazon.com/security/vulnerability-reporting/) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-8wx3-324g-w4qq
- https://github.com/opensearch-project/security
