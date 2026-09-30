# [?] Merge rust-bitcoin/rust-bitcoin#4905: Fix SerializedSignature iteration stack overflow

## Summary
Severity: Unknown
Chain: Bitcoin
Component: rust-bitcoin/rust-bitcoin
Published: 2025-08-23
Source: https://github.com/rust-bitcoin/rust-bitcoin/commit/bbf19288a269ae77cb26d0ea48073e36d5f7f627
Type: security-commit

## Details
Merge rust-bitcoin/rust-bitcoin#4905: Fix SerializedSignature iteration stack overflow

65b1c7ea439f6a8da6bedbf9ccd27e4ecc8650db Fix SerializedSignature iteration stack overflow (Casey Rodarmor)

Pull request description:

  `SerializedSignature::{iter,into_iter}` are mutually recursive and cause a stack overflow when called.
  
  This PR delegates `SerializedSignature::into_iter` to `<&[u8]>::into_iter`, and adds a test that the iter function produces the expected bytes, implicitly also testing that it doesn't overflow the stack.


ACKs for top commit:
  tcharding:
    ACK 65b1c7ea439f6a8da6bedbf9ccd27e4ecc8650db
  apoelstra:
    ACK 65b1c7ea439f6a8da6bedbf9ccd27e4ecc8650db; successfully ran local tests


Tree-SHA512: 0b6ba5d2026a1b7f7154b997af8418da27b672a37322733a801a5df4e0898ee3448a43a64c3cd9ac376f18e8bdbae413fbf30b2d5004d3745cf5669666b753c0

## Patch
### bitcoin/src/crypto/ecdsa.rs
```diff
@@ -200,7 +200,7 @@ impl<'a> IntoIterator for &'a SerializedSignature {
     type Item = &'a u8;
 
     #[inline]
-    fn into_iter(self) -> Self::IntoIter { (*self).iter() }
+    fn into_iter(self) -> Self::IntoIter { (**self).iter() }
 }
 
 /// Error encountered while parsing an ECDSA signature from a byte slice.
@@ -336,11 +336,12 @@ impl<'a> Arbitrary<'a> for Signature {
 mod tests {
     use super::*;
 
+    const TEST_SIGNATURE_HEX: &str = "3046022100839c1fbc5304de944f697c9f4b1d01d1faeba32d751c0f7acb21ac8a0f436a72022100e89bd46bb3a5a62adc679f659b7ce876d83ee297c7a5587b2011c4fcc72eab45";
+
     #[test]
     fn write_serialized_signature() {
-        let hex = "3046022100839c1fbc5304de944f697c9f4b1d01d1faeba32d751c0f7acb21ac8a0f436a72022100e89bd46bb3a5a62adc679f659b7ce876d83ee297c7a5587b2011c4fcc72eab45";
         let sig = Signature {
-            signature: secp256k1::ecdsa::Signature::from_str(hex).unwrap(),
+            signature: secp256k1::ecdsa::Signature::from_str(TEST_SIGNATURE_HEX).unwrap(),
             sighash_type: EcdsaSighashType::All,
         };
 
@@ -349,4 +350,14 @@ mod tests {
 
         assert_eq!(sig.to_vec(), buf)
     }
+
+    #[test]
+    fn iterate_serialized_signature() {
+        let sig = Signature {
+            signature: secp256k1::ecdsa::Signature::from_str(TEST_SIGNATURE_HEX).unwrap(),
+            sighash_type: EcdsaSighashType::All,
+        };
+
+        assert_eq!(sig.serialize().iter().copied().collect::<Vec<u8>>(), sig.to_vec());
+    }
 }
```
