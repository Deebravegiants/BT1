# [M] Wasmtime can panic when adding excessive fields to a `wasi:http/types.fields` instance

## Summary
Severity: Medium
Advisory: GHSA-243v-98vx-264h
CVE: CVE-2026-27572
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-243v-98vx-264h
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0 <24.0.6
- crates.io: `wasmtime` — affected >=25.0.0 <36.0.6
- crates.io: `wasmtime` — affected >=37.0.0 <40.0.4

## Details
### Impact

Wasmtime's implementation of the `wasi:http/types.fields` resource is susceptible to panics when too many fields are added to the set of headers. Wasmtime's implementation in the `wasmtime-wasi-http` crate is backed by a data structure which panics when it reaches excessive capacity and this condition was not handled gracefully in Wasmtime. Panicking in a WASI implementation is a Denial of Service vector for embedders and is treated as a security vulnerability in Wasmtime.

### Patches

Wasmtime 24.0.6, 36.0.6, 40.0.4, 41.0.4, and 42.0.0 patch this vulnerability and return a trap to the guest instead of panicking.

### Workarounds

There are no known workarounds at this time, embedders are encouraged to update to a patched version of Wasmtime.

### Resources

* [Limitations of `http::HeaderMap`](https://docs.rs/http/1.4.0/http/header/#limitations)

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-243v-98vx-264h
- https://nvd.nist.gov/vuln/detail/CVE-2026-27572
- https://github.com/bytecodealliance/wasmtime/commit/301dc7162cca51def19131019af1187f45901c0a
- https://docs.rs/http/1.4.0/http/header/#limitations
- https://github.com/bytecodealliance/wasmtime
- https://github.com/bytecodealliance/wasmtime/releases/tag/v24.0.6
- https://github.com/bytecodealliance/wasmtime/releases/tag/v36.0.6
- https://github.com/bytecodealliance/wasmtime/releases/tag/v40.0.4
- https://github.com/bytecodealliance/wasmtime/releases/tag/v41.0.4
- https://rustsec.org/advisories/RUSTSEC-2026-0021.html
