# [M] Argo Workflows: SSO RBAC Delegation Nil Pointer Dereference DoS (gatekeeper.go)

## Summary
Severity: Medium
Advisory: BIT-argo-workflows-2026-42183
Aliases: CVE-2026-42183, GHSA-p4gq-3vxj-f4jq, GO-2026-5527
Ecosystem: Bitnami
Published: 2026-05-12
Source: https://osv.dev/vulnerability/BIT-argo-workflows-2026-42183
Type: osv

## Affected
- Bitnami: `argo-workflows` — affected >=4.0.0 <4.0.5

## Details
Argo Workflows is an open source container-native workflow engine for orchestrating parallel jobs on Kubernetes. From version 4.0.0 to before version 4.0.5, a nil pointer dereference in server/auth/gatekeeper.go rbacAuthorization() causes a panic (denial of service) for SSO users whose claims match a namespace-level RBAC rule but not an SSO-namespace rule, when SSO_DELEGATE_RBAC_TO_NAMESPACE=true. This issue has been patched in version 4.0.5.

## References
- https://github.com/argoproj/argo-workflows/commit/c4cc17d0c034fa9a9cc01ef1af6c8016c93071d4
- https://github.com/argoproj/argo-workflows/releases/tag/v4.0.5
- https://github.com/argoproj/argo-workflows/security/advisories/GHSA-p4gq-3vxj-f4jq
- https://nvd.nist.gov/vuln/detail/CVE-2026-42183
