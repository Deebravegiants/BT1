# [M] Helm Allows A Specially Crafted Chart Archive To Cause Out Of Memory Termination

## Summary
Severity: Medium
Advisory: GHSA-4hfp-h4cw-hj8p
CVE: CVE-2025-32386
CWE: CWE-770, CWE-789
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-04-10
Source: https://github.com/advisories/GHSA-4hfp-h4cw-hj8p
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=0 <3.17.3

## Details
A Helm contributor discovered that a specially crafted chart archive file can cause Helm to use all available memory and have an out of memory (OOM) termination.

### Impact
A chart archive file can be crafted in a manner where it expands to be significantly larger uncompressed than compressed (e.g., >800x difference). When Helm loads this specially crafted chart, memory can be exhausted causing the application to terminate.

### Patches
This issue has been resolved in Helm v3.17.3.

### Workarounds
Ensure that any chart archive files being loaded by Helm do not contain files that are large enough to cause the Helm Client or SDK to use up available memory leading to a termination.

### For more information
Helm's security policy is spelled out in detail in our [SECURITY](https://github.com/helm/community/blob/master/SECURITY.md) document.

### Credits
Disclosed by Jakub Ciolek at AlphaSense.

## References
- https://github.com/helm/helm/security/advisories/GHSA-4hfp-h4cw-hj8p
- https://nvd.nist.gov/vuln/detail/CVE-2025-32386
- https://github.com/helm/helm/commit/d8ca55fc669645c10c0681d49723f4bb8c0b1ce7
- https://github.com/helm/helm
