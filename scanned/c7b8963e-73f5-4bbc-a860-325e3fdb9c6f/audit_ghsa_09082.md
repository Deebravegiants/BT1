# [H] Fission runtime pods automount the fission-fetcher service-account token into the user function   container, granting function code namespace-wide secret / configmap read

## Summary
Severity: High
Advisory: GHSA-85g2-pmrx-r49q
CVE: CVE-2026-46617
CWE: CWE-250, CWE-269, CWE-538
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-85g2-pmrx-r49q
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.23.0

## Details
### Summary

Fission runtime pods were created with `ServiceAccountName: fission-fetcher`, and the `fission-fetcher` ServiceAccount was granted namespace-wide `get` on `secrets` and `configmaps` (it needs that to load function code, env vars, and config). The runtime pod's automounted token was reachable from inside the user's function container at `/var/run/secrets/kubernetes.io/serviceaccount/token`, so user-supplied function code inherited the same Kubernetes API privileges and could read any secret or configmap in the function's namespace — far beyond the `Function.spec.secrets` allowlist that the function specification suggests.

### Affected component

- `pkg/executor/executortype/poolmgr/gp_deployment.go:154-156` — pool-manager runtime pod `ServiceAccountName`.
- `pkg/executor/executortype/newdeploy/newdeploy.go:225-227` — new-deploy runtime pod `ServiceAccountName`.
- `pkg/utils/serviceaccount.go:51-64` — `fission-fetcher` RBAC: namespace-wide `get` on `secrets` / `configmaps`.

### Impact

A user able to deploy or update a function in any namespace where Fission runtime pods are scheduled could:

1. Read every secret in that namespace (TLS keys, OIDC client secrets, database credentials, cloud provider credentials).
2. Read every configmap in that namespace.
3. Use those credentials to pivot to other Kubernetes resources or external systems the secrets unlock.

This violates the principle that `Function.spec.secrets` is the authoritative declaration of which secrets a function can read.

### Root cause

The fetcher sidecar legitimately needs the SA token to call the Fission control plane and fetch package archives. Setting `ServiceAccountName: fission-fetcher` on the pod gives every container in the pod (including the user container) the automounted token. Kubernetes does not provide per-container service-account scoping inside a single pod, so the user container has to be moved into a separate identity / token-mount scheme.

### Fix

Released in [v1.23.0](https://github.com/fission/fission/releases/tag/v1.23.0):

- **PR #3366** (commit `fe1842ef`):
  - The user function container now sets `AutomountServiceAccountToken: false` at the container level (via projected-volume token suppression), so the user container no longer sees the pod's SA token even though the fetcher sidecar still does.
  - The fetcher sidecar retains its existing token mount (separate projected volume) since it needs cluster API access for its own work.
  - For the few legitimate use cases where a function needs its own Kubernetes API access, the user is expected to mount a different ServiceAccount via `Function.spec.podspec` with the minimum necessary RBAC (documented separately).

### Mitigation (until upgrade)

1. Restrict who can create / update `Function` and `Package` CRDs in your cluster — treat the ability to ship function code as equivalent to namespace-wide secret read.
2. Reduce the `fission-fetcher` ClusterRole / Role scope where possible (e.g. constrain it to specific named secrets via separate Role bindings).
3. Add NetworkPolicy egress rules denying function pods access to the Kubernetes API server (this blunts the token even if it leaks).

## References
- https://github.com/fission/fission/security/advisories/GHSA-85g2-pmrx-r49q
- https://nvd.nist.gov/vuln/detail/CVE-2026-46617
- https://github.com/fission/fission/pull/3366
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.23.0
