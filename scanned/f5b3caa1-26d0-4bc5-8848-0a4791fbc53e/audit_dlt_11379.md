# [?] field: expand packed-extension API; fix unsound PackedValue impls (#1620)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-05-10
Source: https://github.com/Plonky3/Plonky3/commit/c092c1f491f6032394d37b67824f6e9eaffff6fb
Type: security-commit

## Details
field: expand packed-extension API; fix unsound PackedValue impls (#1620)

* bench(field): add packed extension Div benchmarks

Adds two pieces:

1. Generic helpers `benchmark_div_latency` / `benchmark_div_throughput` in
   field-testing's `bench_func`, mirroring the existing add/mul/sub patterns.

2. Macro `bench_packed_extension_field!` that wires up packed-extension
   benchmarks (add, mul, div × latency, throughput) for one or more
   `(label, ScalarEF)` pairs. Per-field bench files become a one-shot macro
   invocation, matching the convention `test_packed_extension_field!`
   already uses for the test side.

Per-field bench file `baby-bear/benches/packed_extension.rs` invokes the
macro for `BinomialExtensionField<BabyBear, D>` at D ∈ {4, 5, 8}.

Used to verify the wrapper-based Div is no slower than origin/main's
hand-rolled in-place Montgomery (in fact -3 to -6% on BabyBear binomial,
see fix(field) commit).

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* feat(field): expand PackedFieldExtension API

Adds default methods filling out the symmetry gap with PackedValue:
  - from_ext_fn(impl Fn(usize) -> ExtField) -> Self  (canonical primitive)
  - pack_ext_columns<N> / pack_ext_columns_fn<N>
  - unpack_ext_into<N> / unpack_ext_iter<N>
  - to_ext_slice(&self, &mut [ExtField])

`from_ext_slice` changes from required to a default delegating to `from_ext_fn`.
Existing impls override `from_ext_fn` for the layout-aware fast path; the slice
form falls through. This is purely additive: external impls overriding
`from_ext_slice` continue to work, and `from_ext_fn` is new functionality.

Migrates the binomial/cubic/quintic concrete impls to override `from_ext_fn`
instead of `from_ext_slice` (one primitive, all column/iter methods inherit
the layout-aware fast path through it). Adds the `F: Field` blanket impl
override for the trivial extension case.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* fix(field)!: remove unsound PackedValue/PackedField from cubic/quintic; consolidate Div via shared wrapper

The cubic and quintic packed-extension types implemented PackedValue with
`from_slice` / `as_slice` / `from_slice_mut` / `as_slice_mut` defined as
pointer casts:

    fn from_slice(slice: &[Self::Value]) -> &Self {
        assert_eq!(slice.len(), Self::WIDTH);
        unsafe { &*slice.as_ptr().cast() }
    }

The cast claims `[ExtField; W]` and `[PF; D]` have the same layout. They have
the same total byte size, but the byte order does not match:

  &[ExtField; W]   is lane-major:    [a0,b0,c0, a1,b1,c1, …, a_{W-1},b_{W-1},c_{W-1}]
  &PackedExt       is basis-major:   [a0,…,a_{W-1}, b0,…,b_{W-1}, c0,…,c_{W-1}]

For W = 1 these coincide; for any W > 1 the cast permutes which F values
represent which (basis_coefficient, lane) pair. This is a latent soundness
bug — the unsafe block asserts a layout invariant that doesn't hold,
producing semantically wrong values once any PackedField op runs through it.
Workspace search confirms zero callers exercise the trait, so the bug
never fired.

Aligns cubic/quintic with the binomial design (which intentionally never
claimed PackedValue). The PackedFieldExtension API already provides the
sound bridge between scalar EF and packed-extension types.

Adds `invert_packed_extension<F, EF>(EF::ExtensionPacking) -> EF::ExtensionPacking`
in `batch_inverse.rs`, a shared wrapper for per-lane Montgomery inversion.
Dispatches `F::Packing::WIDTH ∈ {1, 2, 4, 8, 16}` to a const-generic body
that materializes lanes into a `[EF; W]` stack array via
`PackedFieldExtension::extract`, runs `batch_multiplicative_inverse_general`,
and rebuilds via `PackedFieldExtension::from_ext_fn`. Allocation-free; LLVM
folds the match to the single live arm post-monomorphization.

Consolidates `Div` across all three packed extensions (binomial, cubic,
quintic) to delegate via the wrapper. Tightens `Div` / `DivAssign` from
`<F, PF: PackedField<Scalar=F>>` to `<F, F::Packing>` — no caller exercises
non-default PF, and the wrapper requires `PackedFieldExtension` which is
only impl'd for `F::Packing`.

Measured perf (BabyBear binomial extension, Apple M2 Pro, aarch64 NEON
with target-cpu=native, F::Packing::WIDTH = 4; criterion baseline =
4317afc6, the bench-harness commit on this branch.
The intermediate commit 5ddc7807 expands the PackedFieldExtension API
but does not touch any Div code path, so the delta is attributable to
this commit's Div consolidation):

    D=4 div-throughput:  405 µs → 391 µs   (-3.3%)
    D=4 div-latency:     409 µs → 389 µs   (-5.5%)
    D=5 div-throughput:  468 µs → 457 µs   (-2.5%)
    D=5 div-latency:     469 µs → 457 µs   (-2.2%)
    D=8 div-throughput:  637 µs → 601 µs   (-5.5%)
    D=8 div-latency:     738 µs → 605 µs   (-12.9%; D=8-latency baseline
                         had 14 outliers / 11 high-severe, so 95% CI is
                         wide: -17.2..-8.9%. Improvement is real but
                         magnitude is uncertain)

The wrapper is faster than the prior in-place Montgomery despite doing more
total memory ops, because the materialize-then-sequential pattern is more
cache/prefetch-friendly than the basis-major scattered indexing the in-place
form requires. See bench(field) commit on this branch for the harness.

BREAKING: removes the `unsafe impl PackedValue` and `unsafe impl PackedField`
on PackedCubicTrinomialExtensionField and PackedQuinticTrinomialExtensionField.
Tightens Div / DivAssign for all three packed extensions to PF = F::Packing.
No callers in this workspace.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

* feat(field): add ExtensionField::from_ext_basis_coefficients

Adds a method to ExtensionField:
  fn from_ext_basis_coefficients(coeffs: &[Self]) -> Option<Self>

Reassembles a Self element from D = DIMENSION coefficients in Self via
Σⱼ basisⱼ · coeffsⱼ. Returns None on length mismatch, matching the
existing BasedVectorSpace::from_basis_coefficients_slice convention.

This is the Self-coefficient counterpart to from_basis_coefficients_slice
(which takes coefficients in Base) — the natural "lifting" operation in
commit-and-open protocols where an EF polynomial decomposes as
f(X) = Σⱼ basisⱼ · fⱼ(X) with fⱼ over Base, so f(z) = Σⱼ basisⱼ · fⱼ(z)
for any z ∈ Self.

Migrates the two hand-rolled call sites:
  - uni-stark/src/verifier.rs::zps_dot_quotient_chunks
  - batch-stark/src/verifier/mod.rs::recompose

After this commit there are no `ith_basis_element` callers in the workspace
outside the field crate itself.

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### baby-bear/Cargo.toml
```diff
@@ -40,5 +40,9 @@ harness = false
 name = "extension"
 harness = false
 
+[[bench]]
+name = "packed_extension"
+harness = false
+
 [lints]
 workspace = true
```

### baby-bear/benches/packed_extension.rs
```diff
@@ -0,0 +1,10 @@
+use p3_baby_bear::BabyBear;
+use p3_field::extension::BinomialExtensionField;
+use p3_field_testing::bench_packed_extension_field;
+
+bench_packed_extension_field! {
+    BabyBear,
+    quartic = BinomialExtensionField<BabyBear, 4>,
+    quintic = BinomialExtensionField<BabyBear, 5>,
+    octic = BinomialExtensionField<BabyBear, 8>,
+}
```

### batch-stark/src/verifier/mod.rs
```diff
@@ -9,7 +9,7 @@ use hashbrown::HashMap;
 use p3_air::Air;
 use p3_air::symbolic::{AirLayout, SymbolicExpressionExt};
 use p3_commit::{Pcs, PolynomialSpace};
-use p3_field::{Algebra, BasedVectorSpace, PrimeCharacteristicRing};
+use p3_field::{Algebra, BasedVectorSpace, ExtensionField, PrimeCharacteristicRing};
 use p3_lookup::folder::VerifierConstraintFolderWithLookups;
 use p3_lookup::logup::LogUpGadget;
 use p3_lookup::{InteractionSymbolicBuilder, Kind, LookupProtocol};
@@ -540,20 +540,13 @@ where
             if aux_width == 0 {
                 return vec![];
             }
-            // Chunk the flattened coefficients into groups of size `dim`.
-            // Each chunk represents the coefficients of one extension field element.
+            // Each `ext_degree`-chunk holds the basis coefficients (in EF) of one EF element.
+            // chunks_exact yields chunks of exactly `ext_degree` = DIMENSION, so the unwrap
+            // below cannot panic.
             flat.chunks_exact(ext_degree)
-                .map(|coeffs| {
-                    // Dot product: sum(coeff_j * basis_j)
-                    coeffs
-                        .iter()
-                        .enumerate()
-                        .map(|(j, &coeff)| {
-                            coeff
-                                * Challenge::<SC>::ith_basis_element(j)
-                                    .expect("Basis element should exist")
-                        })
-                        .sum()
+                .map(|chunk| {
+                    Challenge::<SC>::from_ext_basis_coefficients(chunk)
+                        .expect("chunk length matches DIMENSION by construction")
                 })
                 .collect()
         };
```

### field-testing/src/bench_func.rs
```diff
@@ -1,6 +1,7 @@
 use alloc::format;
 use alloc::vec::Vec;
 use core::hint::black_box;
+use core::ops::Div;
 
 use criterion::{BatchSize, Criterion};
 use p3_field::{Algebra, Field, PrimeCharacteristicRing, chunked_linear_combination};
@@ -399,6 +400,77 @@ pub fn benchmark_mul_throughput<R: PrimeCharacteristicRing + Copy, const N: usiz
     });
 }
 
+pub fn benchmark_div_latency<R: PrimeCharacteristicRing + Copy + Div<Output = R>, const N: usize>(
+    c: &mut Criterion,
+    name: &str,
+) where
+    StandardUniform: Distribution<R>,
+{
+    c.bench_function(&format!("div-latency/{N} {name}"), |b| {
+        b.iter_batched(
+            || {
+                let mut rng = SmallRng::seed_from_u64(1);
+                let init = rng.random::<R>();
+                let mut vec = Vec::with_capacity(N);
+                for _ in 0..N {
+                    vec.push(rng.random::<R>());
+                }
+                (init, vec)
+            },
+            |(init, vec)| vec.iter().fold(init, |x, y| x / *y),
+            BatchSize::SmallInput,
+        );
+    });
+}
+
+pub fn benchmark_div_throughput<
+    R: PrimeCharacteristicRing + Copy + Div<Output = R>,
+    const N: usize,
+>(
+    c: &mut Criterion,
+    name: &str,
+) where
+    StandardUniform: Distribution<R>,
+{
+    c.bench_function(&format!("div-throughput/{N} {name}"), |b| {
+        b.iter_batched(
+            || {
+                let mut rng = SmallRng::seed_from_u64(1);
+                (
+                    rng.random::<R>(),
+                    rng.random::<R>(),
+                    rng.random::<R>(),
+                    rng.random::<R>(),
+                    rng.random::<R>(),
+                    rng.random::<R>(),
+                    rng.random::<R>(),
+                    rng.random::<R>(),
+                    rng.random::<R>(),
+                    rng.random::<R>(),
+                )
+            },
+            |(mut a, mut b, mut c, mut d, mut e, mut f, mut g, mut h, mut i, mut j)| {
+                for _ in 0..N {
+                    (a, b, c, d, e, f, g, h, i, j) = (
+                        a / b,
+                        b / c,
+                        c / d,
+                        d / e,
+                        e / f,
+                        f / g,
+                        g / h,
+                        h / i,
+                        i / j,
+                        j / a,
+                    );
+                }
+                (a, b, c, d, e, f, g, h, i, j)
+            },
+            BatchSize::SmallInput,
+        );
+    });
+}
+
 pub fn benchmark_base_mul_latency<F: Field, A: Algebra<F> + Copy, const N: usize>(
     c: &mut Criterion,
     name: &str,
@@ -664,3 +736,49 @@ pub fn benchmark_chunked_linear_combination<F: Field, A: Algebra<F> + Copy, cons
     }
     bench_chunk!(1, 2, 4, 8, 16, 32, 64);
 }
+
+/// Wire up packed-extension benchmarks for one or more `(label, ScalarEF)` pairs.
+///
+/// For each pair, generates a Criterion benchmark function that exercises
+/// add/mul/div latency and throughput on `<ScalarEF as ExtensionField<Base>>::ExtensionPacking`.
+/// Emits `criterion_group!` and `criterion_main!` at the call site, so this should be
+/// invoked from a `benches/*.rs` file as the file's top-level content.
+///
+/// # Example
+///
+/// ```ignore
+/// use p3_baby_bear::BabyBear;
+/// use p3_field::extension::BinomialExtensionField;
+/// use p3_field_testing::bench_packed_extension_field;
+///
+/// bench_packed_extension_field! {
+///     BabyBear,
+///     quartic = BinomialExtensionField<BabyBear, 4>,
+///     quintic = BinomialExtensionField<BabyBear, 5>,
+///     octic = BinomialExtensionField<BabyBear, 8>,
+/// }
+/// ```
+#[macro_export]
+macro_rules! bench_packed_extension_field {
+    ($base:ty, $($label:ident = $ef:ty),+ $(,)?) => {
+        // Each round of throughput has 10 operations; run latency tests with 10× reps.
+        const REPS: usize = 100;
+        const L_REPS: usize = 10 * REPS;
+
+        $(
+            fn $label(c: &mut criterion::Criterion) {
+                type Packed = <$ef as p3_field::ExtensionField<$base>>::ExtensionPacking;
+                let name = stringify!($ef);
+                $crate::bench_func::benchmark_add_throughput::<Packed, REPS>(c, name);
+                $crate::bench_func::benchmark_add_latency::<Packed, L_REPS>(c, name);
+                $crate::bench_func::benchmark_mul_throughput::<Packed, REPS>(c, name);
+                $crate::bench_func::benchmark_mul_latency::<Packed, L_REPS>(c, name);
+                $crate::bench_func::benchmark_div_throughput::<Packed, REPS>(c, name);
+                $crate::bench_func::benchmark_div_latency::<Packed, L_REPS>(c, name);
+            }
+        )+
+
+        criterion::criterion_group!(packed_ext_benches, $($label),+);
+        criterion::criterion_main!(packed_ext_benches);
+    };
+}
```

### field/src/batch_inverse.rs
```diff
@@ -4,7 +4,9 @@ use p3_maybe_rayon::prelude::*;
 use tracing::instrument;
 
 use crate::field::Field;
-use crate::{FieldArray, PackedValue, PrimeCharacteristicRing};
+use crate::{
+    ExtensionField, FieldArray, PackedFieldExtension, PackedValue, PrimeCharacteristicRing,
+};
 
 /// Compute the multiplicative inverse of every element in a slice via Montgomery's trick.
 ///
@@ -100,3 +102,43 @@ where
         inv *= x[i];
     }
 }
+
+/// Per-lane inverse of a packed extension via Montgomery's trick. Allocation-free.
+///
+/// Dispatches on `F::Packing::WIDTH` to a const-generic body that materializes the `W`
+/// lanes via [`PackedFieldExtension::extract`], runs [`batch_multiplicative_inverse_general`]
+/// over a stack-sized `[EF; W]` buffer, and rebuilds the packed extension via
+/// [`PackedFieldExtension::from_ext_fn`]. After monomorphization the match folds to
+/// the single live arm.
+///
+/// All `PackedField` backends in this workspace use `WIDTH ∈ {1, 2, 4, 8, 16}`; the
+/// fallback arm panics if a future backend introduces a different width.
+#[inline]
+pub fn invert_packed_extension<F, EF>(packed: EF::ExtensionPacking) -> EF::ExtensionPacking
+where
+    F: Field,
+    EF: ExtensionField<F>,
+{
+    match F::Packing::WIDTH {
+        1 => invert_packed_extension_const::<F, EF, 1>(packed),
+        2 => invert_packed_extension_const::<F, EF, 2>(packed),
+        4 => invert_packed_extension_const::<F, EF, 4>(packed),
+        8 => invert_packed_extension_const::<F, EF, 8>(packed),
+        16 => invert_packed_extension_const::<F, EF, 16>(packed),
+        w => panic!("unsupported PackedField WIDTH = {w}"),
+    }
+}
+
+#[inline]
+fn invert_packed_extension_const<F, EF, const W: usize>(
+    packed: EF::ExtensionPacking,
+) -> EF::ExtensionPacking
+where
+    F: Field,
+    EF: ExtensionField<F>,
+{
+    let lanes: [EF; W] = core::array::from_fn(|i| packed.extract(i));
+    let mut invs = [EF::ZERO; W];
+    batch_multiplicative_inverse_general(&lanes, &mut invs, |x| x.inverse());
+    EF::ExtensionPacking::from_ext_fn(|i| invs[i])
+}
```

### field/src/extension/packed_binomial_extension.rs
```diff
@@ -223,11 +223,8 @@ where
     F: BinomiallyExtendable<D>,
 {
     #[inline]
-    fn from_ext_slice(ext_slice: &[BinomialExtensionField<F, D>]) -> Self {
-        let width = F::Packing::WIDTH;
-        assert_eq!(ext_slice.len(), width);
-
-        Self::new(F::Packing::pack_columns_fn(|lane| ext_slice[lane].value))
+    fn from_ext_fn(f: impl Fn(usize) -> BinomialExtensionField<F, D>) -> Self {
+        Self::new(F::Packing::pack_columns_fn(|lane| f(lane).value))
     }
 
     #[inline]
@@ -560,103 +557,20 @@ where
     }
 }
 
-impl<F, PF, const D: usize> Div for PackedBinomialExtensionField<F, PF, D>
-where
-    F: BinomiallyExtendable<D>,
-    PF: PackedField<Scalar = F>,
+impl<F: BinomiallyExtendable<D>, const D: usize> Div
+    for PackedBinomialExtensionField<F, F::Packing, D>
 {
     type Output = Self;
 
     #[allow(clippy::suspicious_arithmetic_impl)]
     #[inline]
     fn div(self, rhs: Self) -> Self {
-        // This buffer will hold prefix products during the forward pass,
-        // then the final per-lane inverses after the backward pass.
-        let mut rhs_inv = Self::default();
-
-        if PF::WIDTH > 0 {
-            // Forward pass: build cumulative prefix products.
-            //
-            // After this loop:
-            //   rhs_inv[0] = 1
-            //   rhs_inv[1] = rhs[0]
-            //   rhs_inv[2] = rhs[0] * rhs[1]
-            //   ...
-            //   rhs_inv[k] = rhs[0] * rhs[1] * ... * rhs[k-1]
-
-            // Seed the first lane with the multiplicative identity.
-            let one = BinomialExtensionField::<F, D>::ONE;
-            for i in 0..D {
-                rhs_inv.value[i].as_slice_mut()[0] = one.value[i];
-            }
-
-            for lane in 1..PF::WIDTH {
-                // Extract the prefix product accumulated so far (from the previous lane).
-                let prev_prefix = BinomialExtensionField::<F, D>::new(array::from_fn(|i| {
-                    rhs_inv.value[i].as_slice()[lane - 1]
-                }));
-                // Extract the divisor element at the previous lane.
-                let rhs_prev = BinomialExtensionField::<F, D>::new(array::from_fn(|i| {
-                    rhs.value[i].as_slice()[lane - 1]
-                }));
-                // Extend the running product: prefix[lane] = prefix[lane-1] * rhs[lane-1].
-                let prefix = prev_prefix * rhs_prev;
-                // Store the new prefix product back into the buffer at this lane.
-                for i in 0..D {
-                    rhs_inv.value[i].as_slice_mut()[lane] = prefix.value[i];
-                }
-            }
-
-            // Single inversion: compute the inverse of the full product across all lanes:
-            // (rhs[0] * rhs[1] * ... * rhs[N-1])^{-1}.
-            let prefix_last = BinomialExtensionField::<F, D>::new(array::from_fn(|i| {
-                rhs_inv.value[i].as_slice()[PF::WIDTH - 1]
-            }));
-            let rhs_last = BinomialExtensionField::<F, D>::new(array::from_fn(|i| {
-                rhs.value[i].as_slice()[PF::WIDTH - 1]
-            }));
-            let mut suffix_inv = (prefix_last * rhs_last).inverse();
-
-            // Backward pass: recover individual inverses.
-            //
-            // Invariant at the start of each iteration:
-            //   suffix_inv = (rhs[lane] * rhs[lane+1] * ... * rhs[N-1])^{-1}
-            //
-            // So: rhs[lane]^{-1} = prefix[lane] * suffix_inv
-            //     because prefix[lane] * suffix_inv
-            //           = (rhs[0] * ... * rhs[lane-1]) * (rhs[lane] * ... * rhs[N-1])^{-1}
-            //           ... and the rhs[0] * ... * rhs[lane-1] terms cancel with the
-            //           corresponding factors in the denominator, leaving rhs[lane]^{-1}.
-            for lane in (0..PF::WIDTH).rev() {
-                // Read the prefix product stored during the forward pass.
-                let prefix = BinomialExtensionField::<F, D>::new(array::from_fn(|i| {
-                    rhs_inv.value[i].as_slice()[lane]
-                }));
-                // Combine prefix and suffix inverse to get rhs[lane]^{-1}.
-                let inv_lane = prefix * suffix_inv;
-                // Write the computed inverse back into the buffer.
-                for i in 0..D {
-                    rhs_inv.value[i].as_slice_mut()[lane] = inv_lane.value[i];
-                }
-
-                // Update the running suffix inverse by absorbing rhs[lane].
-                // This peels off rhs[lane] from the suffix for the next iteration.
-                let rhs_lane = BinomialExtensionField::<F, D>::new(array::from_fn(|i| {
-                    rhs.value[i].as_slice()[lane]
-                }));
-                suffix_inv *= rhs_lane;
-            }
-        }
-
-        // Final multiplication: numerator * (1 / denominator) per lane.
-        self * rhs_inv
+        self * crate::invert_packed_extension::<F, BinomialExtensionField<F, D>>(rhs)
     }
 }
 
-impl<F, PF, const D: usize> DivAssign for PackedBinomialExtensionField<F, PF, D>
-where
-    F: BinomiallyExtendable<D>,
-    PF: PackedField<Scalar = F>,
+impl<F: BinomiallyExtendable<D>, const D: usize> DivAssign
+    for PackedBinomialExtensionField<F, F::Packing, D>
 {
     #[inline]
     fn div_assign(&mut self, rhs: Self) {
```

### field/src/extension/packed_cubic_extension.rs
```diff
@@ -191,73 +191,12 @@ where
     }
 }
 
-// SAFETY: Memory layout is compatible with `[CubicTrinomialExtensionField<F>; WIDTH]`.
-unsafe impl<F, PF> PackedValue for PackedCubicTrinomialExtensionField<F, PF>
-where
-    F: CubicTrinomialExtendable,
-    PF: PackedField<Scalar = F>,
-{
-    type Value = CubicTrinomialExtensionField<F>;
-
-    const WIDTH: usize = PF::WIDTH;
-
-    #[inline]
-    fn from_slice(slice: &[Self::Value]) -> &Self {
-        assert_eq!(slice.len(), Self::WIDTH);
-        unsafe { &*slice.as_ptr().cast() }
-    }
-
-    #[inline]
-    fn from_slice_mut(slice: &mut [Self::Value]) -> &mut Self {
-        assert_eq!(slice.len(), Self::WIDTH);
-        unsafe { &mut *slice.as_mut_ptr().cast() }
-    }
-
-    #[inline]
-    fn from_fn<Fn: FnMut(usize) -> Self::Value>(mut f: Fn) -> Self {
-        let mut result = Self::default();
-        for i in 0..Self::WIDTH {
-            let val = f(i);
-            for j in 0..3 {
-                result.value[j].as_slice_mut()[i] = val.value[j];
-            }
-        }
-        result
-    }
-
-    #[inline]
-    fn as_slice(&self) -> &[Self::Value] {
-        unsafe {
-            core::slice::from_raw_parts(self as *const Self as *const Self::Value, Self::WIDTH)
-        }
-    }
-
-    #[inline]
-    fn as_slice_mut(&mut self) -> &mut [Self::Value] {
-        unsafe {
-            core::slice::from_raw_parts_mut(self as *mut Self as *mut Self::Value, Self::WIDTH)
-        }
-    }
-}
-
-// SAFETY: Implements all required trait bounds.
-unsafe impl<F, PF> PackedField for PackedCubicTrinomialExtensionField<F, PF>
-where
-    F: CubicTrinomialExtendable,
-    PF: PackedField<Scalar = F>,
-{
-    type Scalar = CubicTrinomialExtensionField<F>;
-}
-
 impl<F: CubicTrinomialExtendable> PackedFieldExtension<F, CubicTrinomialExtensionField<F>>
     for PackedCubicTrinomialExtensionField<F, F::Packing>
 {
     #[inline]
-    fn from_ext_slice(ext_slice: &[CubicTrinomialExtensionField<F>]) -> Self {
-        let width = F::Packing::WIDTH;
-        assert_eq!(ext_slice.len(), width);
-
-        Self::new(F::Packing::pack_columns_fn(|lane| ext_slice[lane].value))
+    fn from_ext_fn(f: impl Fn(usize) -> CubicTrinomialExtensionField<F>) -> Self {
+        Self::new(F::Packing::pack_columns_fn(|lane| f(lane).value))
     }
 
     #[inline]
@@ -589,26 +528,17 @@ where
     }
 }
 
-impl<F, PF> Div for PackedCubicTrinomialExtensionField<F, PF>
-where
-    F: CubicTrinomialExtendable,
-    PF: PackedField<Scalar = F>,
-{
+impl<F: CubicTrinomialExtendable> Div for PackedCubicTrinomialExtensionField<F, F::Packing> {
     type Output = Self;
 
     #[allow(clippy::suspicious_arithmetic_impl)]
     #[inline]
     fn div(self, rhs: Self) -> Self {
-        let rhs_inv = Self::from_fn(|i| rhs.as_slice()[i].inverse());
-        self * rhs_inv
+        self * crate::invert_packed_extension::<F, CubicTrinomialExtensionField<F>>(rhs)
     }
 }
 
-impl<F, PF> DivAssign for PackedCubicTrinomialExtensionField<F, PF>
-where
-    F: CubicTrinomialExtendable,
-    PF: PackedField<Scalar = F>,
-{
+impl<F: CubicTrinomialExtendable> DivAssign for PackedCubicTrinomialExtensionField<F, F::Packing> {
     #[inline]
     fn div_assign(&mut self, rhs: Self) {
         *self = *self / rhs;
```

### field/src/extension/packed_quintic_extension.rs
```diff
@@ -195,73 +195,12 @@ where
     }
 }
 
-// SAFETY: Memory layout is compatible with `[QuinticTrinomialExtensionField<F>; WIDTH]`.
-unsafe impl<F, PF> PackedValue for PackedQuinticTrinomialExtensionField<F, PF>
-where
-    F: QuinticTrinomialExtendable,
-    PF: PackedField<Scalar = F>,
-{
-    type Value = QuinticTrinomialExtensionField<F>;
-
-    const WIDTH: usize = PF::WIDTH;
-
-    #[inline]
-    fn from_slice(slice: &[Self::Value]) -> &Self {
-        assert_eq!(slice.len(), Self::WIDTH);
-        unsafe { &*slice.as_ptr().cast() }
-    }
-
-    #[inline]
-    fn from_slice_mut(slice: &mut [Self::Value]) -> &mut Self {
-        assert_eq!(slice.len(), Self::WIDTH);
-        unsafe { &mut *slice.as_mut_ptr().cast() }
-    }
-
-    #[inline]
-    fn from_fn<Fn: FnMut(usize) -> Self::Value>(mut f: Fn) -> Self {
-        let mut result = Self::default();
-        for i in 0..Self::WIDTH {
-            let val = f(i);
-            for j in 0..5 {
-                result.value[j].as_slice_mut()[i] = val.value[j];
-            }
-        }
-        result
-    }
-
-    #[inline]
-    fn as_slice(&self) -> &[Self::Value] {
-        unsafe {
-            core::slice::from_raw_parts(self as *const Self as *const Self::Value, Self::WIDTH)
-        }
-    }
-
-    #[inline]
-    fn as_slice_mut(&mut self) -> &mut [Self::Value] {
-        unsafe {
-            core::slice::from_raw_parts_mut(self as *mut Self as *mut Self::Value, Self::WIDTH)
-        }
-    }
-}
-
-// SAFETY: Implements all required trait bounds.
-unsafe impl<F, PF> PackedField for PackedQuinticTrinomialExtensionField<F, PF>
-where
-    F: QuinticTrinomialExtendable,
-    PF: PackedField<Scalar = F>,
-{
-    type Scalar = QuinticTrinomialExtensionField<F>;
-}
-
 impl<F: QuinticTrinomialExtendable> PackedFieldExtension<F, QuinticTrinomialExtensionField<F>>
     for PackedQuinticTrinomialExtensionField<F, F::Packing>
 {
     #[inline]
-    fn from_ext_slice(ext_slice: &[QuinticTrinomialExtensionField<F>]) -> Self {
-        let width = F::Packing::WIDTH;
-        assert_eq!(ext_slice.len(), width);
-
-        Self::new(F::Packing::pack_columns_fn(|lane| ext_slice[lane].value))
+    fn from_ext_fn(f: impl Fn(usize) -> QuinticTrinomialExtensionField<F>) -> Self {
+        Self::new(F::Packing::pack_columns_fn(|lane| f(lane).value))
     }
 
     #[inline]
@@ -598,28 +537,18 @@ where
     }
 }
 
-impl<F, PF> Div for PackedQuinticTrinomialExtensionField<F, PF>
-where
-    F: QuinticTrinomialExtendable,
-    PF: PackedField<Scalar = F>,
-{
+impl<F: QuinticTrinomialExtendable> Div for PackedQuinticTrinomialExtensionField<F, F::Packing> {
     type Output = Self;
 
     #[allow(clippy::suspicious_arithmetic_impl)]
     #[inline]
     fn div(self, rhs: Self) -> Self {
-        let mut rhs_inv = Self::broadcast(QuinticTrinomialExtensionField::<F>::ZERO);
-        crate::batch_multiplicative_inverse_general(rhs.as_slice(), rhs_inv.as_slice_mut(), |x| {
-            x.inverse()
-        });
-        self * rhs_inv
+        self * crate::invert_packed_extension::<F, QuinticTrinomialExtensionField<F>>(rhs)
     }
 }
 
-impl<F, PF> DivAssign for PackedQuinticTrinomialExtensionField<F, PF>
-where
-    F: QuinticTrinomialExtendable,
-    PF: PackedField<Scalar = F>,
+impl<F: QuinticTrinomialExtendable> DivAssign
+    for PackedQuinticTrinomialExtensionField<F, F::Packing>
 {
     #[inline]
     fn div_assign(&mut self, rhs: Self) {
```

### field/src/field.rs
```diff
@@ -1120,6 +1120,24 @@ pub trait ExtensionField<Base: Field>: Field + Algebra<Base> + BasedVectorSpace<
     /// Otherwise return None.
     #[must_use]
     fn as_base(&self) -> Option<Base>;
+
+    /// Reassemble an element of `Self` from `D = DIMENSION` coefficients in `Self`
+    /// via `Σⱼ basisⱼ · coeffsⱼ`. Returns `None` if `coeffs.len() != Self::DIMENSION`.
+    ///
+    /// This is the `Self`-coefficient counterpart to
+    /// [`BasedVectorSpace::from_basis_coefficients_slice`], which takes coefficients
+    /// in `Base`. It is the natural "lifting" operation in commit-and-open protocols:
+    /// if an extension polynomial decomposes as `f(X) = Σⱼ basisⱼ · fⱼ(X)` with
+    /// `fⱼ` over `Base`, then `f(z) = Σⱼ basisⱼ · fⱼ(z)` for any `z ∈ Self`.
+    #[inline]
+    #[must_use]
+    fn from_ext_basis_coefficients(coeffs: &[Self]) -> Option<Self> {
+        (coeffs.len() == Self::DIMENSION).then(|| {
+            (0..Self::DIMENSION)
+                .map(|j| Self::ith_basis_element(j).unwrap() * coeffs[j])
+                .sum()
+        })
+    }
 }
 
 // Every field is trivially a one dimensional extension over itself.
@@ -1135,6 +1153,11 @@ impl<F: Field> ExtensionField<F> for F {
     fn as_base(&self) -> Option<F> {
         Some(*self)
     }
+
+    #[inline]
+    fn from_ext_basis_coefficients(coeffs: &[Self]) -> Option<Self> {
+        (coeffs.len() == 1).then(|| coeffs[0])
+    }
 }
 
 /// A field which supplies information like the two-adicity of its multiplicative group, and methods
```

### field/src/packed/packed_traits.rs
```diff
@@ -367,11 +367,59 @@ pub trait PackedFieldExtension<
     ExtField: ExtensionField<BaseField, ExtensionPacking = Self>,
 >: Algebra<ExtField> + Algebra<BaseField::Packing> + BasedVectorSpace<BaseField::Packing>
 {
-    /// Given a slice of extension field `EF` elements of length `W`,
-    /// convert into the array `[[F; D]; W]` transpose to
-    /// `[[F; W]; D]` and then pack to get `[PF; D]`.
+    /// Construct a packed extension by applying `f` to each lane.
+    ///
+    /// This is the extension-field analog of [`PackedValue::from_fn`] and the canonical
+    /// primitive constructor for packed extensions: every other constructor in this
+    /// trait (`from_ext_slice`, `pack_ext_columns`, etc.) routes through it.
+    ///
+    /// `f` is called once per `(basis_coefficient, lane)` pair (`D * W` calls total),
+    /// hence the [`Fn`] bound — closures with side effects are unsuitable.
+    ///
+    /// The default impl uses only the [`BasedVectorSpace`] machinery the trait already
+    /// requires. Concrete impls should override when the extension struct exposes its
+    /// base packings directly, e.g. `Self::new(F::Packing::pack_columns_fn(|l| f(l).value))`.
+    #[inline]
+    #[must_use]
+    fn from_ext_fn(f: impl Fn(usize) -> ExtField) -> Self {
+        Self::from_basis_coefficients_fn(|d| {
+            BaseField::Packing::from_fn(|lane| f(lane).as_basis_coefficients_slice()[d])
+        })
+    }
+
+    /// Pack a length-`WIDTH` slice of extension field elements into one packed extension.
+    ///
+    /// ## Panics
+    /// Panics if `slice.len() != BaseField::Packing::WIDTH`.
+    #[inline]
+    #[must_use]
+    fn from_ext_slice(slice: &[ExtField]) -> Self {
+        assert_eq!(slice.len(), BaseField::Packing::WIDTH);
+        Self::from_ext_fn(|lane| slice[lane])
+    }
+
+    /// Pack `N` columns from `W` rows of extension field elements into `N` packed extensions.
+    ///
+    /// This is the extension-field analog of [`PackedValue::pack_columns`]: given `W` rows
+    /// of `N` extension elements, lane `lane` of output column `col` is `rows[lane][col]`.
+    ///
+    /// ## Panics
+    /// Panics if `rows.len() != BaseField::Packing::WIDTH`.
+    #[inline]
     #[must_use]
-    fn from_ext_slice(ext_slice: &[ExtField]) -> Self;
+    fn pack_ext_columns<const N: usize>(rows: &[[ExtField; N]]) -> [Self; N] {
+        assert_eq!(rows.len(), BaseField::Packing::WIDTH);
+        array::from_fn(|col| Self::from_ext_fn(|lane| rows[lane][col]))
+    }
+
+    /// Pack `N` columns using a closure that produces each row.
+    ///
+    /// Analog of [`PackedValue::pack_columns_fn`].
+    #[inline]
+    #[must_use]
+    fn pack_ext_columns_fn<const N: usize>(row_fn: impl Fn(usize) -> [ExtField; N]) -> [Self; N] {
+        array::from_fn(|col| Self::from_ext_fn(|lane| row_fn(lane)[col]))
+    }
 
     /// Extract the extension field element at the given SIMD lane.
     #[inline]
@@ -382,10 +430,60 @@ pub trait PackedFieldExtension<
         })
     }
 
-    /// Convert an iterator of packed extension field elements to an iterator of
-    /// extension field elements.
+    /// Write all `W` lanes into the given slice.
+    ///
+    /// This is the extension-field analog of [`PackedValue::as_slice`], but the lanes of
+    /// a packed extension are not contiguous in memory (the layout is `[[F; W]; D]`,
+    /// indexed first by basis coefficient), so the lanes must be copied rather than
+    /// borrowed.
+    ///
+    /// ## Panics
+    /// Panics if `out.len() != BaseField::Packing::WIDTH`.
+    #[inline]
+    fn to_ext_slice(&self, out: &mut [ExtField]) {
+        assert_eq!(out.len(), BaseField::Packing::WIDTH);
+        for (lane, slot) in out.iter_mut().enumerate() {
+            *slot = self.extract(lane);
+        }
+    }
+
+    /// Unpack `N` packed extensions into `W` rows of `N` extension elements.
+    ///
+    /// Inverse of [`PackedFieldExtension::pack_ext_columns`]. Lane `lane` of input
+    /// column `col` is written to `rows[lane][col]`.
+    ///
+    /// ## Panics
+    /// Panics if `rows.len() != BaseField::Packing::WIDTH`.
+    #[inline]
+    fn unpack_ext_into<const N: usize>(packed: &[Self; N], rows: &mut [[ExtField; N]]) {
+        assert_eq!(rows.len(), BaseField::Packing::WIDTH);
+        #[allow(clippy::needless_range_loop)]
+        for lane in 0..BaseField::Packing::WIDTH {
+            rows[lane] = array::from_fn(|col| {
+                ExtField::from_basis_coefficients_fn(|d| {
+                    packed[col].as_basis_coefficients_slice()[d].as_slice()[lane]
+                })
+            });
+        }
+    }
+
+    /// Iterator equivalent of [`PackedFieldExtension::unpack_ext_into`].
     ///
-    /// This performs the inverse transformation to `from_ext_slice`.
+    /// Yields `WIDTH` rows of `N` extension elements without requiring a pre-allocated
+    /// buffer. Analog of [`PackedValue::unpack_iter`].
+    #[inline]
+    fn unpack_ext_iter<const N: usize>(packed: [Self; N]) -> impl Iterator<Item = [ExtField; N]> {
+        (0..BaseField::Packing::WIDTH).map(move |lane| {
+            array::from_fn(|col| {
+                ExtField::from_basis_coefficients_fn(|d| {
+                    packed[col].as_basis_coefficients_slice()[d].as_slice()[lane]
+                })
+            })
+        })
+    }
+
+    /// Convert an iterator of packed extension field elements to an iterator of
+    /// extension field elements (flat — one [`ExtField`] per lane per packed value).
     #[inline]
     #[must_use]
     fn to_ext_iter(iter: impl IntoIterator<Item = Self>) -> impl Iterator<Item = ExtField> {
@@ -461,8 +559,13 @@ unsafe impl<F: Field> PackedFieldPow2 for F {
 
 impl<F: Field> PackedFieldExtension<F, F> for F::Packing {
     #[inline]
-    fn from_ext_slice(ext_slice: &[F]) -> Self {
-        *F::Packing::from_slice(ext_slice)
+    fn from_ext_fn(f: impl Fn(usize) -> F) -> Self {
+        F::Packing::from_fn(f)
+    }
+
+    #[inline]
+    fn from_ext_slice(slice: &[F]) -> Self {
+        *F::Packing::from_slice(slice)
     }
 
     #[inline]
```

### uni-stark/src/verifier.rs
```diff
@@ -8,7 +8,7 @@ use p3_air::symbolic::SymbolicAirBuilder;
 use p3_air::{Air, RowWindow};
 use p3_challenger::{CanObserve, FieldChallenger};
 use p3_commit::{Pcs, PolynomialSpace};
-use p3_field::{BasedVectorSpace, Field, PrimeCharacteristicRing};
+use p3_field::{BasedVectorSpace, ExtensionField, Field, PrimeCharacteristicRing};
 use p3_matrix::dense::RowMajorMatrixView;
 use p3_matrix::stack::VerticalPair;
 use p3_util::zip_eq::zip_eq;
@@ -73,18 +73,15 @@ where
         })
         .collect_vec();
 
+    // valid_shape checks each ch has length <SC::Challenge as BasedVectorSpace<Val<SC>>>::DIMENSION,
+    // so from_ext_basis_coefficients won't return None.
     quotient_chunks
         .iter()
         .enumerate()
         .map(|(ch_i, ch)| {
-            // We checked in valid_shape the length of "ch" is equal to
-            // <SC::Challenge as BasedVectorSpace<Val<SC>>>::DIMENSION. Hence
-            // the unwrap() will never panic.
             zps[ch_i]
-                * ch.iter()
-                    .enumerate()
-                    .map(|(e_i, &c)| SC::Challenge::ith_basis_element(e_i).unwrap() * c)
-                    .sum::<SC::Challenge>()
+                * SC::Challenge::from_ext_basis_coefficients(ch)
+                    .expect("quotient chunk length checked in valid_shape")
         })
         .sum::<SC::Challenge>()
 }
```
