# [M] Field-level security issue with .keyword fields in OpenSearch

## Summary
Severity: Medium
Advisory: GHSA-v3cg-7r9h-r2g6
CVE: CVE-2023-23613
CWE: CWE-200
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-01-24
Source: https://github.com/advisories/GHSA-v3cg-7r9h-r2g6
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=0 <1.3.8
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=2.0.0 <2.5.0

## Details
### Advisory title: Field-level security issue with .keyword fields

### Affected versions:
OpenSearch 1.0.0-1.3.7 and 2.0.0-2.4.1

### Patched versions:
OpenSearch 1.3.8 and 2.5.0

### Impact:
There is an issue in the implementation of field-level security (FLS) and field masking where rules written to explicitly exclude fields are not correctly applied for certain queries that rely on their auto-generated .keyword fields.

This issue is only present for authenticated users with read access to the indexes containing the restricted fields.

### Workaround:
FLS rules that use explicit exclusions can be written to grant explicit access instead. Policies authored in this way are not subject to this issue.

### Patches:
OpenSearch versions 1.3.8 and 2.5.0 contain a fix for this issue.

### For more information:
If you have any questions or comments about this advisory, please contact AWS/Amazon Security via our issue reporting page (https://aws.amazon.com/security/vulnerability-reporting/) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-v3cg-7r9h-r2g6
- https://nvd.nist.gov/vuln/detail/CVE-2023-23613
- https://github.com/opensearch-project/OpenSearch/releases/tag/2.5.0
- https://github.com/opensearch-project/security
