# [M] Cmov/CmovEq on aarch64 can produce wrong results if high-bits of registers are set 

## Summary
Severity: Medium
Advisory: GHSA-3rjw-m598-pq24
CVE: CVE-2026-50185
CWE: CWE-758
Ecosystem: crates.io
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:L/VA:N/SC:N/SI:N/SA:N/E:P (CVSS_V4)
Published: 2026-07-02
Source: https://github.com/advisories/GHSA-3rjw-m598-pq24
Type: github-advisory

## Affected
- crates.io: `cmov` — affected >=0.1.1 <0.5.4

## Details
### Summary

The aarch64 implementations of `Cmov` and `CmovEq` seem to assume that the high bits when loading a value of size smaller than a register into a register are zero-extended. However, this is not the case and these bits are unspecified. This can result in a `left.cmovz(&right, condition)` not moving `right` into `left`, even if `condition == 0`. 

### Details

The Rust reference for inline assembly states that:
> If a value is of a smaller size than the register it is allocated in then the upper bits of that register will have an undefined value for inputs [..]. [Reference](https://doc.rust-lang.org/reference/inline-assembly.html#r-asm.register-operands.smaller-value)

If the high bits `[8..]` of the selector loaded into a register in the `Cmov` implementation or the high bits `[16..]` of `self` or `other` for CmovEq (specifically the implementation for `u16` and `i16`) are set, the inline asm compares will produce a different result than the Rust code expects based on the narrow types.

In other words, the following assert fails, even though `condition as u8` is zero:
```rust
let condition: u32 = black_box(1 << 8);
let mut left = 1;
let right = 2;
left.cmovz(&right, condition as u8);
assert_eq!(left, right);
```
Because the ninth bit is set in the original variable, this bit is also set when the truncated condition is loaded into the input register for the `cmp`, causing the `csel` to select the wrong value.

The problematic code is located in `cmov/src/backends/aarch64.rs` [here for Cmov](https://github.com/RustCrypto/utils/blob/dad5e3b9e66d929e86144fe7c8f25371892e35f3/cmov/src/backends/aarch64.rs#L4-L19) and [here for CmovEq](https://github.com/RustCrypto/utils/blob/dad5e3b9e66d929e86144fe7c8f25371892e35f3/cmov/src/backends/aarch64.rs#L60-L72).

The following function:
```rust
#[unsafe(no_mangle)]
pub fn cmovz_wrong_output(left: &mut i32, right: i32, condition: u32) {
    left.cmovz(&right, condition as u8);
}
```
produces the assembly:
```asm
cmovz_wrong_output:
	.cfi_startproc
	ldr w8, [x0]
	//APP
	cmp w2, #0
	csel w8, w1, w8, eq
	//NO_APP
	str w8, [x0]
	ret
```

which compares the 32-bits of the condition value against 0, instead of the intended 8.

Similarly, the following function using `cmoveq`
```rust
#[unsafe(no_mangle)]
pub fn cmoveq_wrong_output(left: u32, right: u32, input: u8, output: &mut u8) {
    (left as u16).cmoveq(&(right as u16), input, output);
}
```
compiles to:
```asm
cmoveq_wrong_output:
	.cfi_startproc
	ldrb w8, [x3]
	and w9, w2, #0xff
	//APP
	eor w10, w0, w1
	cmp w10, #0
	csel w8, w9, w8, eq
	//NO_APP
	strb w8, [x3]
	ret
```
where 32 bits of left and right are compared instead of 16. The same happens for `i16`.

For CmovEq, it seems the `u8/i8` impls are not affected, as they are calling `u16::from` in [the implementation](https://github.com/RustCrypto/utils/blob/dad5e3b9e66d929e86144fe7c8f25371892e35f3/cmov/src/lib.rs#L119) which causes the upper bits to be masked out.

### PoC

The following two test cases fail on `aarch64-unknown-linux-gnu` when compiled with `--release` (the cmovz one even in debug) emulated with qemu.

```
> rustc --version
rustc 1.94.0 (4a4ef493e 2026-03-02)
```

```rust
#[cfg(test)]
mod tests {
    use core::hint::black_box;

    use cmov::{Cmov, CmovEq};

    #[test]
    fn cmovz_wrong_output() {
        // The black box is necessary here, as otherwise the compiler will 
        // provide a constant 0 to the csel
        let condition: u32 = black_box(1 << 8);
        let mut left = 1;
        let right = 2;
        // I added this debug_assert as a sanity check, but funnily it causes
        // the wrong cmov behavior in debug as well (as opposed to only in release mode without the debug_assert)
        debug_assert_eq!(0, condition as u8);
        left.cmovz(&right, condition as u8);
        assert_eq!(left, right);
    }

    #[test]
    fn cmoveq_wrong_output() {
        let input = 1;
        let mut output = 0;
        let left: u32 = black_box(1 << 16);
        let right: u32 = black_box(1 << 17);
        // asserting in release mode here would hide the bug, the debug_assert_eq is
        // a sanity check that these values SHOULD be equal
        debug_assert_eq!(left as u16, right as u16);
        (left as u16).cmoveq(&(right as u16), input, &mut output);
        assert_eq!(input, output);
    }
}
```

### Impact

Under specific circumstances, this issue can cause `Cmov/CmovEq` to produce incorrect output on `aarch64`. However, whether this bug can actually manifest depends on the surrounding code that calls the relevant impls. In the PoC, a narrowing cast is required, which masks out the set bits from Rust's point of view, but which are then used in the inline assembly. 

### Additional Finding

PR [#1299](https://github.com/RustCrypto/utils/pull/1299) fixed a different bug in the aarch64 backend but introduced a small error. The `csel!` macro expect a `cmp` expression as its first argument which is never used. The compare is always `"cmp {0:w}, 0",` even for `csel64!`, which intends to use `cmp {0:x}, 0`. Given the bug described above, this oversight actually reduces its impact slightly, as only the bits in position`[8..32]` can cause issues,  even for those impls that use `csel64!`.

## References
- https://github.com/RustCrypto/utils/security/advisories/GHSA-3rjw-m598-pq24
- https://github.com/RustCrypto/utils
