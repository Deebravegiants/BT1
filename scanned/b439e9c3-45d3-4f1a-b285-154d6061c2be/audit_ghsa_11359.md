# [M] Terraform Provider for ArgoCD has possible exposure to GO-2026-4337 / CVE-2025-68121

## Summary
Severity: Medium
Advisory: GHSA-594f-3595-c47v
CWE: CWE-1395, CWE-295
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-594f-3595-c47v
Type: github-advisory

## Affected
- Go: `github.com/argoproj-labs/terraform-provider-argocd` — affected >=0 <1.2.3-0.20260316182343-b3364f3f32e7

## Details
### Summary
The terraform-provider-argocd might have been vulnerable to GO-2026-4337 / CVE-2025-68121 ("Unexpected session resumption in crypto/tls").

### Details

See https://pkg.go.dev/vuln/GO-2026-4337 for the upstream vulnerability.

Provider versions starting with `v7.15.1` are using `go 1.25.8` for building and are thus no longer affected.

## References
- https://github.com/argoproj-labs/terraform-provider-argocd/security/advisories/GHSA-594f-3595-c47v
- https://github.com/argoproj-labs/terraform-provider-argocd/commit/b3364f3f32e70f1563c5f3162d370db704430294
- https://github.com/argoproj-labs/terraform-provider-argocd
