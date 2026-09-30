# [?] fix:Correct ECDSA signature malleability handling (#13544)

## Summary
Severity: Unknown
Chain: Aptos
Component: aptos-labs/aptos-core
Published: 2024-06-05
Source: https://github.com/aptos-labs/aptos-core/commit/6e4a3f9aeeb6d3afab3f3ae9efc625a008382223
Type: security-commit

## Details
fix:Correct ECDSA signature malleability handling (#13544)

* Correct ECDSA signature malleability handling

* Rename function check_s_lt_order_half to check_s_le_order_half

## Patch
### crates/aptos-crypto/src/secp256r1_ecdsa/secp256r1_ecdsa_sigs.rs
```diff
@@ -65,23 +65,23 @@ impl Signature {
         if bytes.len() != SIGNATURE_LENGTH {
             return Err(CryptoMaterialError::WrongLengthError);
         }
-        if !Signature::check_s_lt_order_half(&bytes[32..]) {
+        if !Signature::check_s_le_order_half(&bytes[32..]) {
             return Err(CryptoMaterialError::CanonicalRepresentationError);
         }
         Ok(())
     }
 
-    /// Check if S < ORDER_HALF to capture invalid signatures.
-    fn check_s_lt_order_half(s: &[u8]) -> bool {
+    /// Check if S <= ORDER_HALF to capture invalid signatures.
+    fn check_s_le_order_half(s: &[u8]) -> bool {
         for i in 0..32 {
             match s[i].cmp(&ORDER_HALF[i]) {
                 Ordering::Less => return true,
                 Ordering::Greater => return false,
                 _ => {},
             }
         }
-        // At this stage S == ORDER_HALF which implies a non canonical S.
-        false
+        // At this stage S == ORDER_HALF , it is still considered a canonical value.
+        true
     }
 
     /// If the signature {R,S} does not have S < n/2 where n is the Ristretto255 order, return
```

### crates/aptos-crypto/src/unit_tests/secp256r1_ecdsa_test.rs
```diff
@@ -208,13 +208,11 @@ proptest! {
         let sig_unchecked = Signature::from_bytes_unchecked(&serialized);
         prop_assert!(sig_unchecked.is_ok());
 
-        // Update the signature by setting S = L to make it invalid.
+        // S = ORDER_HALF should be a canonical signature.
         serialized[32..].copy_from_slice(&ORDER_HALF);
-        let serialized_malleable_l: &[u8] = &serialized;
-        // try_from will fail with CanonicalRepresentationError.
-        prop_assert_eq!(
-            Signature::try_from(serialized_malleable_l),
-            Err(CryptoMaterialError::CanonicalRepresentationError)
+        let canonical: &[u8] = &serialized;
+        prop_assert!(
+            Signature::try_from(canonical).is_ok()
         );
     }
 }
```
