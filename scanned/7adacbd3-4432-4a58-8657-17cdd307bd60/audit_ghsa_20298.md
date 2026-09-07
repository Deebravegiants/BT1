# [M] Miscompilation of `i8x16.swizzle` and `select` with v128 inputs

## Summary
Severity: Medium
Advisory: GHSA-jqwc-c49r-4w2x
CVE: CVE-2022-31104
CWE: CWE-682
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:L/A:L (CVSS_V3)
Published: 2022-06-29
Source: https://github.com/advisories/GHSA-jqwc-c49r-4w2x
Type: github-advisory

## Affected
- crates.io: `wasmtime` — affected >=0 <0.38.1
- crates.io: `cranelift-codegen` — affected >=0 <0.85.1

## Details
### Impact

Wasmtime's implementation of the [SIMD proposal for WebAssembly](https://github.com/webassembly/simd) on x86_64 contained two distinct bugs in the instruction lowerings implemented in Cranelift. The aarch64 implementation of the simd proposal is not affected. The bugs were presented in the `i8x16.swizzle` and `select` WebAssembly instructions. The `select` instruction is only affected when the inputs are of `v128` type. The correspondingly affected Cranelift instructions were `swizzle` and `select`.

The `swizzle` instruction lowering in Cranelift erroneously overwrote the mask input register which could corrupt a constant value, for example. This means that future uses of the same constant may see a different value than the constant itself.

The `select` instruction lowering in Cranelift wasn't correctly implemented for vector types that are 128-bits wide. When the condition was 0 the wrong instruction was used to move the correct input to the output of the instruction meaning that only the low 32 bits were moved and the upper 96 bits of the result were left as whatever the register previously contained (instead of the input being moved from). The `select` instruction worked correctly if the condition was nonzero, however.

This bug in Wasmtime's implementation of these instructions on x86_64 represents an incorrect implementation of the specified semantics of these instructions according to the [WebAssembly specification](https://webassembly.github.io/spec/). The impact of this is benign for hosts running WebAssembly but represents possible vulnerabilities within the execution of a guest program. For example a WebAssembly program could take unintended branches or materialize incorrect values internally which runs the risk of exposing the program itself to other related vulnerabilities which can occur from miscompilations.

### Patches

We have released Wasmtime 0.38.1 and cranelift-codegen (and other associated cranelift crates) 0.85.1 which contain the corrected implementations of these two instructions in Cranelift.

### Workarounds

If upgrading is not an option for you at this time, you can avoid the vulnerability by [disabling the Wasm simd proposal](https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.wasm_simd)

```rust
config.wasm_simd(false);
```

Additionally the bug is only present on x86_64 hosts. Other aarch64 hosts are not affected. Note that s390x hosts don't yet implement the simd proposal and are not affected.

### References

* [The WebAssembly simd proposal](https://github.com/webassembly/simd)
* [Original test case showing the erroneous behavior](https://github.com/bytecodealliance/wasmtime/issues/4315)
* [Fix for the `swizzle` instruction](https://github.com/bytecodealliance/wasmtime/pull/4318)
* [Fix for the `select` instruction](https://github.com/bytecodealliance/wasmtime/pull/4317)

### For more information

If you have any questions or comments about this advisory:

* Reach out to us on [the Bytecode Alliance Zulip chat](https://bytecodealliance.zulipchat.com/#narrow/stream/217126-wasmtime)
* Open an issue in [the bytecodealliance/wasmtime repository](https://github.com/bytecodealliance/wasmtime/)

## References
- https://github.com/bytecodealliance/wasmtime/security/advisories/GHSA-jqwc-c49r-4w2x
- https://nvd.nist.gov/vuln/detail/CVE-2022-31104
- https://github.com/bytecodealliance/wasmtime/pull/4317
- https://github.com/bytecodealliance/wasmtime/pull/4318
- https://docs.rs/wasmtime/latest/wasmtime/struct.Config.html#method.wasm_simd
- https://github.com/bytecodealliance/wasmtime
- https://github.com/webassembly/simd
- https://rustsec.org/advisories/RUSTSEC-2022-0095.html
- https://webassembly.github.io/spec
