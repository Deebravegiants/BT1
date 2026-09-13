# [M] Out-of-bounds read/write and invalid free with `externref`s and GC safepoints in Wasmtime 

## Summary
Severity: Medium
Advisory: GHSA-4873-36h9-wv49
CVE: CVE-2021-39218
CWE: CWE-125, CWE-590, CWE-787
Ecosystem: PyPI, crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-4873-36h9-wv49
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0.26.0 <0.30.0
- PyPI: `wasmtime` — affected >=0.26.0 <0.30.0

## Details
### Impact

There was an invalid free and out-of-bounds read and write bug when running Wasm that uses `externref`s in Wasmtime.

To trigger this bug, Wasmtime needs to be running Wasm that uses `externref`s, the host creates non-null `externrefs`, Wasmtime performs a garbage collection (GC), and there has to be a Wasm frame on the stack that is at a GC safepoint where

* there are no live references at this safepoint, and
* there is a safepoint with live references earlier in this frame's function.

Under this scenario, Wasmtime would incorrectly use the GC stack map for the safepoint from earlier in the function instead of the empty safepoint. This would result in Wasmtime treating arbitrary stack slots as `externref`s that needed to be rooted for GC. At the *next* GC, it would be determined that nothing was referencing these bogus `externref`s (because nothing could ever reference them, because they are not really `externref`s) and then Wasmtime would deallocate them and run `<ExternRef as Drop>::drop` on them. This results in a free of memory that is not necessarily on the heap (and shouldn't be freed at this moment even if it was), as well as potential out-of-bounds reads and writes.

Even though support for `externref`s (via the reference types proposal) is enabled by default, unless you are creating non-null `externref`s in your host code or explicitly triggering GCs, you cannot be affected by this bug.

We have reason to believe that the effective impact of this bug is relatively small because usage of `externref` is currently quite rare.

### Patches

This bug has been patched and users should upgrade to Wasmtime version 0.30.0.

Additionally, we have updated [our primary `externref` fuzz target](https://github.com/bytecodealliance/wasmtime/blob/37c094faf53f1b356aab3c79d451395e4f7edb34/fuzz/fuzz_targets/table_ops.rs) such that it better exercises these code paths and we can have greater confidence in their correctness going forward.

### Workarounds

If you cannot upgrade Wasmtime at this time, you can avoid this bug by disabling the reference types proposal by passing `false` to [`wasmtime::Config::wasm_reference_types`](https://docs.rs/wasmtime/0.29.0/wasmtime/struct.Config.html#method.wasm_reference_types)

### References

* [The Wasm reference types proposal, which introduces `externref`](https://github.com/WebAssembly/reference-types/)

### For more information

If you have any questions or comments about this advisory:

* Reach out to us on [the Bytecode Alliance Zulip chat](https://bytecodealliance.zulipchat.com/#narrow/stream/217126-wasmtime)
* Open an issue in [the `bytecodealliance/wasmtime` repository](https://github.com/bytecodealliance/wasmtime/)

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-4873-36h9-wv49
- https://nvd.nist.gov/vuln/detail/CVE-2021-39218
- https://github.com/bytecodealliance/wasmtime/commit/398a73f0dd862dbe703212ebae8e34036a18c11c
- https://crates.io/crates/wasmtime
- https://github.com/bytecodealliance/wasmtime
- https://github.com/bytecodealliance/wasmtime-py/compare/0.29.0...0.30.0
- https://github.com/pypa/advisory-database/tree/main/vulns/wasmtime/PYSEC-2021-321.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WAVBRYDDUIY2ZR3K3FO4BVYJKIMJ5TP7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z2Z33FTXFQ6EOINVEQIP4DFBG53G5XIY
- https://rustsec.org/advisories/RUSTSEC-2021-0110.html
