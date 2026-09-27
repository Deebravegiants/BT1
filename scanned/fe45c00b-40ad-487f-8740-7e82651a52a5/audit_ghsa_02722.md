# [M] Wrong type for `Linker`-define functions when used across two `Engine`s

## Summary
Severity: Medium
Advisory: GHSA-q879-9g95-56mx
CVE: CVE-2021-39219
CWE: CWE-843
Ecosystem: PyPI, crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:N/I:H/A:H (CVSS_V3)
Published: 2021-09-20
Source: https://github.com/advisories/GHSA-q879-9g95-56mx
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0 <0.30.0
- PyPI: `wasmtime` — affected >=0 <0.30.0

## Details
### Impact

As a Rust library the `wasmtime` crate clearly marks which functions are safe and which are `unsafe`, guaranteeing that if consumers never use `unsafe` then it should not be possible to have memory unsafety issues in their embeddings of Wasmtime. An issue was discovered in the safe API of `Linker::func_*` APIs. These APIs were previously not sound when one `Engine` was used to create the `Linker` and then a different `Engine` was used to create a `Store` and then the `Linker` was used to instantiate a module into that `Store`. Cross-`Engine` usage of functions is not supported in Wasmtime and this can result in type confusion of function pointers, resulting in being able to safely call a function with the wrong type.

Triggering this bug requires using at least two `Engine` values in an embedding and then additionally using two different values with a `Linker` (one at the creation time of the `Linker` and another when instantiating a module with the `Linker`).

It's expected that usage of more-than-one `Engine` in an embedding is relatively rare since an `Engine` is intended to be a globally shared resource, so the expectation is that the impact of this issue is relatively small.

The fix implemented is to change this behavior to `panic!()` in Rust instead of silently allowing it. Using different `Engine` instances with a `Linker` is a programmer bug that `wasmtime` catches at runtime.

### Patches

This bug has been patched and users should upgrade to Wasmtime version 0.30.0.

### Workarounds

If you cannot upgrade Wasmtime and are using more than one `Engine` in your embedding it's recommended to instead use only one `Engine` for the entire program if possible. An `Engine` is designed to be a globally shared resource that is suitable to have only one for the lifetime of an entire process. If using multiple `Engine`s is required then code should be audited to ensure that `Linker` is only used with one `Engine`.

### For more information

If you have any questions or comments about this advisory:

* Reach out to us on [the Bytecode Alliance Zulip chat](https://bytecodealliance.zulipchat.com/#narrow/stream/217126-wasmtime)
* Open an issue in [the `bytecodealliance/wasmtime` repository](https://github.com/bytecodealliance/wasmtime/)

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-q879-9g95-56mx
- https://nvd.nist.gov/vuln/detail/CVE-2021-39219
- https://github.com/bytecodealliance/wasmtime/commit/b39f087414f27ae40c44449ed5d1154e03449bff
- https://crates.io/crates/wasmtime
- https://github.com/bytecodealliance/wasmtime
- https://github.com/bytecodealliance/wasmtime-py/compare/0.29.0...0.30.0
- https://github.com/pypa/advisory-database/tree/main/vulns/wasmtime/PYSEC-2021-322.yaml
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/WAVBRYDDUIY2ZR3K3FO4BVYJKIMJ5TP7
- https://lists.fedoraproject.org/archives/list/package-announce@lists.fedoraproject.org/message/Z2Z33FTXFQ6EOINVEQIP4DFBG53G5XIY
- https://rustsec.org/advisories/RUSTSEC-2021-0110.html
