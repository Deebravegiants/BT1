# [M] melange has Path Traversal When Resolving External Pipelines via Unvalidated pipeline[].uses

## Summary
Severity: Medium
Advisory: GHSA-98f2-w9h9-7fp9
CVE: CVE-2026-29050
CWE: CWE-22
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:R/S:U/C:H/I:L/A:N (CVSS_V3)
Published: 2026-04-23
Source: https://github.com/advisories/GHSA-98f2-w9h9-7fp9
Type: github-advisory

## Affected
- Go: `chainguard.dev/melange` — affected >=0.32.0 <0.43.4

## Details
### Impact

An attacker who can influence a melange configuration file — for example through pull-request-driven CI or build-as-a-service scenarios — could set `pipeline[].uses` to a value containing `../` sequences or an absolute path. The `(*Compiled).compilePipeline` function in `pkg/build/compile.go` passed `uses` directly to `filepath.Join(pipelineDir, uses + ".yaml")` without validating the value, so the resolved path could escape each `--pipeline-dir` and read an arbitrary YAML-parseable file visible to the melange process. Because the loaded file is subsequently interpreted as a melange pipeline and its `runs:` block is executed via `/bin/sh -c` in the build sandbox, this additionally allowed shell commands sourced from an out-of-tree file to run during the build, bypassing the review boundary that normally covers the in-tree pipeline definition.

### Patches

Fixed in melange **v0.43.4** via commit [5829ca4](https://github.com/chainguard-dev/melange/commit/5829ca45cfe14dfeb73ffb716992db3b1b7892ac). The fix rejects `uses` values that are absolute paths or contain `..`, and verifies (via `filepath.Rel` after `filepath.Clean`) that the resolved target remains within the pipeline directory.

### Workarounds

Only run `melange build` against configuration files from trusted sources. In CI systems that build user-supplied melange configs, gate builds behind manual review of `pipeline[].uses` values and reject any containing `..` or leading `/`.

### Credits

melange thanks Oleh Konko ([@1seal](https://github.com/1seal) from [1seal.org](https://1seal.org/)) for discovering and reporting this issue.

## References
- https://github.com/chainguard-dev/melange/security/advisories/GHSA-98f2-w9h9-7fp9
- https://nvd.nist.gov/vuln/detail/CVE-2026-29050
- https://github.com/chainguard-dev/melange/commit/5829ca45cfe14dfeb73ffb716992db3b1b7892ac
- https://github.com/chainguard-dev/melange
