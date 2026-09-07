# [M] wasmtime_jit_debug Dumps Undefined Memory by `JitDumpFile`

## Summary
Severity: Medium
Advisory: GHSA-9ghp-w2hm-vfpf
CWE: CWE-119
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:L/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2025-06-17
Source: https://github.com/advisories/GHSA-9ghp-w2hm-vfpf
Type: github-advisory

## Affected
- crates.io: `wasmtime-jit-debug` — affected >=0 <24.0.0

## Details
The unsound function `dump_code_load_record` uses `from_raw_parts` to directly convert the pointer `addr` and `len` into a slice without any validation and that memory block would be dumped.

Thus, the 'safe' function dump_code_load_record is actually 'unsafe' since it requires the caller to guarantee that the addr is valid and len must not overflow. Otherwise, the function could dump the memory into file illegally, causing memory leak.

> **Note**: this is an internal-only crate in the Wasmtime project not intended for external use and is more strongly signaled nowadays as of [bytecodealliance/wasmtime#10963](https://github.com/bytecodealliance/wasmtime/pull/10963). Please open an issue in Wasmtime if you're using this crate directly.

## References
- https://github.com/bytecodealliance/wasmtime/issues/8905
- https://github.com/bytecodealliance/wasmtime/commit/b5e31a5c33725ab8a7dfbe8505c56b5cf282ffed
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2024-0442.html
