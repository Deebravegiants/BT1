# [?] fix(challenger): reject absorb length tags that overflow u8 (#1738)

## Summary
Severity: Unknown
Chain: ZK
Component: Plonky3/Plonky3
Published: 2026-06-04
Source: https://github.com/Plonky3/Plonky3/commit/e631b40d8215d501a18c0d5ef234d8c659286865
Type: security-commit

## Details
fix(challenger): reject absorb length tags that overflow u8 (#1738)

The capacity length tag stamped by padded absorbs is a u8, but both
call sites cast a usize length with `as u8`, which silently wraps.
With max_absorb_injective_limbs * RATE > 255, two absorbs whose
lengths differ by a multiple of 256 would stamp the same tag and
collide in the transcript (e.g. absorbing [x] vs [x] plus 256 zeros
produces identical padded rate rows and identical tags).

- MultiField32Challenger::new now errors when
  max_absorb_injective_limbs * RATE > 255, which also bounds the
  digest-block path since limbs-per-slot >= 1 implies RATE <= 255.
- Both `as u8` casts become checked u8::try_from conversions, so a
  future refactor that breaks the constructor invariant panics
  loudly instead of wrapping silently.
- Document the byte-sized tag domain on the absorb method and add a
  regression test pinning the boundary (2 * 128 = 256 rejected,
  2 * 127 = 254 accepted) and the exact error message.

Co-authored-by: Claude Opus 4.8 (1M context) <noreply@anthropic.com>

## Patch
### challenger/src/duplex_challenger.rs
```diff
@@ -110,6 +110,11 @@ where
     /// Clears `input_buffer` and `output_buffer` before absorbing. Used by
     /// [`MultiField32Challenger`](crate::MultiField32Challenger) so packed scalar and native-digest
     /// absorbs share this [`DuplexChallenger`]'s sponge state without queuing through `observe`.
+    ///
+    /// # Why the tag is a byte
+    ///
+    /// - The tag distinguishes at most 256 absorb lengths.
+    /// - Callers must keep logical lengths at most 255, or lengths differing by 256 collide.
     pub fn absorb_rate_padded_with_tag(&mut self, values: &[F], length_tag: u8) {
         const {
             assert!(
```

### challenger/src/multi_field_challenger.rs
```diff
@@ -91,6 +91,13 @@ where
         if RATE >= WIDTH {
             return Err(String::from("RATE must be less than WIDTH"));
         }
+        // A full flush stamps up to limbs-per-slot * RATE scalars into a byte-sized length tag.
+        // Past 255, lengths differing by 256 would share a tag and collide in the transcript.
+        if max_absorb_injective_limbs::<F, PF>() * RATE > u8::MAX as usize {
+            return Err(String::from(
+                "absorb length tag must fit in a u8: max_absorb_injective_limbs * RATE must be at most 255",
+            ));
+        }
 
         Ok(Self {
             inner: DuplexChallenger::new(permutation),
@@ -112,7 +119,9 @@ where
             .chunks(absorb_n)
             .map(|chunk| reduce_packed(chunk, rb))
             .collect();
-        self.inner.absorb_rate_padded_with_tag(&packed, n_in as u8);
+        // Invariant: the constructor bounds a full flush at 255 scalars, so this never truncates.
+        let tag = u8::try_from(n_in).expect("absorb length tag must fit in a u8");
+        self.inner.absorb_rate_padded_with_tag(&packed, tag);
         self.f_buffer.clear();
         self.f_squeeze_buffer.clear();
     }
@@ -186,8 +195,9 @@ where
         let words: &[PF; N] = values.as_ref();
 
         for chunk in words.chunks(RATE) {
-            self.inner
-                .absorb_rate_padded_with_tag(chunk, chunk.len() as u8);
+            // Invariant: each block holds at most RATE words, bounded at 255 by the constructor.
+            let tag = u8::try_from(chunk.len()).expect("absorb length tag must fit in a u8");
+            self.inner.absorb_rate_padded_with_tag(chunk, tag);
             self.f_squeeze_buffer.clear();
         }
     }
@@ -353,6 +363,41 @@ mod tests {
 
     impl CryptographicPermutation<[PF; WIDTH]> for MixingPermutation {}
 
+    /// A no-op permutation generic over the state width.
+    /// Lets tests instantiate challengers at widths the fixed-width permutations cannot reach.
+    #[derive(Clone)]
+    struct WideIdentityPermutation;
+
+    impl<const W: usize> Permutation<[PF; W]> for WideIdentityPermutation {
+        fn permute_mut(&self, _input: &mut [PF; W]) {}
+    }
+
+    impl<const W: usize> CryptographicPermutation<[PF; W]> for WideIdentityPermutation {}
+
+    #[test]
+    fn test_new_rejects_length_tag_overflow() {
+        // The capacity length tag is a single byte stamped per padded absorb.
+        // A full flush absorbs up to limbs-per-slot * RATE scalars at once.
+        //
+        // Fixture state: BabyBear packs 2 limbs per Goldilocks rate slot.
+        assert_eq!(max_absorb_injective_limbs::<F, PF>(), 2);
+
+        // Mutation: push RATE past the byte boundary.
+        //
+        //     RATE = 128 → 2 * 128 = 256 > 255 → reject
+        //     RATE = 127 → 2 * 127 = 254 ≤ 255 → accept
+        let too_wide = MultiField32Challenger::<F, PF, _, 129, 128>::new(WideIdentityPermutation);
+        assert_eq!(
+            too_wide.err().as_deref(),
+            Some(
+                "absorb length tag must fit in a u8: max_absorb_injective_limbs * RATE must be at most 255"
+            )
+        );
+
+        let in_range = MultiField32Challenger::<F, PF, _, 128, 127>::new(WideIdentityPermutation);
+        assert!(in_range.is_ok());
+    }
+
     #[test]
     fn test_packing() {
         let c = MultiField32Challenger::<F, PF, _, WIDTH, RATE>::new(MixingPermutation).unwrap();
```
