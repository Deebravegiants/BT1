# [H] RustCrypto Utilities cmov: `thumbv6m-none-eabi` compiler emits non-constant time assembly when using `cmovnz`

## Summary
Severity: High
Advisory: GHSA-2gqc-6j2q-83qp
CVE: CVE-2026-23519
CWE: CWE-203, CWE-208
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:H/AT:N/PR:N/UI:N/VC:H/VI:N/VA:N/SC:H/SI:N/SA:N (CVSS_V4)
Published: 2026-01-15
Source: https://github.com/advisories/GHSA-2gqc-6j2q-83qp
Type: github-advisory

## Affected
- crates.io: `cmov` — affected >=0 <0.4.4

## Details
### Summary

`thumbv6m-none-eabi` (Cortex M0, M0+ and M1) compiler emits non-constant time assembly when using `cmovnz` (portable version). I did not found any other target with the same behaviour but I did not go through all targets supported by Rust. 

### Details

It seems that, [during `mask` computation](https://github.com/RustCrypto/utils/blob/9e555db060c80f4669d804f448a524a37d201b32/cmov/src/portable.rs#L78), an LLVM optimisation pass is detecting that [`bitnz`](https://github.com/RustCrypto/utils/blob/9e555db060c80f4669d804f448a524a37d201b32/cmov/src/portable.rs#L13) is returning 0 or 1, that can be interpreted as a boolean. This intermediate value is not masked by a call to `black_box` and thus the subsequent [`.wrapping_sub(1)`](https://github.com/RustCrypto/utils/blob/9e555db060c80f4669d804f448a524a37d201b32/cmov/src/portable.rs#L78C1-L78C84) can be interpreted as a conditional bitwise conditional not.

### PoC

This is an attempt at having a minimal faulty code. In a library crate with an up-to-date `cmov` as only dependency, the content of `src/lib.rs` is:

```rust
#![no_std]
use cmov::Cmov;

#[inline(never)]
pub fn test_ct_cmov(a: &mut u8, b: u8, c: u8) {
    a.cmovnz(&b, c);
}
```


The resulting assembly emitted (shown using `cargo asm --release --target thumbv6m-none-eabi` that uses [`cargo-show-asm`](https://crates.io/crates/cargo-show-asm)):

<details>
<summary>Collapsed assembly</summary>

```asm
.section .text.not_ct::test_ct_cmov,"ax",%progbits
	.globl	not_ct::test_ct_cmov
	.p2align	1
	.type	not_ct::test_ct_cmov,%function
	.code	16
	.thumb_func
not_ct::test_ct_cmov:
	.fnstart
	.cfi_sections .debug_frame
	.cfi_startproc
	.save	{r7, lr}
	push {r7, lr}
	.cfi_def_cfa_offset 8
	.cfi_offset lr, -4
	.cfi_offset r7, -8
	.setfp	r7, sp
	add r7, sp, #0
	.cfi_def_cfa_register r7
	.pad	#8
	sub sp, #8
	movs r3, #0
	lsls r2, r2, #24
	bne .LBB0_2
	mvns r3, r3
.LBB0_2:
	ldrb r2, [r0]
	str r3, [sp, #4]
	str r3, [sp]
	mov r3, sp
	@APP
	@NO_APP
	ldr r3, [sp]
	bics r1, r3
	ands r2, r3
	adds r1, r2, r1
	strb r1, [r0]
	add sp, #8
	pop {r7, pc}
```

</details>

The non-constant time assembly is:

```asm
    bne  .LBB0_2
    mvns r3, r3
.LBB0_2:
```

### Impact

The exact impact is unclear, especially since `cmov` clearly warns users that the portable version is best-effort.

## References
- https://github.com/RustCrypto/utils/security/advisories/GHSA-2gqc-6j2q-83qp
- https://nvd.nist.gov/vuln/detail/CVE-2026-23519
- https://github.com/RustCrypto/utils/commit/55977257e7c82a309d5e8abfdd380a774f0f9778
- https://github.com/RustCrypto/utils
- https://rustsec.org/advisories/RUSTSEC-2026-0003.html
