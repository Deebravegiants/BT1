# [C] Wasmtime with Winch compiler backend on aarch64 may allow a sandbox-escaping memory access

## Summary
Severity: Critical
Advisory: GHSA-xx5w-cvp6-jv83
CVE: CVE-2026-34987
CWE: CWE-125, CWE-787
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-xx5w-cvp6-jv83
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=25.0.0 <36.0.7
- crates.io: `wasmtime` — affected >=37.0.0 <42.0.2
- crates.io: `wasmtime` — affected >=43.0.0 <43.0.1

## Details
### Impact

Wasmtime with its Winch (baseline) non-default compiler backend may allow properly constructed guest Wasm to access host memory outside of its linear-memory sandbox.

This vulnerability requires use of the Winch compiler (`-Ccompiler=winch`). By default, Wasmtime uses its Cranelift backend, not Winch. With Winch, the same incorrect assumption is present in theory on both aarch64 and x86-64. The aarch64 case has an observed-working proof of concept, while the x86-64 case is theoretical and may not be reachable in practice.

This Winch compiler bug can allow the Wasm guest to access memory before or after the linear-memory region, independently of whether pre- or post-guard regions are configured. The accessible range in the initial bug proof-of-concept is up to 32KiB before the start of memory, or ~4GiB after the start of memory, independently of the size of pre- or post-guard regions or the use of explicit or guard-region-based bounds checking. However, the underlying bug assumes a 32-bit memory offset stored in a 64-bit register has its upper bits cleared when it may not, and so closely related variants of the initial proof-of-concept may be able to access truly arbitrary memory in-process. This could result in a host process segmentation fault (DoS), an arbitrary data leak from the host process, or with a write, potentially an arbitrary RCE.

### Patches

Wasmtime 43.0.1, 42.0.2, and 36.0.7 have been released with fixes for this issue.

### Workaround

There are no workarounds within the Winch compiler backend while using the affected versions. Users of Wasmtime are encouraged either to upgrade to patched versions or, if that is not possible, use the Cranelift compiler backend.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-xx5w-cvp6-jv83
- https://nvd.nist.gov/vuln/detail/CVE-2026-34987
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2026-0095.html
