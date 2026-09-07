# [M] OpenSearch has issue with fine-grained access control of indices backing data streams

## Summary
Severity: Medium
Advisory: GHSA-wmx7-x4jp-9jgg
CVE: CVE-2022-41918
CWE: CWE-612, CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-wmx7-x4jp-9jgg
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=0 <1.3.7
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=2.0.0 <2.4.0

## Details
### Impact
There is an issue with the implementation of fine-grained access control rules (document-level security, field-level security and field masking) where they are not correctly applied to the indices that back data streams potentially leading to incorrect access authorization. This issue can only be triggered by authenticated users authorized to read those data streams which are backed by the impacted indexes. Additionally, existing privileged users cannot access random indexes within these clusters; they can only access indexes to which they have already been granted permission.

### Patches
OpenSearch 1.3.7 and 2.4.0 contain a fix for this issue.

### Workarounds
There is no recommended work around.

### For more information
If you have any questions or comments about this advisory, please contact AWS/Amazon Security via our issue reporting page (https://aws.amazon.com/security/vulnerability-reporting/) or directly via email to aws-security@amazon.com. Please do not create a public GitHub issue.

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-wmx7-x4jp-9jgg
- https://nvd.nist.gov/vuln/detail/CVE-2022-41918
- https://github.com/opensearch-project/security/commit/f7cc569c9d3fa5d5432c76c854eed280d45ce6f4
- https://github.com/opensearch-project/security
