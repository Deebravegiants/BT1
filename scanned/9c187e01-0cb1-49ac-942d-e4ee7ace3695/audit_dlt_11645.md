# [?] hashes: Fix Hkdf::expand panic at max length

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-09-09
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/c61576fea722b164abd6aa230bf34f514078eda4
Type: security-commit

## Details
hashes: Fix Hkdf::expand panic at max length

Hkdf::expand accepts an output buffer up to the RFC-5869 maximum of 
255 * T::Hash::LEN bytes, but the u8 counter overflows when incremented
past the final block at that max length.

Replace the u8 counter with a for loop which cannot overflow.

Assisted-by: Claude Opus 4.8

## Patch
### hashes/src/hkdf/mod.rs
```diff
@@ -71,36 +71,33 @@ where
             return Err(MaxLengthError { max: MAX_OUTPUT_BLOCKS * T::Hash::LEN });
         }
 
-        // Counter starts at "1" based on RFC5869 spec and is committed to in the hash.
-        let mut counter = 1u8;
         // Ceiling calculation for the total number of blocks (iterations) required for the expand.
         let total_blocks = okm.len().div_ceil(T::Hash::LEN);
 
-        while counter <= total_blocks as u8 {
+        // Counter starts at "1" based on RFC5869 spec and is committed to in the hash.
+        for counter in 1..=total_blocks {
             let mut engine: HmacEngine<T> = HmacEngine::new(self.prk.as_ref());
 
             // First block does not have a previous block,
             // all other blocks include last block in the HMAC input.
-            if counter != 1u8 {
-                let previous_start_index = (counter as usize - 2) * T::Hash::LEN;
-                let previous_end_index = (counter as usize - 1) * T::Hash::LEN;
+            if counter != 1 {
+                let previous_start_index = (counter - 2) * T::Hash::LEN;
+                let previous_end_index = (counter - 1) * T::Hash::LEN;
                 engine.input(&okm[previous_start_index..previous_end_index]);
             }
             engine.input(info);
-            engine.input(&[counter]);
+            engine.input(&[counter as u8]);
 
             let t = engine.finalize();
-            let start_index = (counter as usize - 1) * T::Hash::LEN;
+            let start_index = (counter - 1) * T::Hash::LEN;
             // Last block might not take full hash length.
-            let end_index = if counter == (total_blocks as u8) {
+            let end_index = if counter == total_blocks {
                 okm.len()
             } else {
-                counter as usize * T::Hash::LEN
+                counter * T::Hash::LEN
             };
 
             okm[start_index..end_index].copy_from_slice(&t.as_ref()[0..(end_index - start_index)]);
-
-            counter += 1;
         }
 
         Ok(())
```
