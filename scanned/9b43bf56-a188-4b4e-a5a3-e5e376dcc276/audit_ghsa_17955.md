# [M] Helm Charts with Specific JSON Schema Values Can Cause Memory Exhaustion

## Summary
Severity: Medium
Advisory: GHSA-9h84-qmv7-982p
CVE: CVE-2025-55199
CWE: CWE-770
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2025-08-14
Source: https://github.com/advisories/GHSA-9h84-qmv7-982p
Type: github-advisory

## Affected
- Go: `helm.sh/helm/v3` — affected >=0 <3.18.5

## Details
A Helm contributor discovered that it was possible to craft a JSON Schema file in a manner which could cause Helm to use all available memory and have an out of memory (OOM) termination.

### Impact
A malicious chart can point `$ref` in _values.schema.json_ to a device (e.g. `/dev/*`) or other problem file which could cause Helm to use all available memory and have an out of memory (OOM) termination.

### Patches
This issue has been resolved in Helm v3.18.5.

### Workarounds
Make sure that all Helm charts that are being loaded into Helm doesn't have any reference of `$ref` pointing to `/dev/zero`.

### References
Helm's security policy is spelled out in detail in our [SECURITY](https://github.com/helm/community/blob/master/SECURITY.md) document.

### Credits
Disclosed by Jakub Ciolek at AlphaSense.

## References
- https://github.com/helm/helm/security/advisories/GHSA-9h84-qmv7-982p
- https://nvd.nist.gov/vuln/detail/CVE-2025-55199
- https://github.com/helm/helm/commit/b78692c18f0fb38fe5ba4571a674de067a4c53a5
- https://github.com/helm/helm
