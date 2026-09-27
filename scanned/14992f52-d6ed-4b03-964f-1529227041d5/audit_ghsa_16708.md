# [M] goreleaser shows environment by default

## Summary
Severity: Medium
Advisory: GHSA-f6mm-5fc7-3g3c
CWE: CWE-532
Ecosystem: Go
CVSS: CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N (CVSS_V3)
Published: 2024-05-15
Source: https://github.com/advisories/GHSA-f6mm-5fc7-3g3c
Type: github-advisory

## Affected
- Go: `github.com/goreleaser/goreleaser` — affected >=1.26.0 <1.26.1

## Details
### Summary
Since #4787 the log output is printed on the INFO level, while previously it was logged on DEBUG. This means if the `go build` output is non-empty, goreleaser leaks the environment.

### PoC
* Create a Go project with dependencies, do not pull them yet (or run goreleaser later in a container, or delete `$GOPATH/pkg`).
* Make sure to have secrets set in the environment
* Make sure to not have `go mod tidy` in a before hook
* Run `goreleaser release --clean`
* Go prints lots of `go: downloading ...` lines, which triggers the "if output not empty, log it" line, which includes the environment.

### Impact
Credentials and tokens are leaked.

## References
- https://github.com/goreleaser/goreleaser/security/advisories/GHSA-f6mm-5fc7-3g3c
- https://github.com/goreleaser/goreleaser/pull/4787
- https://github.com/goreleaser/goreleaser/commit/22f734e41f7a5111a031a3a4eb714c1b6aa6456b
- https://github.com/goreleaser/goreleaser
