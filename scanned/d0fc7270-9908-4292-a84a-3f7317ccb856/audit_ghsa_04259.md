# [C] Fission Container Executor Function PodSpec Injection Leading to Node Escape

## Summary
Severity: Critical
Advisory: GHSA-v455-mv2v-5g92
CVE: CVE-2026-50563
CWE: CWE-269, CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:H (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-v455-mv2v-5g92
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.24.0

## Details
### Summary

Fission's Container Executor path lets a tenant supply `Function.spec.podspec` directly; the executor merges it into the executor-built podspec and creates a Deployment whose pods run the user's container image.

### Details

Two flaws compounded:

1. `pkg/apis/core/v1/validation.go::FunctionSpec.Validate` only checked that `spec.PodSpec != nil` when `executorType: container`; it did not inspect the content of `spec.PodSpec`.
2. `pkg/executor/util/merge.go::MergePodSpec` unconditionally forwarded `hostPID`, `hostNetwork`, `hostIPC`, hostPath volumes, `serviceAccountName`, and container `privileged` into the Deployment spec via the container-executor sink
(`pkg/executor/executortype/container/deployment.go::getDeploymentSpec`).

A tenant with only `functions.fission.io/create` could deploy a Function with a crafted podspec that mounted the host root filesystem and shared host namespaces. The executor — running under its high-privilege SA, which holds
`deployments/create` on the function namespace — created that Deployment on the tenant's behalf, turning Function-create into effective `deployments/create` with arbitrary pod-security configuration.

This is the Function-CRD sibling of GHSA-gx55-f84r-v3r7 / GHSA-wmgg-3p4h-48x7, with a **lower** attack threshold: regular function developers typically hold `functions/create` but not `environments/create`.

### Impact

A tenant with only `functions.fission.io/create` is escalated to node escape via a privileged, host-namespace pod scheduled by the executor.

### Fix

Fixed in [#3391](https://github.com/fission/fission/pull/3391) and released in [v1.24.0](https://github.com/fission/fission/releases/tag/v1.24.0).

- `FunctionSpec.Validate` now calls `ValidatePodSpecSafety("Function.spec.podspec", spec.PodSpec)` after the existing `spec.PodSpec == nil` check.
- The Function validating webhook is already registered on `verbs=create;update`, so it picks up the new validation with no marker change.
- The same merge-layer strip and per-container sanitize used for the Environment path applies here, since the container-executor sink calls `util.MergePodSpec`.

See GHSA-gx55-f84r-v3r7 for the detailed fix.

### Behavioural change

Functions whose `spec.podspec` sets host namespaces, hostPath volumes, container `privileged`/`allowPrivilegeEscalation`, dangerous Linux capabilities, or a `serviceAccountName` override are now rejected at admission. Legitimate
container-executor functions that set `image`, `command`, `args`, `env`, `resources`, `nodeSelector`, `tolerations`, `affinity`, non-hostPath `volumes`, or `volumeMounts` are unaffected.

## References
- https://github.com/fission/fission/security/advisories/GHSA-v455-mv2v-5g92
- https://nvd.nist.gov/vuln/detail/CVE-2026-50563
- https://github.com/fission/fission/pull/3391
- https://github.com/fission/fission/commit/e484df8460bb4e8026e24210120602aa7f181f64
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.24.0
