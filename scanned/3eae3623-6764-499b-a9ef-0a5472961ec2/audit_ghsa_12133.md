# [M] Tekton Pipelines controller panic via long resolver name in TaskRun/PipelineRun

## Summary
Severity: Medium
Advisory: GHSA-cv4x-93xx-wgfj
CVE: CVE-2026-33022
CWE: CWE-129, CWE-400
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-03-17
Source: https://github.com/advisories/GHSA-cv4x-93xx-wgfj
Type: github-advisory

## Affected
- Go: `github.com/tektoncd/pipeline` — affected >=0.60.0 <1.0.1
- Go: `github.com/tektoncd/pipeline` — affected >=1.1.0 <1.3.3
- Go: `github.com/tektoncd/pipeline` — affected >=1.4.0 <1.6.1
- Go: `github.com/tektoncd/pipeline` — affected >=1.7.0 <1.9.2
- Go: `github.com/tektoncd/pipeline` — affected >=1.10.0 <1.10.2

## Details
### Summary

A user with permission to create or update a TaskRun or PipelineRun can crash the Tekton Pipelines controller by setting `.spec.taskRef.resolver` (or `.spec.pipelineRef.resolver`) to a string of 31 characters or more, causing a denial of service for all reconciliation.

### Details

The controller panics in `GenerateDeterministicNameFromSpec` when building a deterministic `ResolutionRequest` name. The generated name has the format `{resolver}-{hash}` and, when the resolver name is long enough, the result exceeds the DNS-1123 label limit of 63 characters.

The truncation logic attempts to find a word boundary using `strings.LastIndex(name, " ")`. Since the generated name never contains spaces (it is composed of the resolver name, a dash, and a hex-encoded hash), `LastIndex` returns `-1`, which is then used as a slice bound:

```go
return name[:strings.LastIndex(name[:maxLength], " ")], nil
// strings.LastIndex returns -1 → panic: slice bounds out of range [:-1]
```

The panic crashes the controller. Because the offending TaskRun or PipelineRun is re-reconciled on restart, the controller enters a `CrashLoopBackOff`, blocking all TaskRun and PipelineRun reconciliation cluster-wide until the offending resource is manually deleted.

Built-in resolvers use short names (`git`, `cluster`, `bundles`, `hub`) and are not affected under normal usage. The vulnerability is exploitable by any user who can create TaskRuns or PipelineRuns with a custom resolver name.

### Impact

**Denial of service** — A single malicious TaskRun or PipelineRun with a long resolver name is sufficient to crash the Tekton Pipelines controller into a restart loop, blocking all CI/CD reconciliation cluster-wide until the resource is removed.

### Patches

Fixed in versions 1.0.1, 1.3.3, 1.6.1, 1.9.2, 1.10.2.

The fix computes the hash first, then truncates only the prefix (resolver name) to fit within the DNS-1123 label limit, preserving the full hash to maintain determinism and uniqueness of `ResolutionRequest` names.

### Workarounds

Restrict who can create TaskRun and PipelineRun resources via Kubernetes RBAC. There is no validation-side workaround without patching.

### Affected Versions

All releases from **v0.60.0** through **v1.10.0**.

The vulnerable truncation logic was introduced in commit `ea1fa7ad1fdc` ("Remote Resolution Refactor"), first released in v0.60.0 (2024-05-22).

Currently supported affected releases:
- **v1.10.x** (latest)
- **v1.9.x** (LTS, EOL 2027-01-30)
- **v1.6.x** (LTS, EOL 2026-10-31)
- **v1.3.x** (LTS, EOL 2026-08-04)
- **v1.0.x** (LTS, EOL 2026-04-29)

Releases prior to v0.60.0 are **not affected** — the truncation code did not exist.

### Acknowledgments

This vulnerability was reported by Oleh Konko (@1seal), who provided a thorough vulnerability analysis, proof-of-concept, and review of the fix. Thank you!

### References

- Fix (main): [5eead3f859b9](https://github.com/tektoncd/pipeline/commit/5eead3f859b9f938e86039e4d29185092c1d4ee6)
- Fix (v1.10.x): [01673237c464](https://github.com/tektoncd/pipeline/commit/01673237c464cfac7e286183f5c9e9d6ec951a64)
- Fix (v1.9.x): [edc64bbf2232](https://github.com/tektoncd/pipeline/commit/edc64bbf22323fcf218170f19047c9bcd8163e90)
- Fix (v1.6.x): [0fa2d66cff81](https://github.com/tektoncd/pipeline/commit/0fa2d66cff814838c3a10cce252104c7fe618932)
- Fix (v1.3.x): [5e4905fb6754](https://github.com/tektoncd/pipeline/commit/5e4905fb6754efa5ecea54de195738d73fb0e01d)
- Fix (v1.0.x): [ebc197e2b973](https://github.com/tektoncd/pipeline/commit/ebc197e2b9733deedaa1624212ec66dcdf61eaaf)
- Introduced in: `ea1fa7ad1fdc` ("Remote Resolution Refactor")

## References
- https://github.com/tektoncd/pipeline/security/advisories/GHSA-cv4x-93xx-wgfj
- https://nvd.nist.gov/vuln/detail/CVE-2026-33022
- https://github.com/tektoncd/pipeline/commit/01673237c464cfac7e286183f5c9e9d6ec951a64
- https://github.com/tektoncd/pipeline/commit/0fa2d66cff814838c3a10cce252104c7fe618932
- https://github.com/tektoncd/pipeline/commit/5e4905fb6754efa5ecea54de195738d73fb0e01d
- https://github.com/tektoncd/pipeline/commit/5eead3f859b9f938e86039e4d29185092c1d4ee6
- https://github.com/tektoncd/pipeline/commit/ebc197e2b9733deedaa1624212ec66dcdf61eaaf
- https://github.com/tektoncd/pipeline/commit/edc64bbf22323fcf218170f19047c9bcd8163e90
- https://github.com/tektoncd/pipeline
