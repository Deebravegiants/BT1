# [M] Fission builder accepts arbitrary buildcmd strings from Environment.spec.builder.command, allowing the builder pod to invoke arbitrary executables

## Summary
Severity: Medium
Advisory: GHSA-7pjr-qpvh-m339
CVE: CVE-2026-46618
CWE: CWE-250, CWE-269, CWE-78
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:L/VI:L/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-7pjr-qpvh-m339
Type: github-advisory

## Affected
- Go: `github.com/fission/fission` — affected >=0 <1.23.0

## Details
### Summary

Before the round-1 security sweep, `pkg/builder/builder.go` passed `Environment.spec.builder.command` directly into `exec.Command(...)` after a `strings.Fields` split, with no validation of the executable path or its arguments. A user who could create or update `Environment` CRDs in a namespace observed by the buildermgr could thereby point the builder pod at any executable inside the builder image (e.g. `/bin/sh -c '...'`) and execute arbitrary code in the builder pod context.

### Affected component

- `pkg/builder/builder.go:254` — call site (`exec.Command(buildCmd, buildArgs...)`).
- `pkg/builder/builder.go:106` — input source: `buildCmd, buildArgs = strings.Fields(req.BuildCommand)[0], strings.Fields(req.BuildCommand)[1:]`.

### Impact

A subject with `create` / `update` privilege on `Environment` objects could:

1. Cause the builder pod for any package using that environment to execute arbitrary code.
2. Read whatever files the builder pod has access to inside its `/packages` shared volume (deployment archive payloads for that package).
3. Write arbitrary content into the `/packages` shared volume, which the fetcher subsequently uploads as the package deployment archive.

The builder pod runs in the user's namespace with the `fission-builder` SA (not the more-privileged executor SA), so the impact is bounded to that namespace's package contents and the builder pod's own filesystem. `PR:H` reflects that creating / modifying `Environment` CRDs is typically restricted to cluster admins or platform operators.

### Root cause

`pkg/builder/builder.go`'s build-command parser did not validate the resulting executable path. Although `exec.Command` does not invoke a shell, it does locate the executable via `$PATH`, and `strings.Fields` splitting allowed multiple flags / sub-arguments to be passed.

### Fix

Released in [v1.23.0](https://github.com/fission/fission/releases/tag/v1.23.0):

- **PR #3364** (commit `0f45c911`) introduces `Builder.resolveBuildCommand` in `pkg/builder/builder.go`, which:
  1. Accepts an empty string (treated as the default `/build`).
  2. Accepts the literal `/build`.
  3. Accepts any absolute path that survives `filepath.Clean` and contains no `..` segments.
  4. Rejects anything containing whitespace metacharacters or relative paths.
- `exec.Command` still receives only the validated absolute path; sub-arguments continue to come from `strings.Fields` of the original string but are now passed positionally with no shell expansion.

### Mitigation (until upgrade)

1. Restrict who can create / update `Environment` CRDs to trusted operators only.
2. Audit `Environment.spec.builder.command` values for any non-`/build` paths.
3. Run the buildermgr with a tightened ServiceAccount that has no secret access in the builder namespace.

## References
- https://github.com/fission/fission/security/advisories/GHSA-7pjr-qpvh-m339
- https://nvd.nist.gov/vuln/detail/CVE-2026-46618
- https://github.com/fission/fission/pull/3364
- https://github.com/fission/fission
- https://github.com/fission/fission/releases/tag/v1.23.0
