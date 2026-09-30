# [M] Helm Allows A Specially Crafted JSON Schema To Cause A Stack Overflow

## Summary
Severity: Medium
Advisory: GHSA-5xqw-8hwv-wg92
CVE: CVE-2025-32387
CWE: CWE-121, CWE-674
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-10
Source: https://github.com/advisories/GHSA-5xqw-8hwv-wg92
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=0 <3.17.3

## Details
A Helm contributor discovered that a specially crafted JSON Schema within a chart can lead to a stack overflow.

### Impact
A JSON Schema file within a chart can be crafted with a deeply nested chain of references, leading to parser recursion that can exceed the stack size limit and trigger a stack overflow. 

### Patches
This issue has been resolved in Helm v3.17.3.

### Workarounds
Ensure that the JSON Schema within any charts loaded by Helm does not have a large number of nested references. These JSON Schema files are larger than 10 MiB.

### For more information
Helm's security policy is spelled out in detail in our [SECURITY](https://github.com/helm/community/blob/master/SECURITY.md) document.

### Credits
Disclosed by Jakub Ciolek at AlphaSense.

## References
- https://github.com/helm/helm/security/advisories/GHSA-5xqw-8hwv-wg92
- https://nvd.nist.gov/vuln/detail/CVE-2025-32387
- https://github.com/helm/helm/commit/d8ca55fc669645c10c0681d49723f4bb8c0b1ce7
- https://github.com/helm/helm
