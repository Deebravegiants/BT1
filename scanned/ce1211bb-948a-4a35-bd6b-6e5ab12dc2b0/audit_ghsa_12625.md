# [C] Improper configuration of RBAC permissions obtaining cluster control permissions

## Summary
Severity: Critical
Advisory: GHSA-74j8-w7f9-pp62
CVE: CVE-2023-33190
CWE: CWE-287, CWE-863
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2023-06-30
Source: https://github.com/advisories/GHSA-74j8-w7f9-pp62
Type: github-advisory

## Affected
- Go: `github.com/labring/sealos` — affected >=0 <4.2.1-rc4

## Details
### Summary
Improper configuration of RBAC permissions resulted in obtaining cluster control permissions, which could control the entire cluster deployed with Sealos, as well as hundreds of pods and other resources within the cluster.

### Details
detail's is disable by publish.

### PoC
detail's is disable by publish.

### Impact
+ sealos public cloud user
+ CWE-287 Improper Authentication

## References
- https://github.com/labring/sealos/security/advisories/GHSA-74j8-w7f9-pp62
- https://nvd.nist.gov/vuln/detail/CVE-2023-33190
- https://github.com/labring/sealos/commit/4cdf52e55666864e5f90ed502e9fc13e18985b7b
- https://github.com/labring/sealos
