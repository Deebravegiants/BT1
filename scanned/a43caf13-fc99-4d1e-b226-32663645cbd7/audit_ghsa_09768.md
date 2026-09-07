# [M] Wasmtime has improperly masked return value from `table.grow` with Winch compiler backend

## Summary
Severity: Medium
Advisory: GHSA-f984-pcp8-v2p7
CVE: CVE-2026-35186
CWE: CWE-789
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:P/PR:L/UI:N/VC:L/VI:L/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-04-10
Source: https://github.com/advisories/GHSA-f984-pcp8-v2p7
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=25.0.0 <36.0.7
- crates.io: `wasmtime` — affected >=37.0.0 <42.0.2
- crates.io: `wasmtime` — affected >=43.0.0 <43.0.1

## Details
### Impact

Wasmtime's Winch compiler backend contains a bug where translating the `table.grow` operator causes the result to be incorrectly typed. For 32-bit tables this means that the result of the operator, internally in Winch, is tagged as a 64-bit value instead of a 32-bit value. This invalid internal representation of Winch's compiler state compounds into further issues depending on how the value is consumed.

One example can be seen when the result of `table.grow` is used as the address of a load operation. The load operation is tricked into thinking the address is a 64-bit value, not a 32-bit value, which means that the final address to load from is calculated incorrectly. This can lead to a situation where the bytes before the start of linear memory can be loaded/stored to.

The primary consequence of this bug is that bytes in the host's address space can be stored/read from. This is only applicable to the 16 bytes before linear memory, however, as the only significant return value of `table.grow` that can be misinterpreted is -1. The bytes before linear memory are, by default, unmapped memory. Wasmtime will detect this fault and abort the process, however, because wasm should not be able to access these bytes.

Overall this this bug in Winch represents a DoS vector by crashing the host process, a correctness issue within Winch, and a possible leak of up to 16-bytes before linear memory. Wasmtime's default compiler is Cranelift, not Winch, and Wasmtime's default settings are to place guard pages before linear memory. This means that Wasmtime's default configuration is not affected by this issue, and when explicitly choosing Winch Wasmtime's otherwise default configuration leads to a DoS. Disabling guard pages before linear memory is required to possibly leak up to 16-bytes of host data.

### Patches

Wasmtime 43.0.1, 42.0.2, and 36.0.7 have been released with fixes for this issue.

### Workaround

There are no workarounds within the Winch compiler backend while using the affected versions. Users of Wasmtime are encouraged either to upgrade to patched versions or, if that is not possible, use the Cranelift compiler backend.

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-f984-pcp8-v2p7
- https://nvd.nist.gov/vuln/detail/CVE-2026-35186
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2026-0094.html
