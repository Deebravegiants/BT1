# [H] Fission: Incomplete capability denylist in Environment/Function PodSpec validation allows tenant-added CAP_SYS_TIME and cross-tenant node wall-clock corruption

## Summary
Severity: High
Advisory: GHSA-qf5v-m7p4-95rp
CVE: CVE-2026-50570
CWE: CWE-269, CWE-732
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:N/I:H/A:L (CVSS_V3)
Published: 2026-07-28
Source: https://github.com/advisories/GHSA-qf5v-m7p4-95rp
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.25.0

## Details
Fission v1.24.0 added PodSpec safety validation for tenant-facing Environment and Function CRDs (`ValidatePodSpecSafety` / `ValidateContainerSafety` admission webhook + `sanitizeContainerSecurityContext` executor merge layer), but the
capability check was implemented as a fixed **denylist of six Linux capabilities** (SYS_ADMIN, NET_ADMIN, SYS_PTRACE, SYS_MODULE, DAC_READ_SEARCH, DAC_OVERRIDE). The denylist omitted **CAP_SYS_TIME**, among others. As a result, a tenant
who could create a Function or Environment CRD could request `securityContext.capabilities.add: ["SYS_TIME"]`, pass Fission's admission validation and merge-layer sanitization, and run attacker-controlled code with `CAP_SYS_TIME` in the
resulting function or runtime container.

Demonstrated consequence: cross-tenant node integrity damage via `CAP_SYS_TIME`. The Linux real-time clock is not namespaced — time namespaces virtualize only `MONOTONIC` and `BOOTTIME`, never `REALTIME` — so a tenant container holding
`CAP_SYS_TIME` could call `clock_settime(CLOCK_REALTIME)` and rewrite the shared node wall clock. That corrupts TLS / certificate validity windows, Kubernetes lease renewal, token expiry, scheduling, and time-series for every workload on
the node.

The denylist also omitted `SYS_RAWIO`, `BPF`, `SYS_RESOURCE`, and `MAC_ADMIN`. Those are documented as evidence that the denylist is structurally incomplete (their practical impact is kernel-, LSM-, or device-cgroup-dependent and is not
exercised in this report).

The deeper structural problem: a denylist on `capabilities.add` cannot constrain capabilities the OCI runtime grants by default — `DAC_OVERRIDE` is in the OCI default cap set and reaches the container regardless of any `add` check,
partially mooting the denylist for its own entries. A capability allowlist (with `drop:["ALL"]` to remove the default set) is the only model that addresses both problems.

### Affected

- Project: `github.com/fission/fission`
- Versions: `<= 1.24.0`
- Audited commits: v1.24.0 tag (`ce617120`) and current HEAD at audit time
- Component: `pkg/apis/core/v1/podspec_safety.go` (`dangerousCapabilities`) and `pkg/executor/util/merge.go` (`dangerousMergeContainerCapabilities`)
- Pre-condition: cluster does not enforce a restrictive Pod Security Admission (PSA) profile on the function-pod namespace. With PSA `restricted` in force the API server's PodSecurity admission rejects the pod at creation and this
finding does not apply. Fission added its own PodSpec validation precisely because it cannot assume PSA enforcement.


Fix section (paste into the Fix / Patches field)

Fixed in [v1.25.0](https://github.com/fission/fission/releases/tag/v1.25.0) by:

- [PR #3465](https://github.com/fission/fission/pull/3465) (commit [`2569b42b`](https://github.com/fission/fission/commit/2569b42b)) — replace the denylist with a PSA-restricted allowlist (`NET_BIND_SERVICE` only) at both enforcement
layers:
  - `pkg/apis/core/v1/podspec_safety.go` — `ValidateContainerSafety` now rejects any `capabilities.add` entry not in `allowedCapabilities`. The container check is invoked from `ValidatePodSpecSafety` for every PodSpec container /
init-container and from `Environment.validateForAdmission` for the bare `Runtime.Container` / `Builder.Container`.
  - `pkg/executor/util/merge.go` — `sanitizeContainerSecurityContext` filters `capabilities.add` through the same allowlist at every merge site (poolmgr / newdeploy / container executor / builder).
- The same PR adds 21 bounded CEL `XValidation` rules covering the cheap pod-level invariants (`hostNetwork` / `hostPID` / `hostIPC` / `serviceAccountName` / `serviceAccount` override) on `FunctionSpec`, `Runtime`, and `Builder`, plus
the bare-Container `SecurityContext` checks (`privileged != true`, `allowPrivilegeEscalation != true`, `capabilities.add ⊆ {NET_BIND_SERVICE}`) on `Runtime` and `Builder`. The API server now short-circuits those attack vectors per CRD
apply before the webhook is invoked. Per-container PodSpec iteration stays in the webhook because it exceeds the API server's CEL cost budget.
- The same PR also adds two forward-compat regression guards in `pkg/apis/core/v1/podspec_safety_test.go`:
  - `TestAllTenantContainerSurfacesAreValidated` walks every CRD root type via reflection and fails if any reachable `*apiv1.PodSpec` or `*apiv1.Container` field is missing from the hand-maintained known-covered set.
  - `TestTenantContainerSurfaces_RejectSysAdmin` end-to-end exercises each covered surface and asserts `ValidateForAdmission` rejects a `SYS_ADMIN` injection at that exact path.

### Not addressed in v1.25.0

The advisory's structural recommendation to force `capabilities.drop: ["ALL"]` at the merge layer is **not** part of this fix. Fission's own sidecar containers (`fission-fetcher`, builder) were authored against the OCI default capability
set and need a per-container cap audit before `drop:["ALL"]` can be applied uniformly. The allowlist on `capabilities.add` closes the demonstrated `CAP_SYS_TIME` impact; the OCI-default-cap concern (which the advisory itself marks as
conditional / not demonstrated) is tracked separately.

## References
- https://github.com/fission/fission/security/advisories/GHSA-qf5v-m7p4-95rp
- https://nvd.nist.gov/vuln/detail/CVE-2026-50570
- https://github.com/fission/fission/pull/3465
- https://github.com/fission/fission/commit/2569b42bfadbcb7d78b55a00a60f77937e522699
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.25.0
