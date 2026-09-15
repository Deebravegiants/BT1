# [M] Cranelift vulnerable to miscompilation of constant values in division on AArch64

## Summary
Severity: Medium
Advisory: GHSA-7f6x-jwh5-m9r4
CVE: CVE-2022-31169
CWE: CWE-682
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N (CVSS_V3)
Published: 2022-07-21
Source: https://github.com/advisories/GHSA-7f6x-jwh5-m9r4
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0 <0.38.2
- crates.io: `cranelift-codegen` — affected >=0 <0.85.2

## Details
### Impact

There was a bug in Wasmtime's code generator, Cranelift, for AArch64 targets where constant divisors could result in incorrect division results at runtime. The translation rules for constants did not take into account whether sign- or zero-extension should happen, which resulted in an incorrect value being placed into a register when a division was encountered. For example, a constant 32-bit unsigned divisor of `0xfffffffe` would be incorrectly sign-extended to 64-bits to `0xfffffffffffffffe`. Any kind of division of operands smaller than 64 bits is implemented with a 64-bit division instruction which would then result in an incorrect result because the divisor was larger than expected.

The impact of this bug is that programs executing within the WebAssembly sandbox would not behave according to the WebAssembly specification. This means that it is hypothetically possible for execution within the sandbox to go awry and WebAssembly programs could produce unexpected results. This should not impact hosts executing WebAssembly, but does affect the correctness of guest programs.

This bug was found with differential fuzzing of Wasmtime against other engines on the AArch64 platform. Fuzzing on AArch64 is not regularly performed at this time and the Wasmtime team is investigating how best to continuously fuzz AArch64 in the same manner as x86_64.

### Patches

This bug has been patched and users should upgrade to Wasmtime version 0.38.2.

### Workarounds

If upgrading is not an option at this time, direct users of Cranelift that control the exact Cranelift instructions being compiled can avoid the vulnerability by explicitly extending constant divisors to 64 bits using either the `sextend.i64` or the `uextend.i64` operation.

Note, though, that this issue only affects the AArch64 targets. Other platforms are not affected.

### For more information

If you have any questions or comments about this advisory:

* Reach out to us on [the Bytecode Alliance Zulip chat](https://bytecodealliance.zulipchat.com/#narrow/stream/217126-wasmtime)
* Open an issue in [the bytecodealliance/wasmtime repository](https://github.com/bytecodealliance/wasmtime/)

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-7f6x-jwh5-m9r4
- https://nvd.nist.gov/vuln/detail/CVE-2022-31169
- https://github.com/bytecodealliance/wasmtime/commit/2ba4bce5cc719e5a74e571a534424614e62ecc41
- https://github.com/bytecodealliance/wasmtime
- https://rustsec.org/advisories/RUSTSEC-2022-0101.html
