# [H] OpenSearch vulnerable to Improper Authorization of Index Containing Sensitive Information

## Summary
Severity: High
Advisory: GHSA-f4qr-f4xx-hjxw
CVE: CVE-2022-35980
CWE: CWE-612
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2022-08-12
Source: https://github.com/advisories/GHSA-f4qr-f4xx-hjxw
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=2.0.0.0 <2.2.0.0

## Details
### Impact
Requests to an OpenSearch cluster configured with advanced access control features ([document level security (DLS)](https://opensearch.org/docs/latest/security-plugin/access-control/document-level-security/), [field level security (FLS)](https://opensearch.org/docs/latest/security-plugin/access-control/field-level-security/), and/or [field masking](https://opensearch.org/docs/latest/security-plugin/access-control/field-masking/)) will not be filtered when the query's search pattern matches an aliased index.

OpenSearch Dashboards creates an alias to `.kibana` by default, so filters with the index pattern of `*` to restrict access to documents or fields will not be applied.

This issue allows requests to access sensitive information when customer have acted to restrict access that specific information. 

### Patches
OpenSearch 2.2.0+ contains the fix for this issue. OpenSearch Security Plugin 2.2.0.0 is compatible with OpenSearch 2.2.0.

### Workarounds
There is no recommended work around.

### References
See pull request #1999 for additional details.

### For more information
If you have any questions or comments about this advisory we ask that contact AWS/Amazon Security via our [vulnerability reporting page](http://aws.amazon.com/security/vulnerability-reporting/) or directly via email to aws-security@amazon.com. Please do **not** create a public GitHub issue.

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-f4qr-f4xx-hjxw
- https://nvd.nist.gov/vuln/detail/CVE-2022-35980
- https://github.com/opensearch-project/security/pull/1999
- https://github.com/opensearch-project/security/commit/7eaaafec2939d7db23a02ffca9cc68e0343de246
- https://github.com/opensearch-project/security
