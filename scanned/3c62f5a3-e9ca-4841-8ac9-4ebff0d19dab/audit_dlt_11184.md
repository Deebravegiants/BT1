# [?] fix: sponge pad panics on input

## Summary
Severity: Unknown
Chain: Miden
Component: 0xMiden/miden-vm
Published: 2023-01-26
Source: https://github.com/0xMiden/miden-vm/commit/ed36ebc542ce660ad2fc3a588235e29adfad691f
Type: security-commit

## Details
fix: sponge pad panics on input

closes #44

## Patch
### src/hash/rpo/mod.rs
```diff
@@ -94,61 +94,64 @@ impl Hasher for Rpo256 {
     type Digest = RpoDigest;
 
     fn hash(bytes: &[u8]) -> Self::Digest {
-        // compute the number of elements required to represent the string; we will be processing
-        // the string in BINARY_CHUNK_SIZE-byte chunks, thus the number of elements will be equal
-        // to the number of such chunks (including a potential partial chunk at the end).
-        let num_elements = if bytes.len() % BINARY_CHUNK_SIZE == 0 {
-            bytes.len() / BINARY_CHUNK_SIZE
-        } else {
-            bytes.len() / BINARY_CHUNK_SIZE + 1
-        };
-
-        // initialize state to all zeros, except for the first element of the capacity part, which
-        // is set to the number of elements to be hashed. this is done so that adding zero elements
-        // at the end of the list always results in a different hash.
+        // initialize the state with zeroes
         let mut state = [ZERO; STATE_WIDTH];
-        state[CAPACITY_RANGE.start] = Felt::new(num_elements as u64);
 
-        // break the string into BINARY_CHUNK_SIZE-byte chunks, convert each chunk into a field
-        // element, and absorb the element into the rate portion of the state. we use
-        // BINARY_CHUNK_SIZE-byte chunks because every BINARY_CHUNK_SIZE-byte chunk is guaranteed
-        // to map to some field element.
-        let mut i = 0;
+        // set the capacity (first element) to a flag on whether or not the input length is evenly
+        // divided by the rate. this will prevent collisions between padded and non-padded inputs,
+        // and will rule out the need to perform an extra permutation in case of evenly divided
+        // inputs.
+        let is_rate_multiple = bytes.len() % RATE_WIDTH == 0;
+        if !is_rate_multiple {
+            state[CAPACITY_RANGE.start] = ONE;
+        }
+
+        // initialize a buffer to receive the little-endian elements.
         let mut buf = [0_u8; 8];
-        for chunk in bytes.chunks(BINARY_CHUNK_SIZE) {
-            if i < num_elements - 1 {
+
+        // iterate the chunks of bytes, creating a field element from each chunk and copying it
+        // into the state.
+        //
+        // every time the rate range is filled, a permutation is performed. if the final value of
+        // `i` is not zero, then the chunks count wasn't enough to fill the state range, and an
+        // additional permutation must be performed.
+        let i = bytes.chunks(BINARY_CHUNK_SIZE).fold(0, |i, chunk| {
+            // the last element of the iteration may or may not be a full chunk. if it's not, then
+            // we need to pad the remainder bytes of the chunk with zeroes, separated by a `1`.
+            // this will avoid collisions.
+            if chunk.len() == BINARY_CHUNK_SIZE {
                 buf[..BINARY_CHUNK_SIZE].copy_from_slice(chunk);
             } else {
-                // if we are dealing with the last chunk, it may be smaller than BINARY_CHUNK_SIZE
-                // bytes long, so we need to handle it slightly differently. We also append a byte
-                // with value 1 to the end of the string; this pads the string in such a way that
-                // adding trailing zeros results in different hash
-                let chunk_len = chunk.len();
-                buf = [0_u8; 8];
-                buf[..chunk_len].copy_from_slice(chunk);
-                buf[chunk_len] = 1;
+                buf.fill(0);
+                buf[..chunk.len()].copy_from_slice(chunk);
+                buf[chunk.len()] = 1;
             }
 
-            // convert the bytes into a field element and absorb it into the rate portion of the
-            // state; if the rate is filled up, apply the Rescue permutation and start absorbing
-            // again from zero index.
+            // set the current rate element to the input. since we take at most 7 bytes, we are
+            // guaranteed that the inputs data will fit into a single field element.
             state[RATE_RANGE.start + i] = Felt::new(u64::from_le_bytes(buf));
-            i += 1;
-            if i % RATE_WIDTH == 0 {
+
+            // proceed filling the range. if it's full, then we apply a permutation and reset the
+            // counter to the beginning of the range.
+            if i == RATE_WIDTH - 1 {
                 Self::apply_permutation(&mut state);
-                i = 0;
+                0
+            } else {
+                i + 1
             }
-        }
+        });
 
         // if we absorbed some elements but didn't apply a permutation to them (would happen when
-        // the number of elements is not a multiple of RATE_WIDTH), apply the RPO permutation.
-        // we don't need to apply any extra padding because we injected total number of elements
-        // in the input list into the capacity portion of the state during initialization.
-        if i > 0 {
+        // the number of elements is not a multiple of RATE_WIDTH), apply the RPO permutation. we
+        // don't need to apply any extra padding because the first capacity element containts a
+        // flag indicating whether the input is evenly divisible by the rate.
+        if i != 0 {
+            state[RATE_RANGE.start + i..RATE_RANGE.end].fill(ZERO);
+            state[RATE_RANGE.start + i] = ONE;
             Self::apply_permutation(&mut state);
         }
 
-        // return the first 4 elements of the state as hash result
+        // return the first 4 elements of the rate as hash result.
         RpoDigest::new(state[DIGEST_RANGE].try_into().unwrap())
     }
 
```

### src/hash/rpo/tests.rs
```diff
@@ -2,7 +2,9 @@ use super::{
     Felt, FieldElement, Hasher, Rpo256, RpoDigest, StarkField, ALPHA, INV_ALPHA, ONE, STATE_WIDTH,
     ZERO,
 };
+use crate::utils::collections::{BTreeSet, Vec};
 use core::convert::TryInto;
+use proptest::prelude::*;
 use rand_utils::rand_value;
 
 #[test]
@@ -193,6 +195,43 @@ fn hash_test_vectors() {
     }
 }
 
+#[test]
+fn sponge_bytes_with_remainder_length_wont_panic() {
+    // this test targets to assert that no panic will happen with the edge case of having an inputs
+    // with length that is not divisible by the used binary chunk size. 113 is a non-negligible
+    // input length that is prime; hence guaranteed to not be divisible by any choice of chunk
+    // size.
+    //
+    // this is a preliminary test to the fuzzy-stress of proptest.
+    Rpo256::hash(&vec![0; 113]);
+}
+
+#[test]
+fn sponge_collision_for_wrapped_field_element() {
+    let a = Rpo256::hash(&[0; 8]);
+    let b = Rpo256::hash(&Felt::MODULUS.to_le_bytes());
+    assert_ne!(a, b);
+}
+
+#[test]
+fn sponge_zeroes_collision() {
+    let mut zeroes = Vec::with_capacity(255);
+    let mut set = BTreeSet::new();
+    (0..255).for_each(|_| {
+        let hash = Rpo256::hash(&zeroes);
+        zeroes.push(0);
+        // panic if a collision was found
+        assert!(set.insert(hash));
+    });
+}
+
+proptest! {
+    #[test]
+    fn rpo256_wont_panic_with_arbitrary_input(ref vec in any::<Vec<u8>>()) {
+        Rpo256::hash(&vec);
+    }
+}
+
 const EXPECTED: [[Felt; 4]; 19] = [
     [
         Felt::new(1502364727743950833),
```
