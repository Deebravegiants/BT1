# [M] Wasmtime segfault or unused out-of-sandbox load with `f64x2.splat` operator on x86-64 

## Summary
Severity: Medium
Advisory: GHSA-qqfj-4vcm-26hv
CVE: CVE-2026-34944
CWE: CWE-248, CWE-789
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:L/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-09
Source: https://github.com/advisories/GHSA-qqfj-4vcm-26hv
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0 <24.0.7
- crates.io: `wasmtime` — affected >=25.0.0 <36.0.7
- crates.io: `wasmtime` — affected >=37.0.0 <42.0.2
- crates.io: `wasmtime` — affected >=43.0.0 <43.0.1

## Details
On x86-64 platforms with SSE3 disabled Wasmtime's compilation of the `f64x2.splat` WebAssembly instruction with Cranelift may load 8 more bytes than is necessary. When [signals-based-traps](https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.signals_based_traps) are disabled this can result in a uncaught segfault due to loading from unmapped guard pages. With guard pages disabled it's possible for out-of-sandbox data to be loaded, but this data is not visible to WebAssembly guests.

### Details

The `f64x2.splat` operator, when operating on a value loaded from a memory (for example with f64.load), compiles with Cranelift to code on x86-64 without SSE3 that loads 128 bits (16 bytes) rather than the expected 64 bits (8 bytes) from memory. When the address is in-bounds for a (correct) 8-byte load but not an (incorrect) 16-byte load, this can load beyond memory by up to 8 bytes. This can result in three different behaviors depending on Wasmtime's configuration:

1.  If guard pages are disabled then this extra data will be loaded. The extra data is present in the upper bits of a register, but the upper bits are not visible to WebAssembly guests. Actually witnessing this data would require a different bug in Cranelift, of which none are known. Thus in this situation while it's something we're patching in Cranelift it's not a security issue.
2. If guard pages are enabled, and [signals-based-traps](https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.signals_based_traps) are enabled, then this operation will result in a safe WebAssembly trap. The trap is incorrect because the load is not out-of-bounds as defined by WebAssembly, but this mistakenly widened load will load bytes from an unmapped guard page, causing a segfault which is caught and handled as a Wasm trap. In this situation this is not a security issue, but we're patching Cranelift to fix the WebAssembly behavior.
3. If guard pages are enabled, and [signals-based-traps](https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.signals_based_traps) are disabled, then this operation results in an uncaught segfault. Like the previous case with guard pages enabled this will load from an unmapped guard page. Unlike before, however, signals-based-traps are disabled meaning that signal handlers aren't configured. The resulting segfault will, by default, terminate the process. This is a security issue from a DoS perspective, but does not represent an arbitrary read or write from WebAssembly, for example.

Wasmtime's default configuration is case (2) in this case. That means that Wasmtime, by default, incorrectly executes this 
WebAssembly instruction but does not have insecure behavior.

### Impact

If [signals-based-traps](https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.signals_based_traps) are disabled and guard pages are enabled then guests can trigger an uncaught segfault in the host, likely aborting the host process. This represents, for example, a DoS vector for WebAssembly guests.

This bug does not affect Wasmtime's default configuration and requires [signals-based-traps](https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.signals_based_traps) to be disabled. This bug only affects the x86-64 target with the SSE3 feature disabled and the Cranelift backend (Wasmtime's default backend).

### Patches

Wasmtime 24.0.7, 36.0.7, 42.0.2, and 43.0.1 have been issued to fix this bug. Users are recommended to update to these patched versions of Wasmtime.

### Workarounds

This bug only affects x86-64 hosts where SSE3 is disabled. If SSE3 is enabled or if a non-x86-64 host is used then hosts are not affect. Otherwise there are no known workarounds to this issue.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-qqfj-4vcm-26hv
- https://nvd.nist.gov/vuln/detail/CVE-2026-34944
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2026-0087.html
