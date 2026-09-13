# [M] OpenSearch StackOverflow vulnerability

## Summary
Severity: Medium
Advisory: GHSA-6g3j-p5g6-992f
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-12-01
Source: https://github.com/advisories/GHSA-6g3j-p5g6-992f
Type: github-advisory

## Affected
- Maven: `org.opensearch:opensearch` — affected >=0 <1.3.14
- Maven: `org.opensearch:opensearch` — affected >=2.0.0 <2.11.1

## Details
### Impact
A flaw was discovered in OpenSearch, affecting the `_search` API that allowed a specially crafted query string to cause a Stack Overflow and ultimately a Denial of Service.

The issue was identified by Elastic Engineering and corresponds to security advisory [ESA-2023-14](https://discuss.elastic.co/t/elasticsearch-8-9-1-7-17-13-security-update/343297) (CVE-2023-31419).

### Mitigation
Versions 1.3.14 and 2.11.1 contain a fix for this issue.

### For more information
If you have any questions or comments about this advisory, please contact AWS/Amazon Security via our issue reporting page (https://aws.amazon.com/security/vulnerability-reporting/) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/opensearch-project/OpenSearch/security/advisories/GHSA-6g3j-p5g6-992f
- https://github.com/opensearch-project/OpenSearch
