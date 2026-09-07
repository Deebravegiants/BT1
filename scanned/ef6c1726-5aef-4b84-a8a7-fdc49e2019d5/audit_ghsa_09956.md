# [M] Tekton Pipelines: VolumeMount path restriction bypass via missing filepath.Clean in /tekton/ check

## Summary
Severity: Medium
Advisory: GHSA-rx35-6rhx-7858
CVE: CVE-2026-40923
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:L/A:N (CVSS_V3)
Published: 2026-04-21
Source: https://github.com/advisories/GHSA-rx35-6rhx-7858
Type: github-advisory

## Affected
- Go: `github.com/tektoncd/pipeline` — affected >=1.10.0 <1.11.1
- Go: `github.com/tektoncd/pipeline` — affected >=1.7.0 <1.9.3
- Go: `github.com/tektoncd/pipeline` — affected >=1.4.0 <1.6.2
- Go: `github.com/tektoncd/pipeline` — affected >=1.2.0 <1.3.4
- Go: `github.com/tektoncd/pipeline` — affected >=1.0.0 <1.0.2

## Details
### Summary

A validation bypass in the VolumeMount path restriction allows mounting
volumes under restricted `/tekton/` internal paths by using `..` path
traversal components. The restriction check uses `strings.HasPrefix`
without `filepath.Clean`, so a path like `/tekton/home/../results`
passes validation but resolves to `/tekton/results` at runtime.

### Details

Tekton Pipelines restricts VolumeMount paths under `/tekton/` (except
`/tekton/home`) to prevent users from interfering with internal
execution state. The validation at
`pkg/apis/pipeline/v1/container_validation.go` checks mount paths using
`strings.HasPrefix` without normalizing the path first:

```go
if strings.HasPrefix(vm.MountPath, "/tekton/") &&
    !strings.HasPrefix(vm.MountPath, "/tekton/home") {
    // reject
}
```

Because `/tekton/home` is an allowed prefix, a path like
`/tekton/home/../results` passes both checks. At runtime, the container
runtime resolves `..` and the actual mount point becomes
`/tekton/results`.

The same pattern exists in `pkg/apis/pipeline/v1beta1/task_validation.go`.

### Impact

An authenticated user with Task or TaskRun creation permissions can
mount volumes over internal Tekton paths, potentially:

- Writing fake task results that downstream pipelines trust
- Reading or modifying step scripts before execution
- Interfering with entrypoint coordination state

### Patches

_(to be filled: fixed in versions X.Y.Z)_

### Workarounds

- Use admission controllers (OPA/Gatekeeper, Kyverno) to validate that
  VolumeMount paths do not contain `..` components.
- In multi-tenant setups, restrict who can create Task and TaskRun
  resources via RBAC.

### Affected Versions

All versions through **v1.10.0** (both `v1` and `v1beta1` APIs).

### Acknowledgments

This vulnerability was reported by @kodareef5.

## References
- https://github.com/tektoncd/pipeline/security/advisories/GHSA-rx35-6rhx-7858
- https://nvd.nist.gov/vuln/detail/CVE-2026-40923
- https://github.com/tektoncd/pipeline
- https://github.com/tektoncd/pipeline/releases/tag/v1.11.1
