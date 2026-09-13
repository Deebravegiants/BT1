# [C] Fission: Environment Runtime.Container and Builder.Container SecurityContext bypass allows privileged pod creation

## Summary
Severity: Critical
Advisory: GHSA-m63v-2g9w-2w6v
CVE: CVE-2026-50566
CWE: CWE-250, CWE-269
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-m63v-2g9w-2w6v
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.24.0

## Details
### Summary

A follow-up bypass of the round-4 PodSpec hardening (GHSA-gx55-f84r-v3r7, GHSA-wmgg-3p4h-48x7, GHSA-v455-mv2v-5g92). Those advisories validate and sanitize the `PodSpec` (`spec.runtime.podSpec` / `spec.builder.podSpec` /
`function.spec.podSpec`), but the Environment CRD also exposes `spec.runtime.container` and `spec.builder.container` — a standalone `Container` merged into the runtime/builder pod whose `SecurityContext` bypassed both layers.

### Details

**Admission-layer gap.** `Environment.Validate()` calls `ValidatePodSpecSafety()` on `Runtime.PodSpec` and `Builder.PodSpec` only. That function takes a `*PodSpec`, so it never inspects the standalone `Runtime.Container.SecurityContext`
or `Builder.Container.SecurityContext`.

**Merge-layer gap.** `sanitizeContainerSecurityContext()` ran only inside `MergePodSpec()`. The container field is merged via `MergeContainer()`, which did not sanitize. With only `Runtime.Container` set and `Runtime.PodSpec` nil,
`MergePodSpec` is never invoked, so the sanitizer never ran.

Affected merge sites: poolmgr (`gp_deployment.go`), newdeploy (`newdeploy.go`), and buildermgr (`envwatcher.go`).

#### Proof of concept

```yaml
apiVersion: fission.io/v1
kind: Environment
metadata:
  name: priv-escape-test
  namespace: default
spec:
  version: 3
  runtime:
    image: "ghcr.io/fission/python-env:latest"
    container:
      name: priv-escape-test
      securityContext:
        privileged: true
  poolsize: 1
```

The admission webhook accepts this Environment and the resulting pool pod runs with `privileged: true`. Equivalent bypasses: `allowPrivilegeEscalation: true`, `capabilities.add: ["SYS_ADMIN"]`, `capabilities.add:
["NET_ADMIN","SYS_PTRACE"]`. The same attack applies to `Builder.Container`.

### Impact

A tenant with `environments.fission.io` create/update RBAC can run `privileged` / `allowPrivilegeEscalation` / dangerous-capability containers in the Fission function or builder namespace, scheduled under the executor's high-privilege
service account — enabling container-sandbox escape, host filesystem and network access, and potential node- and cluster-level compromise. Identical blast radius to GHSA-gx55-f84r-v3r7.

### Fix

Fixed in [#3406](https://github.com/fission/fission/pull/3406) and released in [v1.24.0](https://github.com/fission/fission/releases/tag/v1.24.0).

- **Admission layer (primary defence):** a new `ValidateContainerSafety` in `pkg/apis/core/v1/podspec_safety.go` applies the per-container SecurityContext denylist (`privileged`, `allowPrivilegeEscalation`, dangerous capabilities) to a
standalone container, and is called from `Environment.Validate()` for `Runtime.Container` and `Builder.Container`.
- **Merge layer (defence in depth):** `sanitizeContainerSecurityContext()` is now invoked inside `MergeContainer()` itself, covering all three executor/builder call sites.

### Workarounds

- Restrict Environment create/update RBAC to trusted administrators.
- Deploy a Kyverno / OPA Gatekeeper policy rejecting dangerous Container SecurityContext on Environment CRDs.
- Label the function/builder namespaces with `pod-security.kubernetes.io/enforce: restricted`.

### References

- GHSA-gx55-f84r-v3r7, GHSA-wmgg-3p4h-48x7, GHSA-v455-mv2v-5g92 — the round-4 PodSpec fixes this advisory bypasses ([#3391](https://github.com/fission/fission/pull/3391), `e484df84`).

## References
- https://github.com/fission/fission/security/advisories/GHSA-m63v-2g9w-2w6v
- https://nvd.nist.gov/vuln/detail/CVE-2026-50566
- https://github.com/fission/fission/pull/3406
- https://github.com/fission/fission/commit/695d3e97e3a20463ab7c8c081843e69e65e952e5
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.24.0
