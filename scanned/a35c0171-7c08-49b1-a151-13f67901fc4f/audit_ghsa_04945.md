# [H] Fission: Cross-namespace event leakage via KubernetesWatchTrigger allows persistent tenant surveillance

## Summary
Severity: High
Advisory: GHSA-gc3j-79f2-7vvw
CVE: CVE-2026-49822
CWE: CWE-284, CWE-862
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-gc3j-79f2-7vvw
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.24.0

## Details
### Summary

A low-privilege developer who could create a `KubernetesWatchTrigger` (KWT) in their own namespace was able to establish a persistent surveillance channel over any other namespace.

### Details

Two independent flaws compounded:

1. `pkg/kubewatcher/kubewatcher.go::createKubernetesWatch` used `w.Spec.Namespace` (user-controlled) directly as the Watch target without checking it against `w.Namespace` (the KWT's own namespace). `kubewatcher` established the Watch
using its cluster-scoped service account and serialized every Pod/Service/Job change event as full JSON over HTTP POST to the attacker's function.
2. The validating webhook (`pkg/webhook/kuberneteswatchtrigger.go`) registered `verbs=create` only, so `update`/`patch` requests bypassed validation entirely.

A separate leak: an empty `spec.namespace` resolved to **all namespaces** via the controller's default, letting an attacker omit the field to surveil the entire cluster.

### Impact

A tenant with `kuberneteswatchtriggers.fission.io/create` could continuously receive full event payloads for Pods, Services, and Jobs in any namespace — a persistent cross-tenant surveillance channel requiring no additional privileges.

### Fix

Fixed in [#3379](https://github.com/fission/fission/pull/3379) and released in [v1.24.0](https://github.com/fission/fission/releases/tag/v1.24.0).

- The validating webhook marker is extended to `verbs=create;update`.
- `Validate` rejects `KubernetesWatchTrigger.spec.namespace != metadata.namespace`.
- A controller guard in `createKubernetesWatch` rejects cross-namespace targets that bypass admission and coerces an empty `Spec.Namespace` to the trigger's own namespace.

### Behavioural change

KubernetesWatchTriggers with an unset `spec.namespace` now watch only their own namespace instead of all namespaces. Anyone relying on the previous all-namespaces behaviour must create a separate KWT per namespace.

## References
- https://github.com/fission/fission/security/advisories/GHSA-gc3j-79f2-7vvw
- https://nvd.nist.gov/vuln/detail/CVE-2026-49822
- https://github.com/fission/fission/pull/3379
- https://github.com/fission/fission/commit/e2b92663499f4dc3a1e2d38178f39c3c65e0134a
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.24.0
