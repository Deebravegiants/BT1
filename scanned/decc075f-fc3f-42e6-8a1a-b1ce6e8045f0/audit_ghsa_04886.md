# [M] nebula-mesh: Decrypted CA private key persists in heap after signing

## Summary
Severity: Medium
Advisory: GHSA-8h84-fhqq-q58v
CVE: CVE-2026-48025
CWE: CWE-244
Ecosystem: Go
Published: 2026-06-10
Source: https://github.com/advisories/GHSA-8h84-fhqq-q58v
Type: github-advisory

## Affected
- Go: `github.com/juev/nebula-mesh` — affected >=0 <0.3.7
- Go: `github.com/forgekeep/nebula-mesh` — affected >=0 <0.3.7

## Details
`internal/pki/resolver.go:36-64` constructs a `CAManager` with the plaintext `ed25519.PrivateKey` after unwrapping via the master key; `internal/pki/ca.go:13-16` stores it. Callers at `internal/api/enroll.go:116`, `internal/api/updates.go:297`, and `internal/api/mobile_bundle.go:40` use the manager for one `Sign()` and drop the reference on function return — but the underlying slice contents are not wiped before release.

The keystore package's contract (`internal/keystore/keystore.go` doc: *"Callers MUST zeroise the returned plaintext DEK as soon as it is no longer needed"*) is not met by the `CAManager` consumer. Decrypted CA private keys persist in process heap until Go's GC scavenges the underlying slice — minutes to hours under load, indefinitely on idle servers.

## Affected
All released versions up to v0.3.6.

## Threat model
Memory-read access: core dump, ptrace, kernel swap to disk, container/VM snapshot, OOM-debug bundle, side-channel via shared cache lines. Not a remote-network vulnerability, but defeats the master-key + envelope-encryption design's promise of "private key never lingers".

## Suggested fix
Add a `Wipe()` method on `CAManager`:

```go
// internal/pki/ca.go
func (m *CAManager) Wipe() {
    if m == nil {
        return
    }
    keystore.Zeroize(m.caKey)
}
```

At each call site (`enroll.go:116`, `updates.go:297`, `mobile_bundle.go:40`, and any new caller), `defer caMgr.Wipe()` immediately after the `Resolve()` call. Pattern mirrors the existing `defer keystore.Zeroize(dek)` discipline in the keystore package.

Optional follow-up: wrap `m.Sign()` to zeroize after each call, removing the contract on callers — but the `defer` pattern is sufficient as a minimum.

## References
- https://github.com/juev/nebula-mesh/security/advisories/GHSA-8h84-fhqq-q58v
- https://github.com/forgekeep/nebula-mesh/commit/bca1d5914fbaf3517d3b86145a802c00de4a8122
- https://github.com/forgekeep/nebula-mesh/releases/tag/v0.3.7
- https://github.com/juev/nebula-mesh
