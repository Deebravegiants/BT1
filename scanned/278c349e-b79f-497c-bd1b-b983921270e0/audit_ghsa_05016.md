# [H] Fission: MessageQueueTrigger scaler manager materializes Secret values into Deployment envvars and accepts arbitrary user PodSpec

## Summary
Severity: High
Advisory: GHSA-7m8x-qg2j-4m3v
CWE: CWE-200, CWE-269, CWE-284
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-7m8x-qg2j-4m3v
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.24.0

## Details
### Summary

The Fission MessageQueueTrigger (MQT) scaler controller exposed two privilege-escalation primitives to any subject able to create MQTs in a namespace.

### Details

**1. Secret materialization.** `getEnvVarlist` in `pkg/mqtrigger/scalermanager.go` read the Secret named in `Spec.Secret` using the controller's cluster-wide `secrets/get` RBAC and emitted each key as a literal `EnvVar.Value`, copying
the plaintext secret content into the connector Deployment's pod template. A subject holding `messagequeuetriggers/create` but **not** `secrets/get` could exfiltrate any Secret in the namespace by pointing an MQT at it.

**2. PodSpec injection.** `Spec.PodSpec` was merged into the controller-built connector PodSpec via `util.MergePodSpec` with no allowlist on which fields could come from the user. An MQT could substitute `Containers[].Image` (run any
image), override `Command`/`Args`, inject `Env`, add `VolumeMounts` + `Volumes`, override `ServiceAccountName`, and set `HostNetwork`/`HostPID`/`HostIPC` — turning `messagequeuetriggers/create` into effective `deployments/create` with an
 arbitrary image and service account.

### Impact

A tenant with only `messagequeuetriggers.fission.io/create` in a namespace could read any Secret in that namespace and run an arbitrary container image under an arbitrary service account, escalating well beyond their intended RBAC.

### Fix

Fixed in [#3367](https://github.com/fission/fission/pull/3367) and released in [v1.24.0](https://github.com/fission/fission/releases/tag/v1.24.0).

- `getEnvVarlist` now emits `EnvVar.ValueFrom.SecretKeyRef` so the connector pod resolves values at start time under its own service account. The secret values are never written into the Deployment object and never logged.
- A new allowlist, `MergeAllowedPodSpecFields` (`pkg/executor/util/merge_allowlist.go`), accepts only `NodeSelector`, `Tolerations`, `Affinity`, `RuntimeClassName`, and per-container `Resources`. All other user-supplied fields are
dropped at the controller layer, and the validating webhook rejects every populated non-allowlisted field with a clear error. The webhook and the merge helper share a single canonical `DisallowedPodSpecFields` enumeration so they cannot
drift.

### Behavioural change

MQT authors that previously overrode the connector image, command, args, env, volumes, service account, or host namespaces via `Spec.PodSpec` will see those fields rejected at admission (or silently dropped if the webhook is disabled).
Allowlisted fields flow through unchanged.

## References
- https://github.com/fission/fission/security/advisories/GHSA-7m8x-qg2j-4m3v
- https://github.com/fission/fission/pull/3367
- https://github.com/fission/fission/commit/94bf5792396989fdd71961e8701833c8110da889
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.24.0
