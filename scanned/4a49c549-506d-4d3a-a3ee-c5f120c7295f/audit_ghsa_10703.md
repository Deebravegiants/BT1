# [M] Wasmtime: Heap OOB read in component model UTF-16 to latin1+utf16 string transcoding

## Summary
Severity: Medium
Advisory: GHSA-hx6p-xpx3-jvvv
CVE: CVE-2026-34941
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:H (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-hx6p-xpx3-jvvv
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0 <24.0.7
- crates.io: `wasmtime` — affected >=25.0.0 <36.0.7
- crates.io: `wasmtime` — affected >=37.0.0 <42.0.2
- crates.io: `wasmtime` — affected >=43.0.0 <43.0.1

## Details
### Summary

Wasmtime contains a vulnerability where when transcoding a UTF-16 string to the latin1+utf16 component-model encoding it would incorrectly validate the byte length of the input string when performing a bounds check. Specifically the number of code units were checked instead of the byte length, which is twice the size of the code units.

This vulnerability can cause the host to read beyond the end of a WebAssembly's linear memory in an attempt to transcode nonexistent bytes. In Wasmtime's default configuration this will read unmapped memory on a guard page, terminating the process with a segfault. Wasmtime can be configured, however, without guard pages which would mean that host memory beyond the end of linear memory may be read and interpreted as UTF-16.

A host segfault is a denial-of-service vulnerability in Wasmtime, and possibly being able to read beyond the end of linear memory is additionally a vulnerability. Note that reading beyond the end of linear memory requires nonstandard configuration of Wasmtime, specifically with guard pages disabled.

### Impact

This is an out-of-bounds memory access. Any user running untrusted wasm components that use cross-component string passing (with UTF-16 source and latin1+utf16 destination encodings) is affected.

- With guard pages: Denial of service. The host process crashes with SIGBUS/SIGSEGV.
- Without guard pages: Potential information disclosure. The guest can read host memory beyond its linear memory allocation.

Patches

Wasmtime 24.0.7, 36.0.7, 42.0.2, and 43.0.1 have been issued to fix this bug. Users are recommended to update to these patched versions of Wasmtime.
Workarounds

There is no workaround for this bug. Hosts are recommended to updated to a patched version of Wasmtime.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-hx6p-xpx3-jvvv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34941
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2026-0093.html
