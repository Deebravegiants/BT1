# [M] OpenSearch Issue with tenant read-only permissions

## Summary
Severity: Medium
Advisory: GHSA-72q2-gwwf-6hrv
CVE: CVE-2023-45807
CWE: CWE-281
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2023-10-17
Source: https://github.com/advisories/GHSA-72q2-gwwf-6hrv
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=2.0.0.0 <2.11.0.0
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=0 <1.3.14.0

## Details
### Impact
There is an issue with the implementation of tenant permissions in OpenSearch Dashboards where authenticated users with read-only access to a tenant can perform create, edit and delete operations on index metadata of dashboards and visualizations in that tenant, potentially rendering them unavailable.

This issue does not affect index data, only metadata. Dashboards correctly enforces read-only permissions when indexing and updating documents. This issue does not provide additional read access to data users don’t already have.

### Mitigation
This issue can be mitigated by disabling the tenants functionality for the cluster. Versions 1.3.14 and 2.11.0 contain a fix for this issue.

### For more information
If you have any questions or comments about this advisory, please contact AWS/Amazon Security via our issue reporting page (https://aws.amazon.com/security/vulnerability-reporting/) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-72q2-gwwf-6hrv
- https://nvd.nist.gov/vuln/detail/CVE-2023-45807
- https://github.com/opensearch-project/security
