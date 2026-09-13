# [M] Wasmtime has host data leakage with 64-bit tables and Winch

## Summary
Severity: Medium
Advisory: JLSEC-2026-1358
Ecosystem: Julia
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-08-21
Source: https://osv.dev/vulnerability/JLSEC-2026-1358
Type: osv

## Affected
- Julia: `Wasmtime_jll` — affected >=39.0.0+0 <45.0.1+0

## Details
### Impact

Wasmtime's Winch compiler contains a bug where a 64-bit table, part of the memory64 proposal of WebAssembly, incorrectly translated the `table.size` instruction. This bug could lead to disclosing data on the host's stack to WebAssembly guests. The host's stack can possibly contain sensitive data related to other host-originating operations which is not intended to be disclosed to guests.

This bug specifically arose from a mistake where the return value of `table.size` was statically typed as a 32-bit integer, as opposed to consulting the table's index type to see how large the returned register could be. When combined with details about Wnich's ABI, such as multi-value returns, this can be combined to read stack data from the host, within a guest. This information disclosure should not be possible in WebAssembly, violates spec semantics, and is a vulnerability in Wasmtime.

### Patches

Wasmtime 36.0.7, 42.0.2, and 43.0.1 have been issued to fix this bug. Users are recommended to update to these patched versions of Wasmtime.

### Workarounds

Users of Cranelift are not affected by this issue, but users of Winch have no workarounds other than disabling the `Config::wasm_memory64` proposal.

## References
- https://github.com/advisories/GHSA-m9w2-8782-2946
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-m9w2-8782-2946
- https://nvd.nist.gov/vuln/detail/CVE-2026-34945
- https://rustsec.org/advisories/RUSTSEC-2026-0086.html
