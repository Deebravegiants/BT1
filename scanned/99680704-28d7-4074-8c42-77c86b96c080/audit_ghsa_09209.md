# [M] wasmtime has a panic when allocating a table exceeding the size of the host's address space

## Summary
Severity: Medium
Advisory: GHSA-p8xm-42r7-89xg
CVE: CVE-2026-44216
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-05-07
Source: https://github.com/advisories/GHSA-p8xm-42r7-89xg
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=30.0.0 <36.0.8
- crates.io: `wasmtime` — affected >=37.0.0 <43.0.2

## Details
### Impact

Wasmtime's allocation logic for a WebAssembly table contained checked arithmetic which panicked on overflow. This overflow is possible to trigger, and thus panic, when a table with an extremely large size is allocated. This is possible with the WebAssembly memory64 proposal where tables can have sizes in the 64-bit range as opposed to the previous 32-bit range which would not overflow. The panic happens when attempting to create a very large table, such as when instantiating a WebAssembly module or component.

This bug does not affect the pooling allocator which limits tables sizes to much less than the required amount to trigger the overflow. This bug is only present for the on-demand instance allocator, which is Wasmtime's default allocator. This bug also requires the `memory64` WebAssembly feature to be enabled, which is on-by-default.

Panicking in the host process is considered a denial-of-service vector for Wasmtime.

### Patches

Wasmtime 36.0.8, 43.0.2, and 44.0.1 have all been released which fixes this issue.

### Workarounds

Embeddings can switch to using the pooling allocator to work around this issue, or the `memory64` WebAssembly proposal can be disabled. Otherwise there is no workaround and users are recommended to upgrade.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-p8xm-42r7-89xg
- https://nvd.nist.gov/vuln/detail/CVE-2026-44216
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2026-0114.html
