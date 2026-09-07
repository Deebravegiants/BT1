# [H] nebula-mesh: CA private key not zeroized on web mobile-bundle error paths

## Summary
Severity: High
Advisory: GHSA-2p2f-px33-4vv5
CVE: CVE-2026-53604
CWE: CWE-212, CWE-316
Ecosystem: Go
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-07-14
Source: https://github.com/advisories/GHSA-2p2f-px33-4vv5
Type: github-advisory

## Affected
- Go: `github.com/forgekeep/nebula-mesh` — affected >=0 <0.3.8

## Details
## Impact

The web handler `renderMobileBundle` (`internal/web/handlers.go:1325`) passes the real `*pki.CAResolver` directly into `mobilebundle.Build`. Inside `Build` (`internal/mobilebundle/builder.go:54`), `resolver.LoadByID` decrypts the CA's ed25519 private key into a `*pki.CAManager`, but `Build` never calls `CAManager.Wipe()` on any return path (success or any of the error paths at lines 56, 62, 68, 80, 86, 92, 98, 102, 109, 118, 150).

As a result, when a mobile-bundle request goes through the **web** UI and `Build` returns — especially on error (missing network, invalid prefix, DB error, signing failure) — the plaintext CA private key remains on the Go heap, unwiped, until garbage collection. An attacker able to read process memory (core dump, swap, memory-scraping) can recover the CA signing key, which would allow minting arbitrary host certificates for the mesh.

The **API** handler (`internal/api/mobile_bundle.go:74`) already does this correctly: it loads the `CAManager`, `defer caMgr.Wipe()`, and wraps it in `caManagerResolver`. Only the web path is affected.

This is the same key-zeroization class previously addressed in GHSA-8h84-fhqq-q58v.

## Patches

Add `defer caMgr.Wipe()` inside `mobilebundle.Build` immediately after the `LoadByID` call so every caller (web and API) is protected on all return paths. Ensure `CAManager.Wipe()` is idempotent, since the API handler also wipes the same manager.

## Workarounds

None at the configuration level; requires a code fix.

## Resources

- `internal/web/handlers.go:1325`
- `internal/mobilebundle/builder.go:54`
- `internal/api/mobile_bundle.go:74` (correct reference implementation)
- Prior related advisory: GHSA-8h84-fhqq-q58v

## References
- https://github.com/forgekeep/nebula-mesh/security/advisories/GHSA-2p2f-px33-4vv5
- https://github.com/forgekeep/nebula-mesh/commit/1f1ab9aa8472239763d967e3d50a3cd53a1a79b9
- https://github.com/forgekeep/nebula-mesh
- https://github.com/forgekeep/nebula-mesh/releases/tag/v0.3.8
