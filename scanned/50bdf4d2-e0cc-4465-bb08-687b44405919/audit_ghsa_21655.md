# [M] Invalid drop of partially-initialized instances in the pooling instance allocator for modules with defined `externref` globals 

## Summary
Severity: Medium
Advisory: GHSA-88xq-w8cq-xfg7
CVE: CVE-2022-23636
CWE: CWE-824
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2022-02-16
Source: https://github.com/advisories/GHSA-88xq-w8cq-xfg7
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0.34.0 <0.34.1
- crates.io: `wasmtime` — affected >=0 <0.33.1

## Details
### Impact

There exists a bug in the pooling instance allocator in Wasmtime's runtime where a failure to instantiate an instance for a module that defines an `externref` global will result in an invalid drop of a `VMExternRef` via an uninitialized pointer.

As instance slots may be reused between consecutive instantiations, the value of the uninitialized pointer may be from a previous instantiation and therefore under the control of an attacker via a module's initial values for its globals. If the attacker can somehow determine an address under their control inside the mapped memory representing the instance pool, it is possible to trick the runtime to call `drop_in_place` on a trait object under the attacker's control and therefore cause remote code execution.

Exploiting the bug to cause remote code execution would be very difficult as attackers cannot determine the addresses of globals from code executing within the WebAssembly VM and the memory space for the instance pool cannot be statically determined. Operating system mitigations, such as [address space layout randomization](https://en.wikipedia.org/wiki/Address_space_layout_randomization), would additionally increase the difficulty for attackers to determine useful executable code to target with an exploit. It is also very unlikely that attackers will be able to directly influence the conditions that trigger the bug as described below.

When the conditions to trigger the bug are met, however, it is much easier to exploit this bug to cause a denial of service by crashing the host with an invalid memory read.

The following engine configuration (via [Config](https://docs.rs/wasmtime/0.34.0/wasmtime/struct.Config.html)) is required to be impacted by this bug:

* support for the reference types proposal must be enabled (this is the default for `Config`).
* a pooling allocation strategy must be configured via [Config::allocation_strategy](https://docs.rs/wasmtime/0.34.0/wasmtime/struct.Config.html#method.allocation_strategy), which is **not the default allocation strategy**.

A module must be instantiated with **all the following characteristics**:

* The module defines at least one table or memory.
* The module defines at least one `externref` global.

During instantiation, **one of the following** must occur to cause the instantiation to fail:

* a call to `mprotect` or `VirtualAlloc` fails (e.g. out-of-memory conditions).
* a resource limiter was configured in the associated `Store` (via [Store::limiter](https://docs.rs/wasmtime/0.34.0/wasmtime/struct.Store.html#method.limiter) or [Store::limiter_async](https://docs.rs/wasmtime/0.34.0/wasmtime/struct.Store.html#method.limiter_async)) and the limiter returns `false` from the initial call to `memory_growing` or `table_growing`. **Stores do not have a resource limiter set by default**.

This results in a partially-initialized instance being dropped and that attempts to drop the uninitialized `VMExternRef` representing the defined `externref` global.

We have reason to believe that the effective impact of this bug is relatively small because the usage of `externref` is still uncommon and without a resource limiter configured on the `Store`, which is not the default configuration, it is only possible to trigger the bug from an error returned by `mprotect` or `VirtualAlloc`.

Note that on Linux with the `uffd` feature enabled, it is only possible to trigger the bug from a resource limiter as the call to `mprotect` is skipped; if no resource limiter is used, then this configuration is not vulnerable.

### Patches

The bug has been fixed in 0.34.1 and 0.33.1; users are encouraged to upgrade as soon as possible.

### Workarounds

If it is not possible to upgrade to 0.34.1 or 0.33.1 of the `wasmtime` crate, it is recommend that support for the reference types proposal be disabled by passing `false` to [Config::wasm_reference_types](https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.wasm_reference_types).

Doing so will prevent modules that use `externref` from being loaded entirely.

### For more information

If you have any questions or comments about this advisory:

* Reach out to us on [the Bytecode Alliance Zulip chat](https://bytecodealliance.zulipchat.com/#narrow/stream/217126-wasmtime)
* Open an issue in [the bytecodealliance/wasmtime repository](https://github.com/bytecodealliance/wasmtime/)

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-88xq-w8cq-xfg7
- https://nvd.nist.gov/vuln/detail/CVE-2022-23636
- https://github.com/bytecodealliance/wasmtime/commit/886ecc562040bef61faf19438c22285c2d62403a
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2022-0096.html
