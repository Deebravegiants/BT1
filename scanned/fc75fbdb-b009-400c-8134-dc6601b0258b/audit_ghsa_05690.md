# [M] Wasmtime segfault or unused out-of-sandbox load with f64.copysign operator on x86-64

## Summary
Severity: Medium
Advisory: GHSA-vc8c-j3xm-xj73
CVE: CVE-2026-24116
CWE: CWE-125
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:L/AC:L/AT:P/PR:L/UI:A/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-01-27
Source: https://github.com/advisories/GHSA-vc8c-j3xm-xj73
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=29.0.0 <36.0.5
- crates.io: `wasmtime` — affected >=37.0.0 <40.0.3
- crates.io: `wasmtime` — affected >=41.0.0 <41.0.1

## Details
On x86-64 platforms with AVX Wasmtime's compilation of the `f64.copysign` WebAssembly instruction with Cranelift may load 8 more bytes than is necessary. When [signals-based-traps] are disabled this can result in a uncaught segfault due to loading from unmapped guard pages. With guard pages disabled it's possible for out-of-sandbox data to be loaded, but unless there is another bug in Cranelift this data is not visible to WebAssembly guests.

### Details

The `f64.copysign` operator, when operating on a value loaded from a memory (for example with `f64.load`), compiles with Cranelift to code on x86-64 with AVX that loads 128 bits (16 bytes) rather than the expected 64 bits (8 bytes) from memory. When the address is in-bounds for a (correct) 8-byte load but not an (incorrect) 16-byte load, this can load beyond memory by up to 8 bytes. This can result in three different behaviors depending on Wasmtime's configuration:

1. If guard pages are disabled then this extra data will be loaded. The extra data is present in the upper bits of a register, but the upper bits are not visible to WebAssembly guests. Actually witnessing this data would require a different bug in Cranelift, of which none are known. Thus in this situation while it's something we're patching in Cranelift it's not a security issue.
2. If guard pages are enabled, and [signals-based-traps] are enabled, then this operation will result in a safe WebAssembly trap. The trap is incorrect because the load is not out-of-bounds as defined by WebAssembly, but this mistakenly widened load will load bytes from an unmapped guard page, causing a segfault which is caught and handled as a Wasm trap. In this situation this is not a security issue, but we're patching Cranelift to fix the WebAssembly behavior.
3. If guard pages are enabled, and [signals-based-traps] are disabled, then this operation results in an uncaught segfault. Like the previous case with guard pages enabled this will load from an unmapped guard page. Unlike before, however, signals-based-traps are disabled meaning that signal handlers aren't configured. The resulting segfault will, by default, terminate the process. This is a security issue from a DoS perspective, but does not represent an arbitrary read or write from WebAssembly, for example.

Wasmtime's default configuration is case (2) in this case. That means that Wasmtime, by default, incorrectly executes this WebAssembly instruction but does not have insecure behavior.

### Impact

If [signals-based-traps] are disabled and guard pages are enabled then guests can trigger an uncaught segfault in the host, likely aborting the host process. This represents, for example, a DoS vector for WebAssembly guests.

This bug does not affect Wasmtime's default configuration and requires [signals-based-traps] to be disabled. This bug only affects the x86-64 target with the AVX feature enabled and the Cranelift backend (Wasmtime's default backend).

### Patches

Wasmtime 36.0.5, 40.0.3, and 41.0.1 have been released to fix this issue. Users are recommended to upgrade to the patched versions of Wasmtime. Other affected versions [are not patched](https://docs.wasmtime.dev/stability-release.html) and users should updated to supported major version instead.

### Workarounds

This bug can be worked around by enabling [signals-based-traps]. While disabling guard pages can be a quick fix in some situations, it's not recommended to disabled guard pages as it is a key defense-in-depth measure of Wasmtime.

### Resources

* [signals-based-traps configuration][signals-based-traps]
* [guard pages configuration](https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.memory_guard_size)

[signals-based-traps]: https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.signals_based_traps

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-vc8c-j3xm-xj73
- https://nvd.nist.gov/vuln/detail/CVE-2026-24116
- https://github.com/bytecodealliance/wasmtime/commit/728fa07184f8da2a046f48ef9b61f869dce133a6
- https://github.com/bytecodealliance/wasmtime/commit/799585fc362fcb991de147dd1a9f2ba0861ed440
- https://github.com/bytecodealliance/wasmtime/commit/ac92d9bb729ad3a6d93f0724c4c33a0c4a9c0227
- https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.memory_guard_size
- https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.signals_based_traps
- https://docs.wasmtime.dev/stability-release.html
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2026-0006.html
