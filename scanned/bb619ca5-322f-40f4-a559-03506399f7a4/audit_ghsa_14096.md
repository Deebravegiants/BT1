# [M] OpenSearch issue with fine-grained access control during extremely rare race conditions

## Summary
Severity: Medium
Advisory: GHSA-g8xc-6mf7-h28h
CVE: CVE-2023-31141
CWE: CWE-863
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2023-05-09
Source: https://github.com/advisories/GHSA-g8xc-6mf7-h28h
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=1.0.0 <1.3.10.0
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=2.0.0 <2.7.0.0

## Details
### Impact
There is an issue with the implementation of fine-grained access control rules (document-level security, field-level security and field masking) where they are not correctly applied to the queries during extremely rare race conditions potentially leading to incorrect access authorization. For this issue to be triggered, two concurrent requests need to land on the same instance exactly when query cache eviction happens, once every four hours.

### Affected versions
OpenSearch 1.0.0-1.3.9 and 2.0.0-2.6.0

### Patched versions
OpenSearch 1.3.10 and 2.7.0

### For more information
If you have any questions or comments about this advisory, please contact AWS/Amazon Security via our issue reporting page (https://aws.amazon.com/security/vulnerability-reporting/) or directly via email to aws-security@amazon.com. Please do not create a public GitHub issue.

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-g8xc-6mf7-h28h
- https://nvd.nist.gov/vuln/detail/CVE-2023-31141
- https://github.com/opensearch-project/security
