# [M] Wasmtime is vulnerable to panic when dropping a `[Typed]Func::call_async` future

## Summary
Severity: Medium
Advisory: GHSA-xjhv-v822-pf94
CVE: CVE-2026-27195
CWE: CWE-755
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:P/VC:N/VI:N/VA:H/SC:N/SI:N/SA:H (CVSS_V4)
Published: 2026-02-24
Source: https://github.com/advisories/GHSA-xjhv-v822-pf94
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=39.0.0 <40.0.4
- crates.io: `wasmtime` — affected >=41.0.0 <41.0.4

## Details
The affected versions of Wasmtime can panic if the host embedder drops the future returned by `wasmtime::component::[Typed]Func::call_async` before it resolves.

### Details

Starting with Wasmtime 39.0.0, the `component-model-async` feature became the default, which brought with it a new implementation of `[Typed]Func::call_async` which made it capable of calling async-typed guest export functions.  However, that implementation had a bug leading to a panic under certain circumstances:

1. The host embedding calls `[Typed]Func::call_async` on a function exported by a component, polling the returned `Future` once.
2. The component function yields control to the async runtime (e.g. Tokio), e.g. due to a call to host function registered using `LinkerInstance::func_wrap_async` which yields, or due an epoch interruption.
3. The host embedding drops the `Future` after polling it once.  This leaves the component instance in a non-reenterable state since the call never had a chance to complete.
4. The host embedding calls `[Typed]Func::call_async` again, polling the returned `Future`.  Since the component instance cannot be entered at this point, the call traps, but not before allocating a task and thread for the call.
5. The host embedding ignores the trap and drops the `Future`.  This panics due to the runtime attempting to dispose of the task created above, which panics since the thread has not yet exited.

### Impact
When a host embedder using the affected versions of Wasmtime calls `wasmtime::component::[Typed]Func::call_async` on a guest export and then drops the returned future without waiting for it to resolve, and then does so again with the same component instance, Wasmtime will panic. Embeddings that have the `component-model-async` compile-time feature disabled are unaffected.

### Patches
Wasmtime 40.0.4 and 41.0.4 have been patched to fix this issue. Versions 42.0.0 and later are not affected.

### Workarounds
If an embedding is not actually using any component-model-async features then disabling the `component-model-async` Cargo feature can work around this issue. This issue can also be worked around by either ensuring every `call_async` future is awaited until it completes or refraining from using the `Store` again after dropping a not-yet-resolved `call_async` future.

### Resources
This was first reported in https://bytecodealliance.zulipchat.com/#narrow/channel/206238-general/topic/Panic.20in.20Wasmtime.2041.2E0.2E3.20.28runtime.2Fconcurrent.2Fcomponent.29

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-xjhv-v822-pf94
- https://nvd.nist.gov/vuln/detail/CVE-2026-27195
- https://github.com/bytecodealliance/wasmtime/commit/9e51c0d9a240a9613d279c061f82286bd11383fd
- https://github.com/bytecodealliance/wasmtime/commit/d86b00736b9ece60b3c81e52f7a7e4cdd9f7d895
- https://bytecodealliance.zulipchat.com/#narrow/channel/206238-general/topic/.E2.9C.94.20Panic.20in.20Wasmtime.2041.2E0.2E3.20.28runtime.2Fconcurrent.2Fcomponent.29/with/574438798
- https://github.com/bytecodealliance/wasmtime
- https://github.com/bytecodealliance/wasmtime/releases/tag/v40.0.4
- https://github.com/bytecodealliance/wasmtime/releases/tag/v41.0.4
- https://rustsec.org/advisories/RUSTSEC-2026-0022.html
