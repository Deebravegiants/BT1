# [H] Unexpected command execution in untrusted VCS repositories in cmd/go

## Summary
Severity: High
Advisory: BIT-golang-2025-4674
Aliases: CVE-2025-4674, GO-2025-3828
Ecosystem: Bitnami
Published: 2025-07-31
Source: https://osv.dev/vulnerability/BIT-golang-2025-4674
Type: osv

## Affected
- Bitnami: `golang` — affected >=1.24.0-0 <1.24.5

## Details
The go command may execute unexpected commands when operating in untrusted VCS repositories. This occurs when possibly dangerous VCS configuration is present in repositories. This can happen when a repository was fetched via one VCS (e.g. Git), but contains metadata for another VCS (e.g. Mercurial). Modules which are retrieved using the go command line, i.e. via "go get", are not affected.

## References
- https://go.dev/cl/686515
- https://go.dev/issue/74380
- https://groups.google.com/g/golang-announce/c/gTNJnDXmn34
- https://nvd.nist.gov/vuln/detail/CVE-2025-4674
- https://pkg.go.dev/vuln/GO-2025-3828
- http://www.openwall.com/lists/oss-security/2025/07/08/5
