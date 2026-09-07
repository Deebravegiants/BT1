# [M] Argo CD GitOps Engine does not scrub secret values from patch errors

## Summary
Severity: Medium
Advisory: GHSA-274v-mgcv-cm8j
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2025-01-30
Source: https://github.com/advisories/GHSA-274v-mgcv-cm8j
Type: github-advisory

## Affected
- Go: `github.com/argoproj/gitops-engine` — affected >=0.7.2
- Go: `github.com/argoproj/gitops-engine` — affected >=0 <0.7.1-0.20250129155113-4c6e03c463141

## Details
### Impact
A vulnerability was discovered in Argo CD that exposed secret values in error messages and the diff view when an invalid Kubernetes Secret resource was synced from a repository. 

The vulnerability assumes the user has write access to the repository and can exploit it, either intentionally or unintentionally, by committing an invalid Secret to repository and triggering a Sync. Once exploited, any user with read access to Argo CD can view the exposed secret data.

### Patches
A patch for this vulnerability is available in the following Argo CD versions:
- v2.13.4
- v2.12.10
- v2.11.13

### Workarounds
There is no workaround other than upgrading.

### Resources
Fixed with commit https://github.com/argoproj/argo-cd/commit/6f5537bdf15ddbaa0f27a1a678632ff0743e4107 & https://github.com/argoproj/gitops-engine/commit/7e21b91e9d0f64104c8a661f3f390c5e6d73ddca

## References
- https://github.com/argoproj/argo-cd/security/advisories/GHSA-47g2-qmh2-749v
- https://github.com/argoproj/gitops-engine/security/advisories/GHSA-274v-mgcv-cm8j
- https://github.com/argoproj/argo-cd/commit/6f5537bdf15ddbaa0f27a1a678632ff0743e4107
- https://github.com/argoproj/gitops-engine/commit/7e21b91e9d0f64104c8a661f3f390c5e6d73ddca
- https://github.com/argoproj/gitops-engine
- https://pkg.go.dev/vuln/GO-2025-3437
