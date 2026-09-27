# [M] Wasmtime vulnerable to Use After Free with `externref`s

## Summary
Severity: Medium
Advisory: GHSA-5fhj-g3p3-pq9g
CVE: CVE-2022-31146
CWE: CWE-416
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:L/A:L (CVSS_V3)
Published: 2022-07-20
Source: https://github.com/advisories/GHSA-5fhj-g3p3-pq9g
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0.37.0 <0.38.2
- crates.io: `cranelift-codegen` — affected >=0.84.0 <0.85.2

## Details
There is a bug in Wasmtime's code generator, Cranelift, where functions using reference types may be incorrectly missing metadata required for runtime garbage collection (GC). This means that if a GC happens at runtime then the collector will mistakenly think some Wasm stack frames do not have live references to garbage collected values and therefore reclaim and deallocate them. The function can then subsequently continue to use the values, leading later to use-after-free bugs. This bug was introduced in Cranelift's migration to the `regalloc2` register allocator in the Wasmtime 0.37.0 release on 2022-05-20. This bug has been patched and users should upgrade to Wasmtime version 0.38.2.

Mitigations for this issue can be achieved by doing one of:

* Disabling the reference types proposal by passing `false` to [`wasmtime::Config::wasm_reference_types`](https://docs.rs/wasmtime/0.38.0/wasmtime/struct.Config.html#method.wasm_reference_types).
* Downgrading to Wasmtime 0.36.0 or prior.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-5fhj-g3p3-pq9g
- https://nvd.nist.gov/vuln/detail/CVE-2022-31146
- https://github.com/bytecodealliance/wasmtime/commit/2ba4bce5cc719e5a74e571a534424614e62ecc41
- https://github.com/WebAssembly/reference-types
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2022-0100.html
