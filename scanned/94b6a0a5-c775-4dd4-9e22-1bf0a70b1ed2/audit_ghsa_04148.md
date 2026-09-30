# [M] Fission builder pods auto-mount the fission-builder ServiceAccount token in the user-supplied builder container

## Summary
Severity: Medium
Advisory: GHSA-8wcj-mfrc-jx5q
CVE: CVE-2026-50565
CWE: CWE-250, CWE-269, CWE-538
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2026-06-30
Source: https://github.com/advisories/GHSA-8wcj-mfrc-jx5q
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.24.0

## Details
### Summary

Fission builder pods were created with `ServiceAccountName: fission-builder` and no `AutomountServiceAccountToken: false`, so the kubelet auto-mounted the service-account token into every container in the pod — including the
user-supplied builder image.

### Details

The user controls the builder container image, command, and podspec through `Environment.spec.builder.image` / `.container` / `.podspec`. With the SA token auto-mounted at `/var/run/secrets/kubernetes.io/serviceaccount/token` inside that
 container, any code running there inherited the `fission-builder` identity. The `fission-builder` SA holds namespace-wide `get` on `secrets` and `configmaps` (`pkg/utils/serviceaccount.go`), so the user-controlled builder container
could read every Secret in the builder namespace by name.

This is the buildermgr sibling of GHSA-85g2-pmrx-r49q (CVE-2026-46617), whose fix suppressed the SA-token automount on function runtime pods but did not cover the structurally identical primitive in `pkg/buildermgr/envwatcher.go`.

### Impact

A subject with `create`/`update` on `Environment` CRDs in a namespace observed by the buildermgr could read every Secret and ConfigMap in the builder namespace via the auto-mounted `fission-builder` token.

### Fix

Fixed in [#3390](https://github.com/fission/fission/pull/3390) and released in [v1.24.0](https://github.com/fission/fission/releases/tag/v1.24.0). In `createBuilderDeployment`:

- Set pod-level `AutomountServiceAccountToken=false` on the initial PodSpec and add the projected fetcher SA-token volume.
- Re-clamp `AutomountServiceAccountToken=false` after every `MergePodSpec` call so a user-supplied podspec cannot restore the kubelet automount.
- Mount the token via a projected volume on the fetcher sidecar only, so the legitimate build → archive-upload flow keeps its cluster API access.

Reuses the projected-volume helpers from `pkg/executor/util/satoken.go` introduced by the GHSA-85g2-pmrx-r49q fix.

### Behavioural change

The user-supplied builder container no longer receives an auto-mounted SA token. The fetcher sidecar still gets its token via a projected volume.

## References
- https://github.com/fission/fission/security/advisories/GHSA-8wcj-mfrc-jx5q
- https://nvd.nist.gov/vuln/detail/CVE-2026-50565
- https://github.com/fission/fission/pull/3390
- https://github.com/fission/fission/commit/8fa799417c77ce8a0189d9858bfe11ece29b84a6
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.24.0
