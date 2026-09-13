# [M] go-ipld-prime/codec/json may panic if asked to encode bytes

## Summary
Severity: Medium
Advisory: GHSA-c653-6hhg-9x92
CVE: CVE-2023-22460
CWE: CWE-20
Ecosystem: Go
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2023-01-05
Source: https://github.com/advisories/GHSA-c653-6hhg-9x92
Type: github-advisory

## Affected
- Go: `github.com/ipld/go-ipld-prime` — affected >=0 <0.19.0

## Details
`go-ipld-prime` is a series of Go interfaces for manipulating IPLD data and a Go module that contains the `go-ipld-prime/codec/json` codec.

### Impact

Encoding data which contains a `Bytes` kind Node will pass a `Bytes` token to the JSON encoder which will panic as it doesn't expect to receive `Bytes` tokens. Such an encoding should be treated as an error, as plain JSON should not be able to encode Bytes.

**This only impacts uses of the "json" codec, "dag-json" is not impacted.** Use of "json" as a decoder is not impacted.

### Patches

Fixed in v0.19.0.

### Workarounds

Prefer the "dag-json" codec which has the ability to [encode bytes](https://ipld.io/specs/codecs/dag-json/spec/#bytes).

### References

See fix in [#472](https://github.com/ipld/go-ipld-prime/pull/472)

## References
- https://github.com/ipld/go-ipld-prime/security/advisories/GHSA-c653-6hhg-9x92
- https://nvd.nist.gov/vuln/detail/CVE-2023-22460
- https://github.com/ipld/go-ipld-prime/pull/472
- https://github.com/ipld/go-ipld-prime/commit/146d1c8529676fe9ee0604f014656af2395505fc
- https://github.com/ipld/go-ipld-prime
- https://github.com/ipld/go-ipld-prime/releases/tag/v0.19.0
- https://pkg.go.dev/vuln/GO-2023-1269
