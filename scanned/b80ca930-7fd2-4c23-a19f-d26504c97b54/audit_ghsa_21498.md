# [M] Wasmtime out of bounds read/write with zero-memory-pages configuration

## Summary
Severity: Medium
Advisory: GHSA-44mr-8vmm-wjhg
CVE: CVE-2022-39392
CWE: CWE-119, CWE-125, CWE-787
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:H/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2022-11-10
Source: https://github.com/advisories/GHSA-44mr-8vmm-wjhg
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=2.0.0 <2.0.2
- crates.io: `wasmtime` — affected >=0 <1.0.2

## Details
### Impact

There is a bug in Wasmtime's implementation of its pooling instance allocator when the allocator is configured to give WebAssembly instances a maximum of zero pages of memory. In this configuration the virtual memory mapping for WebAssembly memories did not meet the compiler-required configuration requirements for safely executing WebAssembly modules. Wasmtime's default settings require virtual memory page faults to indicate that wasm reads/writes are out-of-bounds, but the pooling allocator's configuration would not create an appropriate virtual memory mapping for this meaning out of bounds reads/writes can successfully read/write memory unrelated to the wasm sandbox within range of the base address of the memory mapping created by the pooling allocator.

This bug can only be triggered by setting [`InstanceLimits::memory_pages`](https://docs.rs/wasmtime/2.0.1/wasmtime/struct.InstanceLimits.html#structfield.memory_pages) to zero. This is expected to be a very rare configuration since this means that wasm modules cannot allocate any pages of linear memory. All wasm modules produced by all current toolchains are highly likely to use linear memory, so it's expected to be unlikely that this configuration is set to zero by any production embedding of Wasmtime, hence the low severity of this bug despite the critical consequences.

### Patches

This bug has been patched and users should upgrade to Wasmtime 2.0.2.

### Workarounds

One way to mitigate this issue is to disable usage of the pooling allocator. Note that the pooling allocator is not enabled by default.

This bug can also only be worked around by increasing the `memory_pages` allotment when configuring the pooling allocator to a value greater than zero. If an embedding wishes to still prevent memory from actually being used then the `Store::limiter` method can be used to dynamically disallow growth of memory beyond 0 bytes large. Note that the default `memory_pages` value is greater than zero.

This bug is not applicable with the default settings of the `wasmtime` crate.

### References

* [`Config::allocation_strategy`](https://docs.rs/wasmtime/2.0.1/wasmtime/struct.Config.html#method.allocation_strategy) - configuration required to enable the pooling allocator.
* [`InstanceLimits::memory_pages`](https://docs.rs/wasmtime/2.0.1/wasmtime/struct.InstanceLimits.html#structfield.memory_pages) - configuration field that, when zero, exhibits this bug.
* [`Store::limiter`](https://docs.rs/wasmtime/2.0.1/wasmtime/struct.Store.html#method.limiter) - means of limiting memory without using `memory_pages`
* [Mailing list announcement](https://groups.google.com/a/bytecodealliance.org/g/sec-announce/c/c1HBDDJwNPA)
* [Patch for the `release-2.0.0` branch](https://github.com/bytecodealliance/wasmtime/commit/e60c3742904ccbb3e26da201c9221c38a4981d72)

### For more information

If you have any questions or comments about this advisory:

* Reach out to us on [the Bytecode Alliance Zulip chat](https://bytecodealliance.zulipchat.com/#narrow/stream/217126-wasmtime)
* Open an issue in [the bytecodealliance/wasmtime repository](https://github.com/bytecodealliance/wasmtime/)

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-44mr-8vmm-wjhg
- https://nvd.nist.gov/vuln/detail/CVE-2022-39392
- https://github.com/bytecodealliance/wasmtime/commit/e60c3742904ccbb3e26da201c9221c38a4981d72
- https://github.com/bytecodealliance/wasmtime
- https://groups.google.com/a/bytecodealliance.org/g/sec-announce/c/c1HBDDJwNPA
- https://rustsec.org/advisories/RUSTSEC-2022-0076.html
- https://rustsec.org/advisories/RUSTSEC-2022-0102.html
