# [?] perf(binary-dft): exploit subfield structure in the additive transform and the encoder (#2173)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-09-18
Source: https://github.com/Plonky3/Plonky3/commit/050da26edb515538a9bb0c7a65855bfcf3fef049
Type: security-commit

## Details
perf(binary-dft): exploit subfield structure in the additive transform and the encoder (#2173)

* perf(binary-dft): type the two- and four-byte subfield twiddles

A butterfly whose twiddle lies in a byte-aligned tower subfield can scale each
coordinate of an element on its own, which is what the one-byte case already did.
The two- and four-byte cases fell through to a full-width product instead, because
the narrow levels have no product against a subfield as wide as themselves and so
cannot carry a single generic bound.

A chain of three generic scaling functions, one per subfield width, plus one
forwarding impl per level, gives each level exactly the typed products it has.
A hardware carryless multiply reprices the widest two levels below anything
multi-coordinate, so those take the chain only where the instruction is absent.

Measured on a Ryzen 9 9950X3D, forward transform at width 16, height 2^18:

    arm                    before      after     gain
    ntt/128/tower         97.1 ms    39.6 ms    2.45x
    ntt/64                33.4 ms    15.3 ms    2.19x
    ntt/32                11.9 ms     7.9 ms    1.51x

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

* perf(binary-dft): run a subfield message's closed layers at its own width

At commit time a trace is bit- or byte-valued, and the widest butterfly layers of an
unshifted transform scale by twiddles from the message's own subfield. Those layers
therefore map the subfield into itself and need none of the alphabet's width.

Splitting a row index into its top and bottom halves turns the network into two whole
transforms: the closed layers are the entire transform of the buffer read as a short
wide matrix at the narrow level, and the rest is the stage range the buffer really is.
Both are unshifted and share their block indices, so they agree twiddle for twiddle.

The threshold below which the split is skipped is stated rather than implicit: a
message inside a private cache saves nothing on those layers and pays a thread handoff
per layer for the privilege.

Measured on a Ryzen 9 9950X3D against the better of the two unspecialised routes,
byte message to a `BinaryField128` codeword, width 16:

    height   portable before   after     gain     native before   after    gain
    2^14           1.954 ms   1.492 ms   1.31x        361.5 us   244.7 us  1.48x
    2^16           8.626 ms   7.193 ms   1.20x        900.9 us   629.5 us  1.43x
    2^18          50.98 ms   36.44 ms    1.40x         15.18 ms    6.21 ms 2.45x
    2^20         239.0 ms   178.1 ms     1.34x         78.80 ms   36.57 ms 2.15x

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

* bench(sumcheck): measure the univariate-skip extension and its round message

The table-driven extension had no benchmark, so nothing said what it costs against
the composition and the equality weighting that surround it in a prover round.

Three arms: one row, a block of rows, and the whole streamed round message, over the
two levels a skipped round runs on and three domain shapes.

On a Ryzen 9 9950X3D the byte-level product-form shape extends one row in 18.2 ns,
and a streamed round message over 2^16 rows and three operands takes 2.67 ms. The
extension is therefore about four percent of the round, and the weighted composition
over the wide alphabet is the rest.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

* feat(binary-dft): encode a column-major message into an interleaved codeword

A commitment that folds several variables at a time opens whole folding blocks, so its
codeword is a matrix of one column per block. A prover holds the opposite layout, with
each block's coefficients contiguous, and today brings the two together in a pass of
its own before handing the encoder a matrix.

Zero-padding is what extends the domain, and the layers that cross the padding read
only zeros, so they copy the message into each coset and compute nothing. Writing that
copy directly in the interleaved order puts the transpose inside a pass that has to
happen anyway, and the layers left over are one shifted transform per coset.

Measured on a Ryzen 9 9950X3D against the transpose-then-encode route a commitment
takes today, sixteen columns of `BinaryField128`:

    shape          portable before   after      gain     native before  after      gain
    2^16 * 1/2      27.88 ms   24.61 ms   1.13x      7.92 ms   7.18 ms   1.10x
    2^16 * 1/4      58.97 ms   48.25 ms   1.22x     13.42 ms  11.74 ms   1.14x
    2^18 * 1/4     277.8 ms   227.1 ms    1.22x     63.80 ms  61.34 ms   1.04x
    2^20 * 1/4    1285 ms    1014 ms      1.27x    291.5 ms  282.9 ms    1.03x
    2^20 * 1/8    2681 ms    2057 ms      1.30x    520.2 ms  501.9 ms    1.03x

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

* review(binary-dft,binary-field): address the transforms-and-encoding review

Move the zero-padding skip out of the interleaved encoder and into the
tower transform's padded entry point, so the encoders reach it through
the trait rather than through a free function, and so the benchmark arm
that isolates the fusion skips the same layers the fused path does.

Widen the field crate's mixed-product crossover to cover the eight-byte
level. With a carryless multiply the coordinate expansion there costs
2.1x the embedded product at a four-byte subfield and 1.04x at a
two-byte one, measured by a new mixed-product benchmark. The transform's
own gate stays: it chooses between a scalar typed loop and the packed
full-width kernel, not between two product widths, and dropping it costs
the full-width twiddle 8 to 78 percent.

Share the padded-length check between the encoder, the subfield encoder
and the interleaved one. Reject an empty column list and a message
dimension no length can address, instead of panicking later inside a
chunk split. Widen the subfield benchmark's reference so it widens
across the machine, as the specialised route does.

Pin what the review found untested: every partial stage range against
the same stages run one pass at a time, in both directions and at named
worker counts; the padded transform against running the skipped layers;
and the split past the layers a byte subfield is closed under, against
the reference oracle rather than against another transform.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

* docs(binary-dft): say which transform the subfield split's second phase runs

The widest layers run at the narrow width, and the layers left over run
this crate's tower transform rather than whichever backend is fastest at
the wide element size. On a target where the two differ substantially at
that width, widening first through the faster one can beat the split, so
the entry point's doc now states which one it uses.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>

---------

Co-authored-by: Claude Opus 5 (1M context) <noreply@anthropic.com>

## Patch
### binary-dft/benches/ntt.rs
```diff
@@ -7,13 +7,18 @@ use criterion::{
     BatchSize, BenchmarkGroup, BenchmarkId, Criterion, Throughput, criterion_group, criterion_main,
 };
 use p3_baby_bear::BabyBear;
-use p3_binary_dft::{AdditiveNtt, AdditiveRsEncoder, ButterflyField, LchNtt, PolyBasisNtt};
+use p3_binary_dft::{
+    AdditiveNtt, AdditiveRsEncoder, ButterflyField, LchNtt, PolyBasisNtt, interleaved_encode_batch,
+    subfield_encode_batch, subfield_ntt_batch,
+};
 use p3_binary_field::{
-    BinaryField16, BinaryField32, BinaryField64, BinaryField128, Ghash128, TowerLevel,
+    BinaryField8, BinaryField16, BinaryField32, BinaryField64, BinaryField128, Ghash128, TowerLevel,
 };
 use p3_commit::Encoder;
 use p3_dft::Radix2DFTSmallBatch;
-use p3_matrix::dense::RowMajorMatrix;
+use p3_field::PrimeCharacteristicRing;
+use p3_matrix::dense::{RowMajorMatrix, RowMajorMatrixView, RowMajorMatrixViewMut};
+use p3_maybe_rayon::prelude::*;
 use rand::distr::{Distribution, StandardUniform};
 use rand::rngs::SmallRng;
 use rand::{RngExt, SeedableRng};
@@ -234,6 +239,132 @@ fn bench_encode(c: &mut Criterion) {
     }
 }
 
+/// The two routes from a byte-valued message to a wide codeword.
+///
+/// Either way the caller ends up with `BinaryField128` evaluations.
+///
+/// ```text
+///     wide      widen every entry, then transform at the wide element size
+///     subfield  transform the closed layers at the byte size, then widen
+/// ```
+///
+/// The wide arm carries the widening pass too, since a caller pays it in both routes.
+fn bench_subfield(c: &mut Criterion) {
+    let mut group = c.benchmark_group("subfield");
+    group.sample_size(10);
+
+    let mut rng = SmallRng::seed_from_u64(3);
+    let lch = LchNtt::<BinaryField128>::default();
+    let poly = PolyBasisNtt::default();
+
+    for log_height in LOG_HEIGHTS {
+        for width in [1, WIDTH] {
+            let message = RowMajorMatrix::<BinaryField8>::rand(&mut rng, 1 << log_height, width);
+            let parameter = format!("h{log_height}/w{width}");
+
+            // Throughput counts the matrix entries, so every arm compares directly.
+            group.throughput(Throughput::Elements((width << log_height) as u64));
+
+            // The specialised route widens across the machine above a few mebibytes.
+            // A serial widen here would charge the wide arms its page faults as well.
+            let widen = |m: &RowMajorMatrix<BinaryField8>| {
+                RowMajorMatrix::new(
+                    m.values
+                        .par_iter()
+                        .copied()
+                        .map(BinaryField128::from)
+                        .collect(),
+                    width,
+                )
+            };
+
+            group.bench_function(BenchmarkId::new("wide/lch", &parameter), |b| {
+                b.iter(|| lch.ntt_batch(widen(&message)));
+            });
+            group.bench_function(BenchmarkId::new("wide/poly", &parameter), |b| {
+                b.iter(|| poly.ntt_batch(widen(&message)));
+            });
+            group.bench_function(BenchmarkId::new("subfield", &parameter), |b| {
+                b.iter_batched(
+                    || message.clone(),
+                    subfield_ntt_batch::<BinaryField8, BinaryField128>,
+                    BatchSize::PerIteration,
+                );
+            });
+
+            // The encoder over the same message, where the zero padding is byte-sized too.
+            // Throughput still counts the message entries, so it compares with the arms above.
+            group.bench_function(BenchmarkId::new("subfield/encode", &parameter), |b| {
+                b.iter_batched(
+                    || message.clone(),
+                    |m| subfield_encode_batch::<BinaryField8, BinaryField128>(m, LOG_INV_RATE),
+                    BatchSize::PerIteration,
+                );
+            });
+        }
+    }
+    group.finish();
+}
+
+/// The two routes from a column-major message to an interleaved codeword.
+///
+/// ```text
+///     two-pass  interleave in a pass of its own, then encode the padded matrix
+///     fused     interleave into the first coset, then transform each coset
+/// ```
+fn bench_interleaved(c: &mut Criterion) {
+    let mut group = c.benchmark_group("interleaved");
+    group.sample_size(10);
+
+    let mut rng = SmallRng::seed_from_u64(13);
+    let encoder = AdditiveRsEncoder::<BinaryField128>::default();
+
+    for log_message in LOG_HEIGHTS {
+        for log_inv_rate in [1usize, 2, 3] {
+            let columns = (0..WIDTH << log_message)
+                .map(|_| rng.random::<BinaryField128>())
+                .collect::<Vec<_>>();
+            let parameter = format!("h{log_message}/r{log_inv_rate}");
+
+            // Throughput counts the codeword entries, so the rates compare.
+            group.throughput(Throughput::Elements(
+                ((WIDTH << log_message) << log_inv_rate) as u64,
+            ));
+
+            group.bench_function(BenchmarkId::new("two_pass", &parameter), |b| {
+                b.iter(|| {
+                    // The layout `commit_base` builds before it hands the encoder a matrix.
+                    let mut values = BinaryField128::zero_vec(columns.len() << log_inv_rate);
+                    let source = RowMajorMatrixView::new(&columns, 1 << log_message);
+                    let mut target =
+                        RowMajorMatrixViewMut::new(&mut values[..columns.len()], WIDTH);
+                    source.transpose_into(&mut target);
+                    encoder.encode_batch_padded(RowMajorMatrix::new(values, WIDTH), log_inv_rate)
+                });
+            });
+
+            // The same backend as the fused path, and the same padded entry point.
+            // So the pair differs in the transpose alone, not in the layers it skips.
+            let lch = LchNtt::<BinaryField128>::default();
+            group.bench_function(BenchmarkId::new("two_pass/lch", &parameter), |b| {
+                b.iter(|| {
+                    let mut values = BinaryField128::zero_vec(columns.len() << log_inv_rate);
+                    let source = RowMajorMatrixView::new(&columns, 1 << log_message);
+                    let mut target =
+                        RowMajorMatrixViewMut::new(&mut values[..columns.len()], WIDTH);
+                    source.transpose_into(&mut target);
+                    lch.ntt_batch_padded(RowMajorMatrix::new(values, WIDTH), log_inv_rate)
+                });
+            });
+
+            group.bench_function(BenchmarkId::new("fused", &parameter), |b| {
+                b.iter(|| interleaved_encode_batch(&columns, log_message, log_inv_rate));
+            });
+        }
+    }
+    group.finish();
+}
+
 /// Direct polynomial-backend workloads, including small later-round domains.
 fn bench_poly(c: &mut Criterion) {
     eprintln!(
@@ -349,6 +480,8 @@ criterion_group!(
     benches,
     bench_butterfly,
     bench_ntt,
+    bench_subfield,
+    bench_interleaved,
     bench_encode,
     bench_poly,
     bench_commit
```

### binary-dft/src/butterfly.rs
```diff
@@ -2,6 +2,7 @@
 
 use core::ops::Mul;
 
+use p3_binary_field::poly_basis::HAS_HARDWARE_CLMUL;
 use p3_binary_field::{
     BinaryField2, BinaryField4, BinaryField8, BinaryField16, BinaryField32, BinaryField64,
     BinaryField128, Gf2, Ghash128, TowerLevel,
@@ -149,6 +150,155 @@ where
     }
 }
 
+/// Scale by a one-byte twiddle, or fall through to the full-width kernel.
+///
+/// This is the end of the chain: no byte-aligned subfield is narrower than one byte.
+#[inline]
+fn scale_by_byte<F, const INVERSE: bool>(lo: &mut [F], hi: &mut [F], t: F, width: TwiddleWidth)
+where
+    F: TowerLevel + Mul<BinaryField8, Output = F>,
+{
+    if let TwiddleWidth::Byte(s) = width {
+        typed_butterfly::<F, BinaryField8, INVERSE>(lo, hi, BinaryField8::from_repr(s));
+    } else {
+        packed_butterfly::<F, INVERSE>(lo, hi, t);
+    }
+}
+
+/// Scale by a two-byte twiddle, or hand a narrower one down the chain.
+#[inline]
+fn scale_by_word<F, const INVERSE: bool>(lo: &mut [F], hi: &mut [F], t: F, width: TwiddleWidth)
+where
+    F: TowerLevel + Mul<BinaryField8, Output = F> + Mul<BinaryField16, Output = F>,
+{
+    if let TwiddleWidth::Word(s) = width {
+        typed_butterfly::<F, BinaryField16, INVERSE>(lo, hi, BinaryField16::from_repr(s));
+    } else {
+        scale_by_byte::<F, INVERSE>(lo, hi, t, width);
+    }
+}
+
+/// Scale by a four-byte twiddle, or hand a narrower one down the chain.
+#[inline]
+fn scale_by_dword<F, const INVERSE: bool>(lo: &mut [F], hi: &mut [F], t: F, width: TwiddleWidth)
+where
+    F: TowerLevel
+        + Mul<BinaryField8, Output = F>
+        + Mul<BinaryField16, Output = F>
+        + Mul<BinaryField32, Output = F>,
+{
+    if let TwiddleWidth::DoubleWord(s) = width {
+        typed_butterfly::<F, BinaryField32, INVERSE>(lo, hi, BinaryField32::from_repr(s));
+    } else {
+        scale_by_word::<F, INVERSE>(lo, hi, t, width);
+    }
+}
+
+/// Whether a typed product beats the full-width product at the two widest levels.
+///
+/// - Scaling by a `D`-byte subfield costs one subfield product per coordinate.
+/// - Recursive multiplication triples in cost per doubling of the width.
+/// - The coordinate count only halves, so the narrower subfield always wins.
+///
+/// A carryless-multiply instruction breaks that at the widest two levels.
+/// Only the one-byte coordinates stay ahead of it, being single table lookups.
+///
+/// The field crate makes the same call for the product alone, and this is not the same call.
+/// A typed run walks one element at a time, and the full-width run packs a register of them.
+///
+/// The whole chain is inlined into one kernel.
+/// So carrying the wide levels through it costs the full-width route its own codegen.
+const WIDE_TYPED_PRODUCTS_PAY: bool = !HAS_HARDWARE_CLMUL;
+
+/// A tower level together with the typed subfield products its own width admits.
+///
+/// A typed product needs the subfield to be strictly narrower than the level.
+/// So the narrow levels route more of the twiddle widths to the full-width kernel.
+///
+/// The chain above holds the shared logic, and an implementation only names its entry point.
+trait SubfieldScaled: ByteCoordinates {
+    /// Apply the butterfly through the narrowest typed product that covers the twiddle.
+    fn scale_butterfly<const INVERSE: bool>(
+        lo: &mut [Self],
+        hi: &mut [Self],
+        t: Self,
+        width: TwiddleWidth,
+    );
+}
+
+impl SubfieldScaled for BinaryField8 {
+    /// One byte wide, so every twiddle is the whole element and no subfield is left.
+    #[inline]
+    fn scale_butterfly<const INVERSE: bool>(
+        lo: &mut [Self],
+        hi: &mut [Self],
+        t: Self,
+        width: TwiddleWidth,
+    ) {
+        scale_by_byte::<Self, INVERSE>(lo, hi, t, width);
+    }
+}
+
+impl SubfieldScaled for BinaryField16 {
+    /// A two-byte twiddle is the whole element here, so the one-byte product is the only gain.
+    #[inline]
+    fn scale_butterfly<const INVERSE: bool>(
+        lo: &mut [Self],
+        hi: &mut [Self],
+        t: Self,
+        width: TwiddleWidth,
+    ) {
+        scale_by_byte::<Self, INVERSE>(lo, hi, t, width);
+    }
+}
+
+impl SubfieldScaled for BinaryField32 {
+    /// A four-byte twiddle is the whole element here, so the chain stops at two bytes.
+    #[inline]
+    fn scale_butterfly<const INVERSE: bool>(
+        lo: &mut [Self],
+        hi: &mut [Self],
+        t: Self,
+        width: TwiddleWidth,
+    ) {
+        scale_by_word::<Self, INVERSE>(lo, hi, t, width);
+    }
+}
+
+impl SubfieldScaled for BinaryField64 {
+    /// Wide enough for every typed product, where the level's own product is recursive.
+    #[inline]
+    fn scale_butterfly<const INVERSE: bool>(
+        lo: &mut [Self],
+        hi: &mut [Self],
+        t: Self,
+        width: TwiddleWidth,
+    ) {
+        if WIDE_TYPED_PRODUCTS_PAY {
+            scale_by_dword::<Self, INVERSE>(lo, hi, t, width);
+        } else {
+            scale_by_byte::<Self, INVERSE>(lo, hi, t, width);
+        }
+    }
+}
+
+impl SubfieldScaled for BinaryField128 {
+    /// Wide enough for every typed product, where the level's own product is recursive.
+    #[inline]
+    fn scale_butterfly<const INVERSE: bool>(
+        lo: &mut [Self],
+        hi: &mut [Self],
+        t: Self,
+        width: TwiddleWidth,
+    ) {
+        if WIDE_TYPED_PRODUCTS_PAY {
+            scale_by_dword::<Self, INVERSE>(lo, hi, t, width);
+        } else {
+            scale_by_byte::<Self, INVERSE>(lo, hi, t, width);
+        }
+    }
+}
+
 /// Run the leading whole registers through the byte map the twiddle's width allows.
 ///
 /// Returns the number of elements covered, which the caller finishes from.
@@ -236,14 +386,14 @@ const fn subfield_prefix<F: ByteCoordinates, const INVERSE: bool>(
 ///
 /// A twiddle narrow enough to sit in a byte-aligned subfield drives a byte map.
 ///
-/// Anything wider falls through to the packed kernel.
+/// Whatever the byte map leaves over falls to a typed product of the same subfield.
 ///
 /// # Panics
 /// Panics if the two runs have different lengths.
 #[inline]
 fn coordinate_butterfly<F, const INVERSE: bool>(lo: &mut [F], hi: &mut [F], t: F)
 where
-    F: ByteCoordinates + Mul<BinaryField8, Output = F>,
+    F: SubfieldScaled,
     F::Repr: Into<u128>,
 {
     // Invariant: the two sides are paired element for element.
@@ -260,16 +410,10 @@ where
     let covered = subfield_prefix::<F, INVERSE>(lo, hi, width);
 
     // Whatever the register loop left over, down to one element.
-    let (lo, hi) = (&mut lo[covered..], &mut hi[covered..]);
-
-    if let TwiddleWidth::Byte(t) = width {
-        // A one-coordinate twiddle scales each coordinate on its own.
-        //
-        // That beats a full-width product even with no byte map to run it through.
-        typed_butterfly::<F, BinaryField8, INVERSE>(lo, hi, BinaryField8::from_repr(t));
-    } else {
-        packed_butterfly::<F, INVERSE>(lo, hi, t);
-    }
+    //
+    // A subfield twiddle scales each coordinate on its own.
+    // That beats a full-width product even with no byte map to run it through.
+    F::scale_butterfly::<INVERSE>(&mut lo[covered..], &mut hi[covered..], t, width);
 }
 
 /// The butterfly of a level with no subfield structure to exploit.
@@ -368,23 +512,31 @@ mod tests {
     /// ```text
     ///     0               the butterfly collapses to a single addition
     ///     1               the identity multiplier
+    ///     0x80            the highest-degree basis element of the one-byte subfield
     ///     0xff            the widest twiddle the one-byte map still covers
     ///     0x100           the narrowest that needs the two-byte map
+    ///     0x8000          the highest-degree basis element of the two-byte subfield
     ///     0xffff          the widest the two-byte map covers
     ///     0x1_0000        the narrowest that needs the four-byte map
+    ///     0x8000_0000     the highest-degree basis element of the four-byte subfield
     ///     0xffff_ffff     the widest the four-byte map covers
     ///     0x1_0000_0000   the narrowest that falls through to the packed kernel
+    ///     1 << 127        the highest-degree basis element of the widest level
     ///     0x87            the tail of the GHASH modulus, for the level that uses it
     /// ```
-    const CORNERS: [u128; 9] = [
+    const CORNERS: [u128; 13] = [
         0,
         1,
+        0x80,
         0xff,
         0x100,
+        0x8000,
         0xffff,
         0x1_0000,
+        0x8000_0000,
         0xffff_ffff,
         0x1_0000_0000,
+        1 << 127,
         0x87,
     ];
 
```

### binary-dft/src/encoder.rs
```diff
@@ -12,6 +12,21 @@ use p3_util::log2_strict_usize;
 use crate::poly::PolyBasisNtt;
 use crate::traits::AdditiveNtt;
 
+/// The length a message grows to once its coefficients are zero-padded to the target rate.
+///
+/// # Panics
+///
+/// Panics if that length does not fit the address space.
+pub(crate) fn padded_message_len(len: usize, log_inv_rate: usize) -> usize {
+    // A shift amount below the word size still leaves the value itself free to overflow.
+    // Recovering the original length from the shifted one is what proves no bits were lost.
+    u32::try_from(log_inv_rate)
+        .ok()
+        .and_then(|rate| len.checked_shl(rate))
+        .filter(|&padded| padded >> log_inv_rate == len)
+        .expect("codeword length overflows usize")
+}
+
 /// Reed–Solomon over the additive NTT domain.
 ///
 /// The message holds the low-index novel-basis coefficients of each column, so the codeword is
@@ -42,15 +57,8 @@ impl<Ntt: AdditiveNtt<BinaryField128> + Sync> Encoder<BinaryField128>
             return self.ntt.ntt_batch(message);
         }
 
-        let len = message.values.len();
-        let padded_len = u32::try_from(log_inv_rate)
-            .ok()
-            .and_then(|rate| len.checked_shl(rate))
-            // `checked_shl` only rejects a shift amount that is too wide; it does not detect
-            // the value itself overflowing, so recovering `len` from the shifted result is
-            // what actually proves no bits were lost.
-            .filter(|&padded| padded >> log_inv_rate == len)
-            .expect("codeword length overflows usize");
+        // Zero-padding the novel-basis coefficients is what extends the domain.
+        let padded_len = padded_message_len(message.values.len(), log_inv_rate);
         let _ = log2_strict_usize(message.height());
         message.values.resize(padded_len, BinaryField128::ZERO);
         self.ntt.ntt_batch_padded(message, log_inv_rate)
@@ -78,7 +86,7 @@ mod tests {
     use rand::SeedableRng;
     use rand::rngs::SmallRng;
 
-    use super::AdditiveRsEncoder;
+    use super::{AdditiveRsEncoder, padded_message_len};
     use crate::naive::NaiveAdditiveNtt;
     use crate::traits::AdditiveNtt;
 
@@ -161,6 +169,34 @@ mod tests {
         let _ = AdditiveRsEncoder::<F>::default().encode_batch_padded(mat, 1);
     }
 
+    #[test]
+    fn the_padded_length_is_the_message_length_shifted() {
+        // Fixture state: a rate of 1/8 multiplies the coefficient count by eight.
+        assert_eq!(padded_message_len(48, 3), 384);
+
+        // No added dimension leaves the message length alone.
+        assert_eq!(padded_message_len(48, 0), 48);
+
+        // An empty message stays empty at every rate.
+        assert_eq!(padded_message_len(0, 60), 0);
+    }
+
+    #[test]
+    #[should_panic = "codeword length overflows usize"]
+    fn the_padded_length_refuses_a_shift_past_the_word_size() {
+        // A shift of the whole word width has no result `usize` can hold.
+        let _ = padded_message_len(2, usize::BITS as usize);
+    }
+
+    #[test]
+    #[should_panic = "codeword length overflows usize"]
+    fn the_padded_length_refuses_a_value_that_overflows() {
+        // The shift amount fits the word, and the shifted value does not.
+        //
+        //     1 << (BITS - 1)  shifted once more drops its only set bit
+        let _ = padded_message_len(1 << (usize::BITS - 1), 1);
+    }
+
     proptest! {
         #![proptest_config(ProptestConfig::with_cases(32))]
 
```

### binary-dft/src/interleaved.rs
```diff
@@ -0,0 +1,273 @@
+//! The interleaved Reed–Solomon codeword a multi-rate commitment's levels read.
+
+use p3_matrix::dense::{RowMajorMatrix, RowMajorMatrixView, RowMajorMatrixViewMut};
+
+use crate::butterfly::ButterflyField;
+use crate::encoder::padded_message_len;
+use crate::lch::transform_cosets;
+
+/// Reed–Solomon encode a message held one folding column at a time.
+///
+/// # Overview
+///
+/// A commitment that folds `f` variables at a time opens whole folding blocks at once.
+/// Its codeword is therefore a matrix of `2^f` columns, one row per domain point.
+///
+/// A prover holds the opposite layout, with each column's coefficients contiguous.
+/// That is what binding a prefix of the variables leaves behind.
+///
+/// Bringing the two layouts together as a pass of its own writes the message once more.
+///
+/// The transform this hands the result to skips the layers that cross the padding.
+/// So the interleaving rides along with a copy that has to happen anyway.
+///
+/// # Arguments
+///
+/// - `columns`: the message's columns back to back, each `2^log_message` values long.
+/// - `log_message`: base-two logarithm of the values one column holds.
+/// - `log_inv_rate`: dimensions added to the message's own domain.
+///
+/// # Returns
+///
+/// One row per domain point, holding every column's value at that point.
+///
+/// # Panics
+///
+/// Panics if there is no column, or if the values do not divide into whole columns.
+/// Panics if the extended domain exceeds the bit width of the level.
+///
+/// Panics if the codeword length overflows the address space.
+#[must_use]
+pub fn interleaved_encode_batch<F: ButterflyField>(
+    columns: &[F],
+    log_message: usize,
+    log_inv_rate: usize,
+) -> RowMajorMatrix<F> {
+    // A codeword of no columns has neither a width to interleave into nor a height to read.
+    assert!(!columns.is_empty(), "at least one message column");
+    assert!(
+        log_message + log_inv_rate <= 1 << F::LOG_BITS,
+        "domain exceeds field dimension"
+    );
+
+    // The widest level admits 128 dimensions, which is past what a length can address.
+    // So the row count is what bounds the dimension, not the level.
+    let rows = u32::try_from(log_message)
+        .ok()
+        .and_then(|bits| 1usize.checked_shl(bits))
+        .expect("message dimension overflows usize");
+    assert_eq!(columns.len() % rows, 0, "whole message columns");
+
+    let width = columns.len() / rows;
+    let len = columns.len();
+    let mut values = F::zero_vec(padded_message_len(len, log_inv_rate));
+
+    // The first coset is the message with its columns interleaved, blocked by the transpose.
+    let source = RowMajorMatrixView::new(columns, rows);
+    let mut target = RowMajorMatrixViewMut::new(&mut values[..len], width);
+    source.transpose_into(&mut target);
+
+    // Every coset above it is a copy of that one, then its own shifted transform.
+    transform_cosets::<F>(&mut values, width, log_message);
+
+    RowMajorMatrix::new(values, width)
+}
+
+#[cfg(test)]
+mod tests {
+    use alloc::format;
+    use alloc::vec::Vec;
+
+    use p3_binary_field::{BinaryField16, BinaryField32, BinaryField128, Ghash128, TowerLevel};
+    use p3_field::PrimeCharacteristicRing;
+    use p3_matrix::dense::{RowMajorMatrix, RowMajorMatrixView, RowMajorMatrixViewMut};
+    use proptest::prelude::*;
+
+    use super::interleaved_encode_batch;
+    use crate::butterfly::ButterflyField;
+    use crate::lch::LchNtt;
+    use crate::naive::NaiveAdditiveNtt;
+    use crate::traits::AdditiveNtt;
+
+    /// Widths covering one column, an odd count, a register-sized row and a folding block.
+    const WIDTHS: [usize; 4] = [1, 3, 8, 16];
+
+    /// A column-major message whose entries depend on both the position and the seed.
+    fn columns<F: TowerLevel>(log_message: usize, width: usize, seed: u64) -> Vec<F> {
+        (0..(width << log_message))
+            .map(|i| {
+                let bits = seed
+                    .wrapping_mul(0x9e37_79b9_7f4a_7c15)
+                    .wrapping_add(i as u64 + 1)
+                    .wrapping_mul(0xbf58_476d_1ce4_e5b9);
+                F::from_le_byte_iter(bits.to_le_bytes().into_iter().cycle())
+            })
+            .collect()
+    }
+
+    /// The reference: interleave in a pass of its own, pad with zeros, transform the whole lot.
+    fn transpose_then_encode<F: ButterflyField, N: AdditiveNtt<F>>(
+        ntt: &N,
+        columns: &[F],
+        log_message: usize,
+        log_inv_rate: usize,
+    ) -> RowMajorMatrix<F> {
+        let rows = 1usize << log_message;
+        let width = columns.len() / rows;
+
+        let mut values = F::zero_vec(columns.len() << log_inv_rate);
+        if width != 0 {
+            let source = RowMajorMatrixView::new(columns, rows);
+            let mut target = RowMajorMatrixViewMut::new(&mut values[..columns.len()], width);
+            source.transpose_into(&mut target);
+        }
+        ntt.ntt_batch(RowMajorMatrix::new(values, width))
+    }
+
+    /// The fused encoder against the two-pass reference, at one shape.
+    fn check_against_the_two_pass<F: ButterflyField>(
+        log_message: usize,
+        width: usize,
+        log_inv_rate: usize,
+        seed: u64,
+    ) {
+        let columns = columns::<F>(log_message, width, seed);
+        let expected =
+            transpose_then_encode(&LchNtt::<F>::default(), &columns, log_message, log_inv_rate);
+        let actual = interleaved_encode_batch::<F>(&columns, log_message, log_inv_rate);
+        assert_eq!(
+            actual, expected,
+            "log_message={log_message} width={width} rate={log_inv_rate}"
+        );
+    }
+
+    #[test]
+    fn the_fused_encoder_matches_the_two_pass_one() {
+        // Rates from none at all, where no coset is copied, up to three added dimensions.
+        for width in WIDTHS {
+            for log_message in 0..=6 {
+                for log_inv_rate in 0..=3 {
+                    check_against_the_two_pass::<BinaryField32>(
+                        log_message,
+                        width,
+                        log_inv_rate,
+                        7,
+                    );
+                    check_against_the_two_pass::<BinaryField128>(
+                        log_message,
+                        width,
+                        log_inv_rate,
+                        11,
+                    );
+                    check_against_the_two_pass::<Ghash128>(log_message, width, log_inv_rate, 13);
+                }
+            }
+        }
+    }
+
+    #[test]
+    fn the_fused_encoder_matches_the_reference_oracle() {
+        // The oracle evaluates the novel basis from its product definition.
+        // So it pins the coset split to that basis, not to another split of the network.
+        for width in [1usize, 3] {
+            for log_message in 0..=4 {
+                for log_inv_rate in 0..=2 {
+                    let columns = columns::<BinaryField16>(log_message, width, 17);
+                    let expected = transpose_then_encode(
+                        &NaiveAdditiveNtt::<BinaryField16>::default(),
+                        &columns,
+                        log_message,
+                        log_inv_rate,
+                    );
+                    let actual = interleaved_encode_batch::<BinaryField16>(
+                        &columns,
+                        log_message,
+                        log_inv_rate,
+                    );
+                    let label = format!("log_message={log_message} width={width}");
+                    assert_eq!(actual, expected, "{label} rate={log_inv_rate}");
+                }
+            }
+        }
+    }
+
+    #[test]
+    fn a_column_reappears_as_the_codeword_column() {
+        // Invariant: column `j` of the codeword is that column's own encoding, on its own.
+        //
+        // Fixture state: four columns of 2^5 values at rate 1/2.
+        //
+        //     columns:  [ c0 | c1 | c2 | c3 ]      each 32 values, contiguous
+        //     codeword:  row i = [ C0[i], C1[i], C2[i], C3[i] ]
+        const LOG_MESSAGE: usize = 5;
+        const WIDTH: usize = 4;
+        let columns = columns::<BinaryField128>(LOG_MESSAGE, WIDTH, 23);
+        let codeword = interleaved_encode_batch::<BinaryField128>(&columns, LOG_MESSAGE, 1);
+
+        for (j, column) in columns
+            .as_chunks::<{ 1 << LOG_MESSAGE }>()
+            .0
+            .iter()
+            .enumerate()
+        {
+            // That column alone, padded and transformed as a single-column message.
+            let mut padded = column.to_vec();
+            padded.resize(padded.len() * 2, BinaryField128::ZERO);
+            let alone =
+                LchNtt::<BinaryField128>::default().ntt_batch(RowMajorMatrix::new(padded, 1));
+
+            for (i, value) in alone.values.iter().enumerate() {
+                assert_eq!(codeword.values[i * WIDTH + j], *value, "column={j} row={i}");
+            }
+        }
+    }
+
+    #[test]
+    #[should_panic = "at least one message column"]
+    fn a_message_with_no_column_is_refused() {
+        // A codeword of no columns has no width to interleave into and no height to read off.
+        // Every later step divides by one of the two, so the shape has to be rejected here.
+        let _ = interleaved_encode_batch::<BinaryField32>(&[], 3, 1);
+    }
+
+    #[test]
+    #[should_panic = "message dimension overflows usize"]
+    fn a_message_dimension_past_the_address_space_is_refused() {
+        // The widest level admits 128 domain dimensions, and a length addresses at most 64.
+        // So a dimension the level allows can still have no row count to describe it.
+        let values = columns::<BinaryField128>(1, 1, 0);
+        let _ = interleaved_encode_batch::<BinaryField128>(&values, 100, 1);
+    }
+
+    #[test]
+    #[should_panic = "whole message columns"]
+    fn a_partial_column_is_refused() {
+        // Nine values do not divide into columns of four, so the interleaving is ill-posed.
+        let values = columns::<BinaryField32>(2, 3, 0);
+        let _ = interleaved_encode_batch::<BinaryField32>(&values[..9], 2, 0);
+    }
+
+    #[test]
+    #[should_panic = "domain exceeds field dimension"]
+    fn a_domain_past_the_level_dimension_is_refused() {
+        // A byte level has sixteen Cantor basis vectors, and this asks for seventeen.
+        let values = columns::<BinaryField16>(15, 1, 0);
+        let _ = interleaved_encode_batch::<BinaryField16>(&values, 15, 2);
+    }
+
+    proptest! {
+        #![proptest_config(ProptestConfig::with_cases(32))]
+
+        /// Random shapes against the two-pass reference, over two representations.
+        #[test]
+        fn random_shapes_match_the_two_pass_encoder(
+            log_message in 0usize..=7,
+            width in 1usize..=5,
+            log_inv_rate in 0usize..=2,
+            seed in any::<u64>(),
+        ) {
+            check_against_the_two_pass::<BinaryField128>(log_message, width, log_inv_rate, seed);
+            check_against_the_two_pass::<Ghash128>(log_message, width, log_inv_rate, seed);
+        }
+    }
+}
```

### binary-dft/src/lch.rs
```diff
@@ -97,6 +97,21 @@ impl<F: ButterflyField> AdditiveNtt<F> for LchNtt<F> {
     fn shifted_intt_batch(&self, mat: RowMajorMatrix<F>, shift: F) -> RowMajorMatrix<F> {
         transform::<F, true>(mat, shift)
     }
+
+    fn ntt_batch_padded(
+        &self,
+        mut mat: RowMajorMatrix<F>,
+        log_inv_rate: usize,
+    ) -> RowMajorMatrix<F> {
+        let width = mat.width();
+        let log_n = log2_strict_usize(mat.height());
+        assert!(log_inv_rate <= log_n, "padding exceeds matrix height");
+        assert!(log_n <= 1 << F::LOG_BITS, "domain exceeds field dimension");
+
+        // The zero tail starts where the message ends, which is what fixes the coset size.
+        transform_cosets::<F>(&mut mat.values, width, log_n - log_inv_rate);
+        mat
+    }
 }
 
 /// Stage twiddle bases and the increments between consecutive block twiddles.
@@ -152,34 +167,42 @@ fn stage_pass<F: ButterflyField, const INVERSE: bool>(
 ) {
     let half = (1 << j) * width;
     let per_task = (BUTTERFLY_GRAIN / half).max(1);
-    values
-        .par_chunks_mut(per_task * (half << 1))
-        .enumerate()
-        .for_each(|(task, group)| {
-            let first = task * per_task;
-            let mut t = twiddles.at(j, first);
-            // Invariant: blocks are visited in ascending index order.
-            // Carrying the twiddle from one block to the next relies on it.
-            for (i, block) in group.chunks_mut(half << 1).enumerate() {
-                if i != 0 {
-                    t += twiddles.step(first + i);
-                }
-                let (lo, hi) = block.split_at_mut(half);
-                let butterfly = |lo: &mut [F], hi: &mut [F]| {
-                    F::butterfly::<INVERSE>(lo, hi, t);
-                };
-                // Pairs are independent across the block.
-                //
-                // So a block wider than the grain is split further, not run on one thread.
-                if half <= BUTTERFLY_GRAIN {
-                    butterfly(lo, hi);
-                } else {
-                    lo.par_chunks_mut(BUTTERFLY_GRAIN)
-                        .zip(hi.par_chunks_mut(BUTTERFLY_GRAIN))
-                        .for_each(|(lo, hi)| butterfly(lo, hi));
-                }
+    let task_len = per_task * (half << 1);
+    let task = |(task, group): (usize, &mut [F])| {
+        let first = task * per_task;
+        let mut t = twiddles.at(j, first);
+        // Invariant: blocks are visited in ascending index order.
+        // Carrying the twiddle from one block to the next relies on it.
+        for (i, block) in group.chunks_mut(half << 1).enumerate() {
+            if i != 0 {
+                t += twiddles.step(first + i);
             }
-        });
+            let (lo, hi) = block.split_at_mut(half);
+            let butterfly = |lo: &mut [F], hi: &mut [F]| {
+                F::butterfly::<INVERSE>(lo, hi, t);
+            };
+            // Pairs are independent across the block.
+            //
+            // So a block wider than the grain is split further, not run on one thread.
+            if half <= BUTTERFLY_GRAIN {
+                butterfly(lo, hi);
+            } else {
+                lo.par_chunks_mut(BUTTERFLY_GRAIN)
+                    .zip(hi.par_chunks_mut(BUTTERFLY_GRAIN))
+                    .for_each(|(lo, hi)| butterfly(lo, hi));
+            }
+        }
+    };
+
+    // A pass covering one task has nothing to spread over the machine.
+    //
+    // Dispatching it anyway costs a thread handoff per stage.
+    // The narrow stages of a short transform pay that once each and get nothing back.
+    if values.len() > task_len {
+        values.par_chunks_mut(task_len).enumerate().for_each(task);
+    } else {
+        values.chunks_mut(task_len).enumerate().for_each(task);
+    }
 }
 
 /// Run the `log_rows` adjacent stages a tile of `2^log_rows` rows is closed under.
@@ -465,16 +488,16 @@ fn group_pass<F: ButterflyField, const INVERSE: bool>(
     }
 }
 
-/// Run every stage of the transform under one tile shape.
+/// Run the `top` narrowest stages of the transform under one tile shape.
 ///
 /// # Algorithm
 ///
 /// Stages below the contiguous tile run inside it. The stages above it are cut into groups of
 /// adjacent stages, each short enough that the rows it is closed under fit one staging tile:
 ///
 /// ```text
-///     stage   ℓ-1 ................ t+2f  t+2f-1 ..... t+f  t+f-1 ..... t  t-1 ... 0
-///             \_____ staged group _____/  \_ staged group _/  \_ group _/  \_ tile _/
+///     stage   top-1 .............. t+2f  t+2f-1 ..... t+f  t+f-1 ..... t  t-1 ... 0
+///             \____ staged group ____/  \_ staged group _/  \_ group _/  \_ tile _/
 /// ```
 ///
 /// The boundaries are counted up from the tile, so a short remainder falls to the top group.
@@ -484,23 +507,26 @@ fn run<F: ButterflyField, const INVERSE: bool>(
     values: &mut [F],
     width: usize,
     log_n: usize,
+    top: usize,
     twiddles: &Twiddles<F>,
     schedule: &Schedule,
 ) {
-    // The schedule is the caller's, so bring it inside what this matrix can hold: a tile is at
-    // most the whole height, and a staged row is a run of matrix rows that must not straddle a
-    // butterfly of the narrowest stage above the tile, which pairs rows `2^tile` apart.
-    let tile = schedule.log_tile_rows.min(log_n);
+    // The schedule is the caller's, so bring it inside what this call can use.
+    //
+    // - A tile is at most the range of stages asked for.
+    // - A staged row is a run of matrix rows.
+    // - That run must not straddle a butterfly of the narrowest stage above the tile.
+    let tile = schedule.log_tile_rows.min(top);
     let slab = schedule.log_slab_rows.min(tile);
     let group = if schedule.log_staged_rows >= MIN_FUSED_STAGES {
         schedule.log_staged_rows
     } else {
         1
     };
-    let groups = (log_n - tile).div_ceil(group);
+    let groups = (top - tile).div_ceil(group);
     let bounds = |g: usize| {
         let low = tile + g * group;
-        (low, (low + group).min(log_n))
+        (low, (low + group).min(top))
     };
 
     if INVERSE {
@@ -522,27 +548,105 @@ fn run<F: ButterflyField, const INVERSE: bool>(
     }
 }
 
-/// Transform a matrix in place, in whichever direction the flag selects.
-fn transform<F: ButterflyField, const INVERSE: bool>(
-    mut mat: RowMajorMatrix<F>,
+/// Run the `top` narrowest stages over a row-major buffer of `width` columns, in place.
+///
+/// Stages are numbered by the distance they pair rows across, so stage zero is the narrowest.
+/// The whole transform is every stage the row count allows.
+///
+/// Asking for fewer than all of them leaves the matrix part-way through the network.
+/// The two directions traverse that network in opposite orders, so they stop at opposite ends:
+///
+/// ```text
+///     forward   stage l-1 ... stage top   then   stage top-1 ... stage 0
+///               \___ the caller's own ___/        \___ this call _____/
+///
+///     inverse   stage 0 ... stage top-1   then   stage top ... stage l-1
+///               \___ this call _______/          \___ the caller's own ___/
+/// ```
+///
+/// So a forward caller has to have run the wider stages already.
+/// An inverse caller still has them ahead of it.
+///
+/// # Panics
+/// Panics if the row count is not a power of two.
+/// Panics if the subspace dimension it calls for exceeds the bit width of the level.
+/// Panics if the stage count exceeds that dimension.
+pub(crate) fn transform_stages<F: ButterflyField, const INVERSE: bool>(
+    values: &mut [F],
+    width: usize,
+    top: usize,
     shift: F,
-) -> RowMajorMatrix<F> {
-    let width = mat.width();
-    let log_n = log2_strict_usize(mat.height());
+) {
+    let log_n = log2_strict_usize(values.len() / width);
+    assert!(log_n <= 1 << F::LOG_BITS, "domain exceeds field dimension");
+    assert!(top <= log_n, "stage count exceeds the domain dimension");
     let twiddles = Twiddles::new(log_n, shift);
 
     // A matrix no larger than a tile is cache-resident for the whole transform, so blocking it
     // would only add bookkeeping to stages already free of memory traffic.
-    if core::mem::size_of_val(mat.values.as_slice()) <= DEEP_TILE_BYTES {
-        for step in 0..log_n {
-            let j = if INVERSE { step } else { log_n - 1 - step };
-            stage_pass::<F, INVERSE>(&mut mat.values, width, j, &twiddles);
+    if core::mem::size_of_val(values) <= DEEP_TILE_BYTES {
+        for step in 0..top {
+            let j = if INVERSE { step } else { top - 1 - step };
+            stage_pass::<F, INVERSE>(values, width, j, &twiddles);
         }
-        return mat;
+        return;
     }
 
     let schedule = Schedule::new::<F>(width, log_n);
-    run::<F, INVERSE>(&mut mat.values, width, log_n, &twiddles, &schedule);
+    run::<F, INVERSE>(values, width, log_n, top, &twiddles, &schedule);
+}
+
+/// Transform a buffer whose leading `2^log_message` rows hold the message and the rest zeros.
+///
+/// # Algorithm
+///
+/// The stages that cross the padding read a zero on the high side of every butterfly:
+///
+/// ```text
+///     (u, 0)  ->  (u + t*0, u + t*0 + 0)  =  (u, u)
+/// ```
+///
+/// They therefore copy the message into each coset of its own subspace and compute nothing.
+/// What is left is one shifted transform per coset, over that coset's own rows:
+///
+/// ```text
+///     coset 0    the message itself, transformed over the subspace
+///     coset c    a contiguous copy of coset 0, then its own shifted transform
+/// ```
+///
+/// A coset's shift is the domain point its first row sits at.
+/// The subspace polynomials are `F_2`-linear, so its blocks read the network's own twiddles.
+///
+/// The copy is what a coset costs instead of one butterfly pass per skipped stage.
+pub(crate) fn transform_cosets<F: ButterflyField>(
+    values: &mut [F],
+    width: usize,
+    log_message: usize,
+) {
+    // One coset is the message's own footprint, so the buffer divides into whole cosets.
+    let len = width << log_message;
+    let (first, rest) = values.split_at_mut(len);
+
+    // Coset `c + 1` starts at domain point `(c + 1) * 2^log_message`, which is its shift.
+    // Transforming it right after the copy finds its rows still in cache.
+    rest.par_chunks_mut(len).enumerate().for_each(|(c, coset)| {
+        coset.copy_from_slice(first);
+        let shift = domain_point::<F>((c + 1) << log_message);
+        transform_stages::<F, false>(coset, width, log_message, shift);
+    });
+
+    // The subspace itself is the coset with no shift, and it is the source every copy read.
+    transform_stages::<F, false>(first, width, log_message, F::ZERO);
+}
+
+/// Transform a matrix in place, in whichever direction the flag selects.
+fn transform<F: ButterflyField, const INVERSE: bool>(
+    mut mat: RowMajorMatrix<F>,
+    shift: F,
+) -> RowMajorMatrix<F> {
+    let width = mat.width();
+    let log_n = log2_strict_usize(mat.height());
+    transform_stages::<F, INVERSE>(&mut mat.values, width, log_n, shift);
     mat
 }
 
@@ -681,9 +785,56 @@ mod tests {
     ) {
         let width = mat.width();
         let log_n = log2_strict_usize(mat.height());
-        for step in 0..log_n {
-            let j = if INVERSE { step } else { log_n - 1 - step };
-            stage_pass::<F, INVERSE>(&mut mat.values, width, j, twiddles);
+        stages_one_at_a_time::<F, INVERSE>(&mut mat.values, width, log_n, twiddles);
+    }
+
+    /// The narrowest `top` stages as plain passes, in the order the direction traverses them.
+    fn stages_one_at_a_time<F: ButterflyField, const INVERSE: bool>(
+        values: &mut [F],
+        width: usize,
+        top: usize,
+        twiddles: &Twiddles<F>,
+    ) {
+        for step in 0..top {
+            let j = if INVERSE { step } else { top - 1 - step };
+            stage_pass::<F, INVERSE>(values, width, j, twiddles);
+        }
+    }
+
+    /// Every stage range of one shape, blocked against the same stages run one pass at a time.
+    fn check_every_stage_range_agrees<F: ButterflyField>(
+        log_n: usize,
+        width: usize,
+        schedule: &Schedule,
+    ) {
+        let coeffs = matrix::<F>(log_n, width, 3);
+        for shift_bits in SHIFTS {
+            let shift = sample::<F>(shift_bits);
+            let twiddles = Twiddles::new(log_n, shift);
+
+            for top in 0..=log_n {
+                let label = format!("log_n={log_n} width={width} shift={shift_bits:#x} top={top}");
+
+                // Forward: the range is the tail of the network, so it runs widest stage first.
+                let mut expected = coeffs.clone();
+                stages_one_at_a_time::<F, false>(&mut expected.values, width, top, &twiddles);
+
+                let mut blocked = coeffs.clone();
+                run::<F, false>(&mut blocked.values, width, log_n, top, &twiddles, schedule);
+                assert_eq!(blocked, expected, "forward {label}");
+
+                // The same range undone puts the coefficients back, whatever the blocking.
+                run::<F, true>(&mut blocked.values, width, log_n, top, &twiddles, schedule);
+                assert_eq!(blocked, coeffs, "round trip {label}");
+
+                // Inverse: the range is the head of the network, so it runs narrowest first.
+                let mut expected = coeffs.clone();
+                stages_one_at_a_time::<F, true>(&mut expected.values, width, top, &twiddles);
+
+                let mut blocked = coeffs.clone();
+                run::<F, true>(&mut blocked.values, width, log_n, top, &twiddles, schedule);
+                assert_eq!(blocked, expected, "inverse {label}");
+            }
         }
     }
 
@@ -700,15 +851,29 @@ mod tests {
             stage_by_stage::<F, false>(&mut expected, &twiddles);
 
             let mut blocked = coeffs.clone();
-            run::<F, false>(&mut blocked.values, width, log_n, &twiddles, schedule);
+            run::<F, false>(
+                &mut blocked.values,
+                width,
+                log_n,
+                log_n,
+                &twiddles,
+                schedule,
+            );
             assert_eq!(blocked, expected, "forward {label}");
 
             // Inverse: same comparison with the stage order reversed.
             let mut expected = coeffs.clone();
             stage_by_stage::<F, true>(&mut expected, &twiddles);
 
             let mut blocked = coeffs.clone();
-            run::<F, true>(&mut blocked.values, width, log_n, &twiddles, schedule);
+            run::<F, true>(
+                &mut blocked.values,
+                width,
+                log_n,
+                log_n,
+                &twiddles,
+                schedule,
+            );
             assert_eq!(blocked, expected, "inverse {label}");
         }
     }
@@ -805,12 +970,26 @@ mod tests {
                 format!("log_n={log_n} width={width} shift={shift_bits:#x} workers={workers}");
 
             let mut blocked = coeffs.clone();
-            run::<F, false>(&mut blocked.values, width, log_n, &twiddles, &schedule);
+            run::<F, false>(
+                &mut blocked.values,
+                width,
+                log_n,
+                log_n,
+                &twiddles,
+                &schedule,
+            );
             assert_eq!(blocked, walked, "ntt {label}");
 
             // Undoing the walk's own codeword holds the inverse schedule to the same twiddles.
             let mut blocked = walked.clone();
-            run::<F, true>(&mut blocked.values, width, log_n, &twiddles, &schedule);
+            run::<F, true>(
+                &mut blocked.values,
+                width,
+                log_n,
+                log_n,
+                &twiddles,
+                &schedule,
+            );
             assert_eq!(blocked, coeffs, "intt {label}");
         }
     }
@@ -970,6 +1149,28 @@ mod tests {
         }
     }
 
+    proptest! {
+        #![proptest_config(ProptestConfig::with_cases(32))]
+
+        /// Random padded shapes, against running the skipped layers as ordinary butterflies.
+        #[test]
+        fn random_padded_shapes_match_the_full_transform(
+            log_message in 0usize..=7,
+            width in 1usize..=5,
+            log_inv_rate in 0usize..=3,
+            seed in any::<u64>(),
+        ) {
+            let message = matrix::<BinaryField128>(log_message, width, seed);
+            let mut padded = message.values;
+            padded.resize(padded.len() << log_inv_rate, BinaryField128::ZERO);
+            let padded = RowMajorMatrix::new(padded, width);
+
+            let ntt = LchNtt::<BinaryField128>::default();
+            let expected = ntt.ntt_batch(padded.clone());
+            prop_assert_eq!(ntt.ntt_batch_padded(padded, log_inv_rate), expected);
+        }
+    }
+
     #[test]
     fn lch_matches_a_twiddle_walk_across_several_tasks() {
         // Fixture state: a height whose stages take more than one butterfly task, so a task
@@ -1075,6 +1276,131 @@ mod tests {
         }
     }
 
+    #[test]
+    fn a_partial_stage_range_matches_the_plain_passes() {
+        // Invariant: a schedule asked for part of the network runs those stages and no others.
+        //
+        // The subfield split is the only caller that stops short, and it stops forward.
+        //
+        // Below the staging worker count no partial range reaches a fused group at all.
+        // So the shapes below are named rather than read off the machine.
+        //
+        // Fixture state: rows per contiguous tile, staged rows per group, rows per staged row.
+        let shape = |tile: usize, staged: usize, slab: usize| Schedule {
+            log_tile_rows: tile,
+            log_staged_rows: staged,
+            log_slab_rows: slab,
+        };
+
+        for width in [1usize, 3, 16] {
+            // A three-stage tile with two-stage groups above it.
+            // The sweep then ends inside the tile, at its edge, inside a group, and past one.
+            check_every_stage_range_agrees::<BinaryField128>(8, width, &shape(3, 2, 0));
+
+            // Groups deeper than the stages left over them, so the top group is always clipped.
+            check_every_stage_range_agrees::<BinaryField128>(7, width, &shape(2, 4, 0));
+
+            // No tile at all, so every stage of the range belongs to a group.
+            check_every_stage_range_agrees::<BinaryField128>(6, width, &shape(0, 3, 0));
+
+            // Staged rows holding a run of matrix rows each, as narrow rows call for.
+            check_every_stage_range_agrees::<BinaryField32>(8, width, &shape(4, 3, 2));
+        }
+
+        // The production shapes at a named worker count, where a cache budget does the grouping.
+        for workers in [1usize, 32] {
+            let schedule = Schedule::for_workers::<BinaryField128>(16, 11, workers);
+            assert!(schedule.log_tile_rows < 11, "no group above the tile");
+            check_every_stage_range_agrees::<BinaryField128>(11, 16, &schedule);
+        }
+    }
+
+    /// One padded shape: skipping the layers that cross the padding against running them.
+    fn check_the_padded_transform_agrees<F: ButterflyField>(
+        log_message: usize,
+        width: usize,
+        log_inv_rate: usize,
+    ) {
+        let message = matrix::<F>(log_message, width, 59);
+
+        // The reference pads the coefficients and transforms every layer of the result.
+        let mut padded = message.values;
+        padded.resize(padded.len() << log_inv_rate, F::ZERO);
+        let padded = RowMajorMatrix::new(padded, width);
+
+        let ntt = LchNtt::<F>::default();
+        let expected = ntt.ntt_batch(padded.clone());
+        assert_eq!(
+            ntt.ntt_batch_padded(padded, log_inv_rate),
+            expected,
+            "log_message={log_message} width={width} rate={log_inv_rate}"
+        );
+    }
+
+    #[test]
+    fn the_padded_transform_matches_the_full_one() {
+        // Invariant: a layer whose high side is all zero copies, so skipping it changes nothing.
+        //
+        //     rate 0   one coset, and the skip has no layer to skip
+        //     rate 3   eight cosets, seven of them a copy of the first
+        for width in WIDTHS {
+            for log_message in 0..=5 {
+                for log_inv_rate in 0..=3 {
+                    check_the_padded_transform_agrees::<BinaryField32>(
+                        log_message,
+                        width,
+                        log_inv_rate,
+                    );
+                    check_the_padded_transform_agrees::<BinaryField128>(
+                        log_message,
+                        width,
+                        log_inv_rate,
+                    );
+                    check_the_padded_transform_agrees::<Ghash128>(log_message, width, log_inv_rate);
+                }
+            }
+        }
+    }
+
+    #[test]
+    fn the_padded_transform_matches_the_reference_oracle() {
+        // The oracle evaluates the novel basis straight from its product definition.
+        // So it pins the coset split to that basis, not to another split of the same network.
+        for width in [1usize, 3] {
+            for log_message in 0..=4 {
+                for log_inv_rate in 0..=2 {
+                    let message = matrix::<BinaryField64>(log_message, width, 61);
+                    let mut padded = message.values;
+                    padded.resize(padded.len() << log_inv_rate, BinaryField64::ZERO);
+                    let padded = RowMajorMatrix::new(padded, width);
+
+                    let expected =
+                        NaiveAdditiveNtt::<BinaryField64>::default().ntt_batch(padded.clone());
+                    let actual =
+                        LchNtt::<BinaryField64>::default().ntt_batch_padded(padded, log_inv_rate);
+                    let label = format!("log_message={log_message} width={width}");
+                    assert_eq!(actual, expected, "{label} rate={log_inv_rate}");
+                }
+            }
+        }
+    }
+
+    #[test]
+    #[should_panic = "padding exceeds matrix height"]
+    fn the_padded_transform_rejects_padding_past_the_height() {
+        // A 2^2-row matrix cannot have been padded from a fraction of a row.
+        let mat = matrix::<BinaryField32>(2, 4, 0);
+        let _ = LchNtt::<BinaryField32>::default().ntt_batch_padded(mat, 3);
+    }
+
+    #[test]
+    #[should_panic = "domain exceeds field dimension"]
+    fn the_padded_transform_rejects_a_domain_past_the_field_dimension() {
+        // A 2^9-row domain asks for nine Cantor basis vectors, and a byte level has eight.
+        let mat = matrix::<BinaryField8>(9, 1, 0);
+        let _ = LchNtt::<BinaryField8>::default().ntt_batch_padded(mat, 1);
+    }
+
     #[test]
     fn the_contiguous_tile_leaves_one_for_every_worker() {
         // Invariant: a contiguous tile is a task, so the schedule keeps one per worker wherever
```

### binary-dft/src/lib.rs
```diff
@@ -21,6 +21,7 @@ mod affine;
 mod butterfly;
 mod domain;
 mod encoder;
+mod interleaved;
 #[cfg(any(
     test,
     all(
@@ -34,6 +35,7 @@ mod lanes;
 mod lch;
 mod naive;
 mod poly;
+mod subfield;
 #[cfg(test)]
 pub(crate) mod test_util;
 mod tower;
@@ -42,7 +44,9 @@ mod traits;
 pub use butterfly::ButterflyField;
 pub use domain::*;
 pub use encoder::*;
+pub use interleaved::*;
 pub use lch::*;
 pub use naive::*;
 pub use poly::*;
+pub use subfield::*;
 pub use traits::*;
```

### binary-dft/src/subfield.rs
```diff
@@ -0,0 +1,405 @@
+//! The additive NTT of a message whose entries lie in a byte-aligned tower subfield.
+
+use alloc::vec::Vec;
+
+use p3_binary_field::TowerLevel;
+use p3_matrix::Matrix;
+use p3_matrix::dense::RowMajorMatrix;
+use p3_maybe_rayon::prelude::*;
+use p3_util::log2_strict_usize;
+
+use crate::butterfly::ButterflyField;
+use crate::encoder::padded_message_len;
+use crate::lch::transform_stages;
+
+/// Number of widest butterfly layers a subfield of `2^log_bits` bits is closed under.
+///
+/// - Layer `j` of a height-`2^l` unshifted transform scales by a point of `span(v_1..v_{l-1-j})`.
+/// - A subfield of `b` bits holds the first `b` basis vectors and nothing above them.
+/// - So the layer stays inside it exactly while `l - 1 - j < b`, the top `b` layers.
+const fn closed_layers(log_bits: usize) -> usize {
+    1 << log_bits
+}
+
+/// Bytes a message must carry before running its closed layers narrow pays.
+///
+/// Those layers are a transform of the message alone, at a fraction of the alphabet's width.
+///
+/// A short one is a few microseconds of work behind one thread handoff per layer.
+/// The narrow element size does not save enough to cover those handoffs.
+///
+/// A hundred and twenty-eight kibibytes is the smallest message measured to come out ahead.
+const NARROW_MESSAGE_BYTES: usize = 128 * 1024;
+
+/// Bytes the codeword must carry before the widening pass is worth handing to the machine.
+///
+/// The pass is one read and one write per entry, with no arithmetic between them.
+/// It is therefore limited by memory rather than by cores.
+///
+/// Four mebibytes is the smallest codeword measured to gain from being spread.
+const PARALLEL_WIDEN_BYTES: usize = 4 * 1024 * 1024;
+
+/// Embed every entry into the wider level, in one pass over the data.
+fn widen<S: TowerLevel, F: TowerLevel + From<S>>(values: &[S]) -> Vec<F> {
+    if size_of::<F>() * values.len() < PARALLEL_WIDEN_BYTES {
+        return values.iter().map(|&value| F::from(value)).collect();
+    }
+    values.par_iter().map(|&value| F::from(value)).collect()
+}
+
+/// Evaluate a subfield message with the widest `head` layers run at the narrow element width.
+///
+/// # Algorithm
+///
+/// Write `l` for the domain dimension and `h` for the layers to run narrow.
+/// A row index splits into its top `h` bits and its bottom `l - h` bits:
+///
+/// ```text
+///     row = a * 2^(l-h) + b ,     a < 2^h ,  b < 2^(l-h)
+/// ```
+///
+/// The top `h` layers pair rows that differ in `a` alone, so they leave `b` untouched:
+///
+/// ```text
+///     phase 1   the buffer read as 2^h rows of 2^(l-h) * width columns, transformed whole
+///     phase 2   the remaining l - h layers of the transform the buffer really is
+/// ```
+///
+/// Both phases are unshifted and share block indices, so they agree twiddle for twiddle.
+///
+/// # Panics
+///
+/// Panics if `head` exceeds the layers the subfield is closed under.
+/// Phase 1 would then ask the subfield for a basis vector above its own.
+fn split_ntt_batch<S, F>(mut mat: RowMajorMatrix<S>, head: usize) -> RowMajorMatrix<F>
+where
+    S: ButterflyField,
+    F: ButterflyField + From<S>,
+{
+    let width = mat.width();
+    let log_n = log2_strict_usize(mat.height());
+    assert!(log_n <= 1 << F::LOG_BITS, "domain exceeds field dimension");
+    assert!(
+        head <= closed_layers(S::LOG_BITS).min(log_n),
+        "the subfield is not closed under that many layers"
+    );
+    let low = log_n - head;
+
+    // Phase 1: every layer of a shorter, wider reading of the same buffer.
+    transform_stages::<S, false>(&mut mat.values, width << low, head, S::ZERO);
+
+    let mut values = widen::<S, F>(&mat.values);
+
+    // Phase 2: the layers the subfield is not closed under, at the alphabet's own width.
+    transform_stages::<F, false>(&mut values, width, low, F::ZERO);
+
+    RowMajorMatrix::new(values, width)
+}
+
+/// Evaluate each column of a subfield message on the subspace of the wider level.
+///
+/// Widening the message first pays the wide element size at every layer.
+/// The widest layers do not need it: their twiddles map the subfield into itself.
+///
+/// The layers left over run the tower transform, not whichever backend is fastest wide.
+///
+/// # Panics
+///
+/// Panics if the height is not a power of two.
+/// Panics if the domain dimension exceeds the bit width of the wider level.
+#[must_use]
+pub fn subfield_ntt_batch<S, F>(mat: RowMajorMatrix<S>) -> RowMajorMatrix<F>
+where
+    S: ButterflyField,
+    F: ButterflyField + From<S>,
+{
+    let log_n = log2_strict_usize(mat.height());
+
+    // A message too small to pay for the narrow phase runs no layer narrow.
+    // What is left is the ordinary transform of the widened message.
+    let head = if size_of::<S>() * mat.values.len() >= NARROW_MESSAGE_BYTES {
+        closed_layers(S::LOG_BITS).min(log_n)
+    } else {
+        0
+    };
+    split_ntt_batch(mat, head)
+}
+
+/// Reed–Solomon encode a subfield message over the additive NTT domain.
+///
+/// The message holds the low-index novel-basis coefficients of each column.
+/// The codeword is their evaluation on the subspace `log_inv_rate` dimensions above.
+///
+/// Zero lies in the subfield, so the padding that extends the domain is paid narrow too.
+///
+/// # Panics
+///
+/// Panics under the same conditions as the plain transform.
+/// Panics if the codeword length overflows the address space.
+#[must_use]
+pub fn subfield_encode_batch<S, F>(
+    mut message: RowMajorMatrix<S>,
+    log_inv_rate: usize,
+) -> RowMajorMatrix<F>
+where
+    S: ButterflyField,
+    F: ButterflyField + From<S>,
+{
+    let padded_len = padded_message_len(message.values.len(), log_inv_rate);
+    let _ = log2_strict_usize(message.height());
+
+    message.values.resize(padded_len, S::ZERO);
+    subfield_ntt_batch(message)
+}
+
+#[cfg(test)]
+mod tests {
+    use alloc::format;
+
+    use p3_binary_field::{
+        BinaryField8, BinaryField16, BinaryField32, BinaryField64, BinaryField128, Gf2, TowerLevel,
+    };
+    use p3_field::PrimeCharacteristicRing;
+    use p3_matrix::dense::RowMajorMatrix;
+    use proptest::prelude::*;
+
+    use super::{closed_layers, split_ntt_batch, subfield_encode_batch, subfield_ntt_batch, widen};
+    use crate::butterfly::ButterflyField;
+    use crate::domain::{domain_point, subspace_polynomial};
+    use crate::lch::LchNtt;
+    use crate::naive::NaiveAdditiveNtt;
+    use crate::traits::AdditiveNtt;
+
+    /// Widths covering a single column, an odd row, and a row of several elements.
+    const WIDTHS: [usize; 4] = [1, 3, 4, 16];
+
+    /// A matrix of subfield entries that depend on both the position and the seed.
+    fn matrix<S: TowerLevel>(log_n: usize, width: usize, seed: u64) -> RowMajorMatrix<S> {
+        RowMajorMatrix::new(
+            (0..(width << log_n))
+                .map(|i| {
+                    let bits = seed
+                        .wrapping_mul(0x9e37_79b9_7f4a_7c15)
+                        .wrapping_add(i as u64 + 1)
+                        .wrapping_mul(0xbf58_476d_1ce4_e5b9);
+                    S::from_le_byte_iter(bits.to_le_bytes().into_iter().cycle())
+                })
+                .collect(),
+            width,
+        )
+    }
+
+    /// Every split depth against the unspecialised transform on the widened message.
+    fn check_against_the_wide_transform<S, F>(log_n: usize, width: usize, seed: u64)
+    where
+        S: ButterflyField,
+        F: ButterflyField + From<S>,
+    {
+        let message = matrix::<S>(log_n, width, seed);
+
+        // The reference widens first and runs the ordinary transform.
+        let wide = RowMajorMatrix::new(widen::<S, F>(&message.values), width);
+        let expected = LchNtt::<F>::default().ntt_batch(wide);
+
+        for head in 0..=closed_layers(S::LOG_BITS).min(log_n) {
+            let label = format!("log_n={log_n} width={width} seed={seed} head={head}");
+            assert_eq!(
+                split_ntt_batch::<S, F>(message.clone(), head),
+                expected,
+                "{label}"
+            );
+        }
+
+        // And the entry point itself, at whichever depth its own size rule picks.
+        assert_eq!(subfield_ntt_batch::<S, F>(message), expected);
+    }
+
+    #[test]
+    fn a_byte_message_transforms_like_the_widened_one() {
+        // Heights on both sides of the eight layers a byte subfield is closed under.
+        for width in WIDTHS {
+            for log_n in 0..=10 {
+                check_against_the_wide_transform::<BinaryField8, BinaryField128>(log_n, width, 7);
+                check_against_the_wide_transform::<BinaryField8, BinaryField64>(log_n, width, 11);
+                check_against_the_wide_transform::<BinaryField8, BinaryField32>(log_n, width, 13);
+            }
+        }
+    }
+
+    #[test]
+    fn a_bit_message_transforms_like_the_widened_one() {
+        // A single-bit subfield is closed under one layer, the narrowest split there is.
+        for width in WIDTHS {
+            for log_n in 0..=8 {
+                check_against_the_wide_transform::<Gf2, BinaryField128>(log_n, width, 17);
+            }
+        }
+    }
+
+    #[test]
+    fn a_two_and_four_byte_message_transforms_like_the_widened_one() {
+        // Sixteen and thirty-two closed layers, so the heights here are all inside the head.
+        for width in WIDTHS {
+            for log_n in 0..=10 {
+                check_against_the_wide_transform::<BinaryField16, BinaryField128>(log_n, width, 19);
+                check_against_the_wide_transform::<BinaryField32, BinaryField128>(log_n, width, 23);
+            }
+        }
+    }
+
+    #[test]
+    fn the_widest_subfield_is_the_alphabet_itself() {
+        // Invariant: with nothing left over the head, phase 2 has no layers at all.
+        for log_n in 0..=6 {
+            check_against_the_wide_transform::<BinaryField64, BinaryField64>(log_n, 3, 29);
+        }
+    }
+
+    #[test]
+    #[should_panic = "the subfield is not closed under that many layers"]
+    fn a_split_deeper_than_the_subfield_allows_is_refused() {
+        // A byte subfield is closed under eight layers.
+        // A ninth needs a basis vector it does not have, and would compute another map.
+        let message = matrix::<BinaryField8>(10, 1, 0);
+        let _ = split_ntt_batch::<BinaryField8, BinaryField128>(message, 9);
+    }
+
+    #[test]
+    fn a_message_below_the_narrow_threshold_runs_no_narrow_layer() {
+        // Invariant: the size rule is what decides, and it decides the same way twice.
+        //
+        // Fixture state: 2^6 rows of one byte column is 64 bytes, far below the threshold.
+        let message = matrix::<BinaryField8>(6, 1, 41);
+        assert_eq!(
+            subfield_ntt_batch::<BinaryField8, BinaryField128>(message.clone()),
+            split_ntt_batch::<BinaryField8, BinaryField128>(message, 0)
+        );
+    }
+
+    /// The deepest split of one shape, against the novel basis read from its product definition.
+    fn check_against_the_oracle(log_n: usize, width: usize) {
+        let message = matrix::<BinaryField8>(log_n, width, 31);
+        let wide = RowMajorMatrix::new(widen::<_, BinaryField128>(&message.values), width);
+        let expected = NaiveAdditiveNtt::default().ntt_batch(wide);
+
+        // The deepest split the height allows, which is where phase 1 does the most.
+        let head = closed_layers(BinaryField8::LOG_BITS).min(log_n);
+        assert_eq!(
+            split_ntt_batch::<_, BinaryField128>(message, head),
+            expected,
+            "log_n={log_n} width={width}"
+        );
+    }
+
+    #[test]
+    fn a_byte_message_matches_the_reference_oracle() {
+        // The oracle evaluates the novel basis straight from its product definition.
+        // So it pins the split to that basis, not to another split of the same network.
+        for width in [1usize, 3] {
+            for log_n in 0..=6 {
+                check_against_the_oracle(log_n, width);
+            }
+        }
+    }
+
+    #[test]
+    fn a_byte_message_past_the_closed_layers_matches_the_reference_oracle() {
+        // Invariant: both phases are pinned to the definition, not the narrow phase alone.
+        // A byte subfield is closed under eight layers, so phase 2 is empty below 2^9.
+        //
+        //     log_n = 9   head = 8, phase 2 runs one layer at the wide width
+        //     log_n = 10  head = 8, phase 2 runs two of them
+        for log_n in [9usize, 10] {
+            check_against_the_oracle(log_n, 1);
+        }
+    }
+
+    #[test]
+    fn the_closed_layer_count_is_the_subfield_bit_width() {
+        // Fixture state: the layer count a level's own basis vectors allow.
+        //
+        // - one bit gives one layer
+        // - eight bits give eight layers
+        // - a hundred and twenty-eight bits give that many
+        assert_eq!(closed_layers(Gf2::LOG_BITS), 1);
+        assert_eq!(closed_layers(BinaryField8::LOG_BITS), 8);
+        assert_eq!(closed_layers(BinaryField128::LOG_BITS), 128);
+    }
+
+    #[test]
+    fn the_closed_layers_really_keep_their_twiddles_in_the_subfield() {
+        // Invariant: every twiddle of the top `h` layers lies in the subfield.
+        // Checked against the subspace-polynomial definition, not against the split.
+        const LOG_N: usize = 12;
+        let head = closed_layers(BinaryField8::LOG_BITS);
+
+        for layer in LOG_N - head..LOG_N {
+            // Layer `layer` pairs rows `2^layer` apart, so it has this many blocks.
+            for block in 0..1usize << (LOG_N - 1 - layer) {
+                let t = subspace_polynomial::<BinaryField128>(layer, BinaryField128::ZERO)
+                    + domain_point::<BinaryField128>(block << 1);
+                assert!(
+                    t.to_repr() <= u128::from(u8::MAX),
+                    "layer={layer} block={block}"
+                );
+            }
+        }
+
+        // And the layer just below is where that stops, for this subfield at this height.
+        let t = domain_point::<BinaryField128>(1 << (head - 1) << 1);
+        assert!(
+            t.to_repr() > u128::from(u8::MAX),
+            "the head could be one layer deeper"
+        );
+    }
+
+    #[test]
+    fn encoding_pads_the_coefficients_at_the_narrow_width() {
+        // Fixture state: a 2^4-row message at rate 1/4, so the codeword has 2^6 rows.
+        for width in WIDTHS {
+            for log_inv_rate in 0..=3 {
+                let message = matrix::<BinaryField8>(4, width, 37);
+
+                // The reference pads at the wide width and transforms the whole thing.
+                let mut padded = widen::<_, BinaryField128>(&message.values);
+                padded.resize(padded.len() << log_inv_rate, BinaryField128::ZERO);
+                let expected = LchNtt::<BinaryField128>::default()
+                    .ntt_batch(RowMajorMatrix::new(padded, width));
+
+                let actual = subfield_encode_batch::<_, BinaryField128>(message, log_inv_rate);
+                assert_eq!(actual, expected, "width={width} rate={log_inv_rate}");
+            }
+        }
+    }
+
+    #[test]
+    #[should_panic = "codeword length overflows usize"]
+    fn encoding_rejects_a_codeword_length_past_the_address_space() {
+        let message = matrix::<BinaryField8>(1, 1, 0);
+        let _ = subfield_encode_batch::<_, BinaryField128>(message, usize::BITS as usize - 1);
+    }
+
+    #[test]
+    #[should_panic = "domain exceeds field dimension"]
+    fn a_domain_past_the_alphabet_dimension_is_refused() {
+        // A 2^9-row domain asks for nine Cantor basis vectors, and a byte level has eight.
+        let message = matrix::<BinaryField8>(9, 1, 0);
+        let _ = subfield_ntt_batch::<BinaryField8, BinaryField8>(message);
+    }
+
+    proptest! {
+        #![proptest_config(ProptestConfig::with_cases(32))]
+
+        /// Random heights and widths, across the three interesting subfield widths.
+        #[test]
+        fn random_subfield_messages_transform_like_the_widened_ones(
+            log_n in 0usize..=9,
+            width in 1usize..=5,
+            seed in any::<u64>(),
+        ) {
+            check_against_the_wide_transform::<Gf2, BinaryField128>(log_n, width, seed);
+            check_against_the_wide_transform::<BinaryField8, BinaryField128>(log_n, width, seed);
+            check_against_the_wide_transform::<BinaryField16, BinaryField64>(log_n, width, seed);
+        }
+    }
+}
```

### binary-field/benches/arithmetic.rs
```diff
@@ -7,8 +7,12 @@
 //! same code with the fast path turned off.
 
 use std::hint::black_box;
+use std::ops::Mul;
 
-use criterion::{BatchSize, Criterion, criterion_group, criterion_main};
+use criterion::measurement::Measurement;
+use criterion::{
+    BatchSize, BenchmarkGroup, BenchmarkId, Criterion, criterion_group, criterion_main,
+};
 use p3_binary_field::{
     BinaryField8, BinaryField16, BinaryField32, BinaryField64, BinaryField128, Ghash128,
     LinearizedPoly8b, PackedRijndael8b, Poly64, Poly192, Rijndael8b, TowerLevel, poly_basis,
@@ -208,6 +212,54 @@ fn bench_mul_alpha(c: &mut Criterion) {
     group.finish();
 }
 
+/// Products of a wide element by a narrow one, at one pair of byte-aligned levels.
+///
+/// The narrow operand is fixed and the wide ones vary, which is the shape a twiddle takes.
+/// The accumulator is a bitwise exclusive-or, so the products are free to overlap.
+fn subfield_mul_arm<U, L, M: Measurement>(
+    group: &mut BenchmarkGroup<'_, M>,
+    upper: &str,
+    lower: &str,
+) where
+    U: TowerLevel + Mul<L, Output = U>,
+    L: TowerLevel,
+    StandardUniform: Distribution<U> + Distribution<L>,
+{
+    let mut rng = SmallRng::seed_from_u64(1);
+    let wide: Vec<U> = (0..REPS).map(|_| rng.random()).collect();
+    let narrow: L = rng.random();
+
+    group.bench_function(BenchmarkId::new(upper, lower), |b| {
+        b.iter(|| {
+            black_box(&wide)
+                .iter()
+                .fold(U::ZERO, |acc, &y| acc + y * black_box(narrow))
+        });
+    });
+}
+
+/// A product of a wide element by an element of a level below it, at every such pair.
+///
+/// One route expands the wide operand into coordinates over the narrow level.
+/// The other embeds the narrow operand and takes the wide level's own product.
+///
+/// Coordinate count falls as the narrow level widens, and each coordinate product costs more.
+/// These arms are what fixes where the two routes cross on a given host.
+fn bench_subfield_mul(c: &mut Criterion) {
+    let mut group = c.benchmark_group("subfield_mul");
+
+    subfield_mul_arm::<BinaryField64, BinaryField8, _>(&mut group, "64", "8");
+    subfield_mul_arm::<BinaryField64, BinaryField16, _>(&mut group, "64", "16");
+    subfield_mul_arm::<BinaryField64, BinaryField32, _>(&mut group, "64", "32");
+
+    subfield_mul_arm::<BinaryField128, BinaryField8, _>(&mut group, "128", "8");
+    subfield_mul_arm::<BinaryField128, BinaryField16, _>(&mut group, "128", "16");
+    subfield_mul_arm::<BinaryField128, BinaryField32, _>(&mut group, "128", "32");
+    subfield_mul_arm::<BinaryField128, BinaryField64, _>(&mut group, "128", "64");
+
+    group.finish();
+}
+
 /// Elements flattened by one iteration of [`bench_flatten_to_base`].
 const FLATTEN_LEN: usize = 1 << 20;
 
@@ -1118,6 +1170,7 @@ criterion_group!(
     bench_square,
     bench_inverse,
     bench_mul_alpha,
+    bench_subfield_mul,
     bench_flatten_to_base,
     bench_representation_mul_latency,
     bench_representation_mul_throughput,
```

### binary-field/src/extension.rs
```diff
@@ -45,10 +45,13 @@ macro_rules! binary_tower_extension {
 
             #[inline]
             fn mul(self, rhs: $lower) -> Self {
-                // These intermediate subfields need more coefficient products than the
-                // native full-width backend; the byte and quadratic subfields do not.
+                // Coordinate expansion costs one narrow product per coordinate.
+                // A carryless multiply makes the wide product cheaper than that from here up.
+                //
+                // The byte level stays on the expansion: its products are table lookups.
+                // The half-width level stays on it too: two products still beat the wide one.
                 if crate::clmul::HAS_HARDWARE_CLMUL
-                    && <$upper>::BITS == 128
+                    && matches!(<$upper>::BITS, 64 | 128)
                     && matches!(<$lower>::BITS, 16 | 32)
                 {
                     return self * Self::from(rhs);
```

### sumcheck/Cargo.toml
```diff
@@ -54,5 +54,9 @@ harness = false
 name = "ring_switch"
 harness = false
 
+[[bench]]
+name = "univariate_skip"
+harness = false
+
 [lints]
 workspace = true
```

### sumcheck/benches/univariate_skip.rs
```diff
@@ -0,0 +1,114 @@
+//! Criterion benches for the univariate-skip low-degree extension.
+//!
+//! - One row on its own, which is the narrowest call there is.
+//! - A block of rows, which is what a caller holding the whole witness makes.
+//! - The streaming round message, which is what a prover runs.
+
+use criterion::{BenchmarkId, Criterion, Throughput, criterion_group, criterion_main};
+use p3_binary_field::{BinaryField8, BinaryField16, BinaryField128, TowerLevel};
+use p3_sumcheck::univariate_skip::{CompressedLde, Conjunction, SkipDomain, SkipRound};
+use rand::rngs::SmallRng;
+use rand::{RngExt, SeedableRng};
+
+/// Rows one batched measurement extends, a whole column of a modest trace.
+const BATCH_ROWS: usize = 1 << 14;
+
+/// Rows one streamed round message covers, tall enough to leave every cache.
+const STREAM_ROWS: usize = 1 << 16;
+
+/// The domain shapes the sweep covers.
+///
+/// ```text
+///     k = 6, d = 2    the product form a zerocheck of R1CS shape runs
+///     k = 6, d = 4    two extra dimensions, so three times as many points per row
+///     k = 7, d = 2    twice the row bytes and twice the points
+/// ```
+const SHAPES: [(usize, usize); 3] = [(6, 2), (6, 4), (7, 2)];
+
+/// One level's extension, at every shape of the sweep.
+fn arm<F: TowerLevel + Send + Sync>(c: &mut Criterion, name: &str) {
+    let mut group = c.benchmark_group(format!("skip_lde/{name}"));
+    let mut rng = SmallRng::seed_from_u64(9);
+
+    for (log_size, degree) in SHAPES {
+        let domain = SkipDomain::<F>::for_degree(log_size, degree).unwrap();
+        let lde = CompressedLde::new(&domain).unwrap();
+        let parameter = format!("k{log_size}/d{degree}");
+
+        // One row, which is the call the streaming prover makes.
+        let row = (0..lde.num_chunks())
+            .map(|_| rng.random::<u8>())
+            .collect::<Vec<_>>();
+        let mut out = F::zero_vec(lde.num_transmitted());
+
+        // Throughput counts the values produced, so shapes of different width compare.
+        group.throughput(Throughput::Elements(lde.num_transmitted() as u64));
+        group.bench_function(BenchmarkId::new("row", &parameter), |b| {
+            b.iter(|| lde.extend(&row, &mut out));
+        });
+
+        // A block of rows, which is the call a caller holding the whole witness makes.
+        let rows = (0..BATCH_ROWS * lde.num_chunks())
+            .map(|_| rng.random::<u8>())
+            .collect::<Vec<_>>();
+        let mut out = F::zero_vec(BATCH_ROWS * lde.num_transmitted());
+
+        group.throughput(Throughput::Elements(
+            (BATCH_ROWS * lde.num_transmitted()) as u64,
+        ));
+        group.bench_function(BenchmarkId::new("batch", &parameter), |b| {
+            b.iter(|| lde.extend_batch(&rows, &mut out));
+        });
+    }
+    group.finish();
+}
+
+/// The two levels a skipped round runs over, whose tables differ by a factor of two.
+fn bench_skip_lde(c: &mut Criterion) {
+    arm::<BinaryField8>(c, "8");
+    arm::<BinaryField16>(c, "16");
+}
+
+/// The whole round message, formed straight from packed witness rows.
+///
+/// This is the prover's own call.
+/// It shows what the extension is worth against the weighted composition around it.
+fn bench_stream_message(c: &mut Criterion) {
+    let mut group = c.benchmark_group("skip_stream");
+    group.sample_size(20);
+
+    let mut rng = SmallRng::seed_from_u64(11);
+    for (log_size, degree) in SHAPES {
+        // A conjunction is the three-operand product form a bit-valued rank-one system takes.
+        let round = SkipRound::<BinaryField8>::new(log_size, degree).unwrap();
+        let row_bytes = round.row_bytes();
+
+        // One packed witness per operand, plus one equality weight per row.
+        let operands = (0..3)
+            .map(|_| {
+                (0..STREAM_ROWS * row_bytes)
+                    .map(|_| rng.random::<u8>())
+                    .collect::<Vec<_>>()
+            })
+            .collect::<Vec<_>>();
+        let borrowed = operands.iter().map(Vec::as_slice).collect::<Vec<_>>();
+        let eq = (0..STREAM_ROWS)
+            .map(|_| rng.random::<BinaryField128>())
+            .collect::<Vec<_>>();
+
+        // Throughput counts the extension values the round reads.
+        group.throughput(Throughput::Elements(
+            (STREAM_ROWS * round.num_transmitted()) as u64,
+        ));
+        group.bench_function(
+            BenchmarkId::from_parameter(format!("k{log_size}/d{degree}")),
+            |b| {
+                b.iter(|| round.stream_round_message(&borrowed, &eq, &Conjunction));
+            },
+        );
+    }
+    group.finish();
+}
+
+criterion_group!(benches, bench_skip_lde, bench_stream_message);
+criterion_main!(benches);
```
