# [H] ipld/go-codec-dagpb panics when processing certain blocks

## Summary
Severity: High
Advisory: GHSA-g3vv-g2j5-45f2
CVE: CVE-2022-2584
CWE: CWE-119
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-04-08
Source: https://github.com/advisories/GHSA-g3vv-g2j5-45f2
Type: github-advisory

## Affected
- Go: `github.com/ipld/go-codec-dagpb` — affected >=0 <1.3.1

## Details
### Impact 
Decoding certain blocks using the go-ipld-prime version of the dag-pb codec (go-codec-dagpb) can cause a panic.  The panic comes from an assumption that the reported link length is accurate, but if the block ends before that reported length then it’s a buffer overread.

### Patches
The issue is fixed in v1.3.1 and above.

Consumers can discover the versions of `go-codec-dagpb` in a module's dependency graph using the following command in the module root:

```go mod graph | grep go-codec-dagpb```

### Workarounds
You can work around this issue without upgrading by recovering panics higher in the call stack of the goroutine that calls the defective code.

### For more information
If you have any questions or comments about this advisory:

* Ask in [IPFS Discord #ipld-chatter](https://discord.gg/ipfs)
* Open an issue in [go-codec-dagpb](https://github.com/ipld/go-codec-dagpb)

## References
- https://github.com/ipld/go-codec-dagpb/security/advisories/GHSA-g3vv-g2j5-45f2
- https://nvd.nist.gov/vuln/detail/CVE-2022-2584
- https://github.com/ipld/go-codec-dagpb/commit/a17ace35cc760a2698645c09868f9050fa219f57
- https://pkg.go.dev/vuln/GO-2022-0422
- github.com/ipld/go-codec-dagpb
