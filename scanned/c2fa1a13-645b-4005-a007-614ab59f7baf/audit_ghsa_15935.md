# [M] wasmtime has a runtime crash when combining tail calls with trapping imports

## Summary
Severity: Medium
Advisory: GHSA-q8hx-mm92-4wvg
CVE: CVE-2024-47763
CWE: CWE-617, CWE-670
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2024-10-09
Source: https://github.com/advisories/GHSA-q8hx-mm92-4wvg
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=12.0.0 <21.0.2
- crates.io: `wasmtime` — affected >=22.0.0 <22.0.1
- crates.io: `wasmtime` — affected >=23.0.0 <23.0.3
- crates.io: `wasmtime` — affected >=24.0.0 <24.0.1
- crates.io: `wasmtime` — affected >=25.0.0 <25.0.2

## Details
### Impact

Wasmtime's implementation of WebAssembly tail calls combined with stack traces can result in a runtime crash in certain WebAssembly modules. The runtime crash may be undefined behavior if Wasmtime was compiled with Rust 1.80 or prior. The runtime crash is a deterministic process abort when Wasmtime is compiled with Rust 1.81 and later.

[WebAssembly tail calls](https://github.com/webassembly/tail-call) are a proposal which relatively recently reached stage 4 in the [standardization process](https://github.com/WebAssembly/proposals/). Wasmtime first enabled support for tail calls by default [in Wasmtime 21.0.0](https://github.com/bytecodealliance/wasmtime/pull/8540), although that release contained a bug where it was only on-by-default for some configurations. In [Wasmtime 22.0.0](https://github.com/bytecodealliance/wasmtime/pull/8682) tail calls were enabled by default for all configurations.

The specific crash happens when an exported function in a WebAssembly module (or component) performs a `return_call` (or `return_call_indirect` or `return_call_ref`) to an imported host function which captures a stack trace (for example, the host function raises a trap). In this situation, the stack-walking code previously assumed there was always at least one WebAssembly frame on the stack but with tail calls that is no longer true. With the tail-call proposal it's possible to have an entry trampoline appear as if it directly called the exit trampoline. This situation triggers an internal assert in the stack-walking code which raises a Rust `panic!()`.

When Wasmtime is compiled with Rust versions 1.80 and prior this means that an `extern "C"` function in Rust is raising a `panic!()`. This is technically undefined behavior and typically manifests as a process abort when the unwinder fails to unwind Cranelift-generated frames. When Wasmtime is compiled with Rust versions 1.81 and later this panic becomes a deterministic process abort.

Overall the impact of this issue is that this is a denial-of-service vector where a malicious WebAssembly module or component can cause the host to crash. There is no other impact at this time other than availability of a service as the result of the crash is always a crash and no more.

This issue was discovered by routine fuzzing performed by the Wasmtime project via Google's OSS-Fuzz infrastructure. We have no evidence that it has ever been exploited by an attacker in the wild.

### Patches

All versions of Wasmtime which have tail calls enabled by default have been patched:

* 21.0.x - patched in 21.0.2
* 22.0.x - patched in 22.0.1
* 23.0.x - patched in 23.0.3 
* 24.0.x - patched in 24.0.1
* 25.0.x - patched in 25.0.2

Wasmtime versions from 12.0.x (the first release with experimental tail call support) to 20.0.x (the last release with tail-calls off-by-default) have support for tail calls but the support is disabled by default. These versions are not affected in their default configurations, but users who explicitly enabled tail call support will need to either disable tail call support or upgrade to a patched version of Wasmtime.

### Workarounds

The main workaround for this issue is to disable tail support for tail calls in Wasmtime, for example with [`Config::wasm_tail_call(false)`](https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.wasm_tail_call). Users are otherwise encouraged to upgrade to patched versions.

### References

* [Wasmtime's initial implementation of tail calls](https://github.com/bytecodealliance/wasmtime/pull/6774)
* [Enabling of tail calls in 21.0.0](https://github.com/bytecodealliance/wasmtime/pull/8540)
* [Fully enabling tail calls in 22.0.0](https://github.com/bytecodealliance/wasmtime/pull/8682)
* [The WebAssembly's `tail-call` proposal](https://github.com/webassembly/tail-call)

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-q8hx-mm92-4wvg
- https://nvd.nist.gov/vuln/detail/CVE-2024-47763
- https://github.com/bytecodealliance/wasmtime/pull/6774
- https://github.com/bytecodealliance/wasmtime/pull/8540
- https://github.com/bytecodealliance/wasmtime/pull/8682
- https://github.com/bytecodealliance/wasmtime/commit/0ebe54d05f0e1f6c64b7c8bb48c9e9f6c95cacba
- https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.wasm_tail_call
- https://github.com/WebAssembly/proposals
- https://github.com/bytecodealliance/wasmtime
- https://github.com/pypa/advisory-database/tree/main/vulns/wasmtime-bin/PYSEC-2024-312.yaml
- https://github.com/webassembly/tail-call
- https://rustsec.org/advisories/RUSTSEC-2024-0440.html
