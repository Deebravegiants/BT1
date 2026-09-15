# [M] RustCrypto: Signatures has timing side-channel in ML-DSA decomposition

## Summary
Severity: Medium
Advisory: GHSA-hcp2-x6j4-29j7
CVE: CVE-2026-22705
CWE: CWE-1240
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:A/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:N (CVSS_V3)
Published: 2026-01-13
Source: https://github.com/advisories/GHSA-hcp2-x6j4-29j7
Type: github-advisory

## Affected
- crates.io: `ml-dsa` — affected >=0 <0.1.0-rc.3

## Details
### Summary

A timing side-channel was discovered in the Decompose algorithm which is used during ML-DSA signing to generate hints for the signature.

### Details

The analysis was performed using a constant-time analyzer that examines compiled assembly code for instructions with data-dependent timing behavior. The analyzer flags:

- **UDIV/SDIV instructions**: Hardware division instructions have early termination optimizations where execution time depends on operand values.

The `decompose` function used a hardware division instruction to compute `r1.0 / TwoGamma2::U32`. This function is called during signing through `high_bits()` and `low_bits()`, which process values derived from secret key components:

- `(&w - &cs2).low_bits()` where `cs2` is derived from secret key component `s2`
- `Hint::new()` calls `high_bits()` on values derived from secret key component `t0`

**Original Code**:
```rust
fn decompose<TwoGamma2: Unsigned>(self) -> (Elem, Elem) {
    // ...
    let mut r1 = r_plus - r0;
    r1.0 /= TwoGamma2::U32;  // Variable-time division on secret-derived data
    (r1, r0)
}
```

### PoC

I do not have an exploit written for this, currently.

### Impact

The dividend (`r1.0`) is derived from secret key material. An attacker with precise timing measurements could extract information about the signing key by observing timing variations in the division operation.

### Mitigation

Replacing division with constant-time Barrett reduction mitigates this risk. Since `TwoGamma2` is a compile-time constant, we precompute the multiplicative inverse:

```patch
diff --git a/ml-dsa/src/algebra.rs b/ml-dsa/src/algebra.rs
index 559b68a..bb126ce 100644
--- a/ml-dsa/src/algebra.rs
+++ b/ml-dsa/src/algebra.rs
@@ -54,8 +54,50 @@ pub(crate) trait Decompose {
     fn decompose<TwoGamma2: Unsigned>(self) -> (Elem, Elem);
 }
 
+/// Constant-time division by a compile-time constant divisor.
+///
+/// This trait provides a constant-time alternative to the hardware division
+/// instruction, which has variable timing based on operand values.
+/// Uses Barrett reduction to compute `x / M` where M is a compile-time constant.
+pub(crate) trait ConstantTimeDiv: Unsigned {
+    /// Bit shift for Barrett reduction, chosen to provide sufficient precision
+    const CT_DIV_SHIFT: usize;
+    /// Precomputed multiplier: ceil(2^SHIFT / M)
+    const CT_DIV_MULTIPLIER: u64;
+
+    /// Perform constant-time division of x by Self::U32
+    /// Requires: x < Q (the field modulus, ~2^23)
+    #[inline(always)]
+    fn ct_div(x: u32) -> u32 {
+        // Barrett reduction: q = (x * MULTIPLIER) >> SHIFT
+        // This gives us floor(x / M) for x < 2^SHIFT / MULTIPLIER * M
+        let x64 = u64::from(x);
+        let quotient = (x64 * Self::CT_DIV_MULTIPLIER) >> Self::CT_DIV_SHIFT;
+        quotient as u32
+    }
+}
+
+impl<M> ConstantTimeDiv for M
+where
+    M: Unsigned,
+{
+    // Use a shift that provides enough precision for the ML-DSA field (Q ~ 2^23)
+    // We need SHIFT > log2(Q) + log2(M) to ensure accuracy
+    // With Q < 2^24 and M < 2^20, SHIFT = 48 is sufficient
+    const CT_DIV_SHIFT: usize = 48;
+
+    // Precompute the multiplier at compile time
+    // We add (M-1) before dividing to get ceiling division, ensuring we never underestimate
+    #[allow(clippy::integer_division_remainder_used)]
+    const CT_DIV_MULTIPLIER: u64 = ((1u64 << Self::CT_DIV_SHIFT) + M::U64 - 1) / M::U64;
+}
+
 impl Decompose for Elem {
     // Algorithm 36 Decompose
+    //
+    // This implementation uses constant-time division to avoid timing side-channels.
+    // The original algorithm used hardware division which has variable timing based
+    // on operand values, potentially leaking secret information during signing.
     fn decompose<TwoGamma2: Unsigned>(self) -> (Elem, Elem) {
         let r_plus = self.clone();
         let r0 = r_plus.mod_plus_minus::<TwoGamma2>();
@@ -63,8 +105,9 @@ impl Decompose for Elem {
         if r_plus - r0 == Elem::new(BaseField::Q - 1) {
             (Elem::new(0), r0 - Elem::new(1))
         } else {
-            let mut r1 = r_plus - r0;
-            r1.0 /= TwoGamma2::U32;
+            let diff = r_plus - r0;
+            // Use constant-time division instead of hardware division
+            let r1 = Elem::new(TwoGamma2::ct_div(diff.0));
             (r1, r0)
         }
     }
```

See our blog post on [how we avoided side-channels in our Go implementation of ML-DSA](https://blog.trailofbits.com/2025/11/14/how-we-avoided-side-channels-in-our-new-post-quantum-go-cryptography-libraries/) for more information.

## References
- https://github.com/RustCrypto/signatures/security/advisories/GHSA-hcp2-x6j4-29j7
- https://nvd.nist.gov/vuln/detail/CVE-2026-22705
- https://github.com/RustCrypto/signatures/pull/1144
- https://github.com/RustCrypto/signatures/commit/035d9eef98486ecd00a8bf418c7817eb14dd6558
- https://github.com/RustCrypto/signatures
- https://rustsec.org/advisories/RUSTSEC-2025-0144.html
