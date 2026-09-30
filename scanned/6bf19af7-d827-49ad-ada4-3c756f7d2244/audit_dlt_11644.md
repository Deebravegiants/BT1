# [?] Merge rust-bitcoin/rust-bitcoin#6856: hashes: Fix Hkdf::expand panic

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2026-09-11
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/4cc6f0d27dfafcfd9b9afafe9f7c84115b0d0263
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#6856: hashes: Fix Hkdf::expand panic

9e71cce17be751cabd63f58eee27b9250ba80e9b hashes: Test Hkdf::expand at maximum output length (Jamil Lambert, PhD)
c61576fea722b164abd6aa230bf34f514078eda4 hashes: Fix Hkdf::expand panic at max length (Jamil Lambert, PhD)

Pull request description:

  Hkdf::expand accepts an output buffer up to the RFC-5869 maximum of 255 * T::Hash::LEN bytes, but the per-block counter was a u8. At the maximum length the counter reaches 255 on the final block and the subsequent counter += 1 overflows.  
  
  Replace the u8 counter with a for loop which cannot overflow.
  
  Closes project-loupe/audit-rust-bitcoin#5


ACKs for top commit:
  satsfy:
    tACK 9e71cce17be751cabd63f58eee27b9250ba80e9b
  tcharding:
    ACK 9e71cce17be751cabd63f58eee27b9250ba80e9b
  apoelstra:
    ACK 9e71cce17be751cabd63f58eee27b9250ba80e9b; successfully ran local tests


Tree-SHA512: 07838b649685d88d334dd05216ddbc11ba0f52a0a3e40f40bc52f5b55d75bd68d5ee14ffc666314d4bafd1013bae52b3598300b47095ab851fb33aabaa07d516

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
@@ -235,6 +232,25 @@ mod tests {
         assert!(e.is_err());
     }
 
+    #[test]
+    fn max_okm() {
+        let salt = hex::decode_to_vec("000102030405060708090a0b0c").unwrap();
+        let ikm = hex::decode_to_vec("0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b0b").unwrap();
+        let info = hex::decode_to_vec("f0f1f2f3f4f5f6f7f8f9").unwrap();
+
+        let hkdf = Hkdf::<sha256::HashEngine>::new(&salt, &ikm);
+        // The RFC-5869 maximum output length of `255 * hash length` must not panic.
+        let mut okm = [0u8; 255 * 32];
+        hkdf.expand(&info, &mut okm).unwrap();
+
+        // HKDF output is a stable prefix stream, so the first 42 bytes match the
+        // RFC-5869 test case 1 vector.
+        assert_eq!(
+            okm[..42].to_lower_hex_string(),
+            "3cb25f25faacd57a90434f64d0362f2a2d2d0a90cf1a5a4c5db02d56ecc4c5bf34007208d5b887185865"
+        );
+    }
+
     #[test]
     fn short_okm() {
         let salt = hex::decode_to_vec("000102030405060708090a0b0c").unwrap();
```
