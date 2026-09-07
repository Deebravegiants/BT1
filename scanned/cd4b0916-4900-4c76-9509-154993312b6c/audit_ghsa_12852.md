# [M] Issue with whitespace in JWT roles in OpenSearch

## Summary
Severity: Medium
Advisory: GHSA-864v-6qj7-62qj
CVE: CVE-2023-23612
CWE: CWE-269, CWE-287
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:L/I:L/A:L (CVSS_V3)
Published: 2023-01-24
Source: https://github.com/advisories/GHSA-864v-6qj7-62qj
Type: github-advisory

## Affected
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=0 <1.3.8
- Maven: `org.opensearch.plugin:opensearch-security` — affected >=2.0.0 <2.5.0

## Details
### Advisory title: Issue with whitespace in JWT roles

### Affected versions:
OpenSearch 1.0.0-1.3.7 and 2.0.0-2.4.1

### Patched versions:
OpenSearch 1.3.8 and 2.5.0

### Impact:
OpenSearch uses JWTs to store role claims obtained from the Identity Provider (IdP) when the authentication backend is SAML or OpenID Connect. There is an issue in how those claims are processed from the JWTs where the leading and trailing whitespace is trimmed, allowing users to potentially claim roles they are not assigned to if any role matches the whitespace-stripped version of the roles they are a member of.

This issue is only present for authenticated users, and it requires either the existence of roles that match, not considering leading/trailing whitespace, or the ability for users to create said matching roles. In addition, the Identity Provider must allow leading and trailing spaces in role names.

### Patches:
OpenSearch versions 1.3.8 and 2.5.0 contain a fix for this issue.

### For more information:
If you have any questions or comments about this advisory, please contact AWS/Amazon Security via our issue reporting page (https://aws.amazon.com/security/vulnerability-reporting/) or directly via email to [aws-security@amazon.com](mailto:aws-security@amazon.com). Please do not create a public GitHub issue.

## References
- https://github.com/opensearch-project/security/security/advisories/GHSA-864v-6qj7-62qj
- https://nvd.nist.gov/vuln/detail/CVE-2023-23612
- https://github.com/opensearch-project/OpenSearch/releases/tag/2.5.0
- https://github.com/opensearch-project/security
