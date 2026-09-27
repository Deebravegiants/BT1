# [C] Fission Environment CRD podspec passthrough enables hostPID/hostNetwork/privileged pods, node escape

## Summary
Severity: Critical
Advisory: GHSA-gx55-f84r-v3r7
CVE: CVE-2026-50564
CWE: CWE-269, CWE-284, CWE-693
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-gx55-f84r-v3r7
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.24.0

## Details
### Summary

Fission's `Environment` CRD exposes `spec.runtime.podSpec` and `spec.builder.podSpec`, which are merged into the Kubernetes pod specs for runtime and builder pods. The merge logic propagated `hostNetwork`, `hostPID`, `hostIPC`, container
 `privileged`, and `serviceAccountName` from the user-supplied podspec with no filtering, and `Environment.Validate` performed no security-relevant checks on these fields.

### Details

A namespace user with `create`/`update` on `environments.fission.io` could produce privileged, host-network, hostPID pods in the Fission function or builder namespace. Because the Helm chart created the `fission-function` and
`fission-builder` namespaces with no `pod-security.kubernetes.io/enforce` labels, Kubernetes Pod Security Admission did not catch the escape either.

From a host-network privileged pod with hostPID, the attacker could `nsenter` into the host, read cloud-metadata credentials, access the container-runtime socket, pivot to other namespaces, and fully compromise the node.

### Impact

`environments.fission.io` create/update RBAC is escalated to node compromise — host filesystem and network access on the scheduling node, and from there potential cluster-wide takeover.

### Fix

Fixed in [#3391](https://github.com/fission/fission/pull/3391) and released in [v1.24.0](https://github.com/fission/fission/releases/tag/v1.24.0). Denylist at admission (the primary defence) plus belt-and-braces at the merge layer.

**Admission denylist** (`pkg/apis/core/v1/podspec_safety.go::ValidatePodSpecSafety`), called from `Environment.Validate` for both `Runtime.PodSpec` and `Builder.PodSpec`:

- pod-level: `HostNetwork`, `HostPID`, `HostIPC`, `ServiceAccountName` / `DeprecatedServiceAccount` override, hostPath volumes;
- per-container: `SecurityContext.Privileged=true`, `SecurityContext.AllowPrivilegeEscalation=true`, dangerous capabilities (`SYS_ADMIN`, `NET_ADMIN`, `SYS_PTRACE`, `SYS_MODULE`, `DAC_READ_SEARCH`, `DAC_OVERRIDE`).

**Update-bypass closed:** the `Environment` validating-webhook marker is extended from `verbs=create` to `verbs=create;update` (chart and envtest manifests aligned).

**Merge-layer belt-and-braces** (`pkg/executor/util/merge.go`): even if admission is bypassed (`failurePolicy=Ignore` or stale pre-webhook objects), the denylisted pod-level fields are stripped and per-container dangerous settings are
sanitized before the merge (with `SecurityContext` deep-copied first so cached informer objects are not mutated). Legitimate operator hardening via the chart's pod-level `securityContext` (fsGroup, runAsNonRoot, runAsUser) still flows
through.

### Behavioural change

Environments that explicitly set any denylisted field are now rejected at admission. There is no legitimate Fission use case — these primitives exist for cluster operators, not Environment authors.

This is the same root cause and fix as GHSA-wmgg-3p4h-48x7.

## References
- https://github.com/fission/fission/security/advisories/GHSA-gx55-f84r-v3r7
- https://nvd.nist.gov/vuln/detail/CVE-2026-50564
- https://github.com/fission/fission/pull/3391
- https://github.com/fission/fission/commit/e484df8460bb4e8026e24210120602aa7f181f64
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.24.0
