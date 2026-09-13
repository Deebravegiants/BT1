# [C] Path traversal in Tekton Pipelines git resolver allows reading arbitrary files from the resolver pod

## Summary
Severity: Critical
Advisory: GHSA-j5q5-j9gm-2w5c
CVE: CVE-2026-33211
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:C/C:H/I:H/A:N (CVSS_V3)
Published: 2026-03-18
Source: https://github.com/advisories/GHSA-j5q5-j9gm-2w5c
Type: github-advisory

## Affected
- Go: `github.com/tektoncd/pipeline` — affected >=1.0.0 <1.0.1
- Go: `github.com/tektoncd/pipeline` — affected >=1.1.0 <1.3.3
- Go: `github.com/tektoncd/pipeline` — affected >=1.4.0 <1.6.1
- Go: `github.com/tektoncd/pipeline` — affected >=1.7.0 <1.9.2
- Go: `github.com/tektoncd/pipeline` — affected >=1.10.0 <1.10.2

## Details
### Summary

The Tekton Pipelines git resolver is vulnerable to path traversal via the `pathInRepo` parameter. A tenant with permission to create `ResolutionRequests` (e.g. by creating `TaskRuns` or `PipelineRuns` that use the git resolver) can read arbitrary files from the resolver pod's filesystem, including ServiceAccount tokens. The file contents are returned base64-encoded in `resolutionrequest.status.data`.

### Details

The git resolver's `getFileContent()` function in `pkg/resolution/resolver/git/repository.go` constructs a file path by joining the repository clone directory with the user-supplied `pathInRepo` parameter:

```go
fileContents, err := os.ReadFile(filepath.Join(repo.directory, path))
```

The `pathInRepo` parameter is not validated for path traversal sequences. An attacker can supply values like `../../../../etc/passwd` to escape the cloned repository directory and read arbitrary files from the resolver pod's filesystem.

The vulnerability was introduced in commit `318006c4e3a5` which switched the git resolver from the go-git library (using an in-memory filesystem that cannot be escaped) to shelling out to the `git` binary and reading files with `os.ReadFile()` from the real filesystem.

### Impact

**Arbitrary file read** — A namespace-scoped tenant who can create `TaskRuns` or `PipelineRuns` with git resolver parameters can read any file readable by the resolver pod process.

**Credential exfiltration and privilege escalation** — The resolver pod's ServiceAccount token is readable at a well-known path (`/var/run/secrets/kubernetes.io/serviceaccount/token`). In the default RBAC configuration, the `tekton-pipelines-resolvers` ServiceAccount has `get`, `list`, and `watch` permissions on `secrets` cluster-wide. An attacker who exfiltrates this token gains the ability to read all Secrets across all namespaces, escalating from namespace-scoped access to cluster-wide secret access.

### Patches

Fixed in 1.0.x, 1.3.x, 1.6.x, 1.9.x, 1.10.x.

The fix validates `pathInRepo` to reject paths containing `..` components at parameter validation time, and adds a containment check using `filepath.EvalSymlinks()` to prevent symlink-based escapes from attacker-controlled repositories.

### Workarounds

There is no workaround other than restricting which users can create `TaskRuns`, `PipelineRuns`, or `ResolutionRequests` that use the git resolver. Administrators can also reduce the impact by scoping the resolver pod's ServiceAccount RBAC permissions using a custom `ClusterRole` with more restrictive rules.

### Affected Versions

All releases from **v1.0.0** through **v1.10.0**, including all patch releases:

- v1.0.0, v1.1.0, v1.2.0
- v1.3.0, v1.3.1, v1.3.2
- v1.4.0, v1.5.0, v1.6.0, v1.7.0
- v1.9.0, v1.9.1, v1.10.0

Releases prior to v1.0.0 (e.g. v0.70.0 and earlier) are **not affected** because they used the go-git library's in-memory filesystem where path traversal cannot escape the git worktree.

### Acknowledgments

This vulnerability was reported by Oleh Konko (@1seal), who provided a thorough vulnerability analysis, proof-of-concept, and review of the fix. Thank you!

### References

- Fix: _(link to merged PR/commit)_
- Introduced in: `318006c4e3a5` ("fix: resolve Git Anonymous Resolver excessive memory usage")

## References
- https://github.com/tektoncd/pipeline/security/advisories/GHSA-j5q5-j9gm-2w5c
- https://nvd.nist.gov/vuln/detail/CVE-2026-33211
- https://github.com/tektoncd/pipeline/commit/10fa538f9a2b6d01c75138f1ed7ba3da0e34687c
- https://github.com/tektoncd/pipeline/commit/318006c4e3a5
- https://github.com/tektoncd/pipeline/commit/3ca7bc6e6dd1d97f80b84f78370d91edaf023cbd
- https://github.com/tektoncd/pipeline/commit/961388fcf3374bc7656d28ab58ca84987e0a75ae
- https://github.com/tektoncd/pipeline/commit/b1fee65b88aa969069c14c120045e97c37d9ee5e
- https://github.com/tektoncd/pipeline/commit/cdb4e1e97a4f3170f9bc2cbfff83a6c8107bc3db
- https://github.com/tektoncd/pipeline/commit/ec7755031a183b345cf9e64bea0e0505c1b9cb78
- https://github.com/tektoncd/pipeline
