# [M] OpenSearch has time discrepancy in authentication responses

## Summary
Severity: Medium
Advisory: GHSA-c6wg-cm5x-rqvj
CVE: CVE-2023-25806
CWE: CWE-203, CWE-208
Ecosystem: Maven
CVSS: CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N (CVSS_V3)
Published: 2023-03-07
Source: https://github.com/advisories/GHSA-c6wg-cm5x-rqvj
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=0 <1.3.9
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=2.0.0 <2.6.0

## Details
### Impact
There is an observable discrepancy in the authentication response time between calls where the user provided exists and calls where it does not. This issue only affects calls using the internal basic identity provider (IdP), and not other externally configured IdPs.

### Patches
OpenSearch 1.3.9 and 2.6.0

### Workarounds
None.

### References
If you have any questions or comments about this advisory, please contact AWS/Amazon Security using our issue reporting page [1] or directly via email [2]. Please do not create a public GitHub issue.

[1] AWS Security issue reporting page: https://aws.amazon.com/security/vulnerability-reporting/
[2] AWS Security email: [aws-security@amazon.com](mailto:aws-security@amazon.com)

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-c6wg-cm5x-rqvj
- https://nvd.nist.gov/vuln/detail/CVE-2023-25806
- https://github.com/opensearch-project/security/pull/2472
- https://github.com/opensearch-project/security
