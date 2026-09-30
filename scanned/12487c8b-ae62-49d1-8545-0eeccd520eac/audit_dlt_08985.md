# [?] fix(crypto): do not panic if the passed Ed25519Sha512 public key is of invalid length (#4650)

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2024-05-28
Source: https://github.com/hyperledger-iroha/iroha/commit/f41b0808b9d671f0fe5f98a2f9f89f3fbf730d0a
Type: security-commit

## Details
fix(crypto): do not panic if the passed Ed25519Sha512 public key is of invalid length (#4650)

Signed-off-by: Nikita Strygin <dcnick3@users.noreply.github.com>

## Patch
### crypto/src/signature/ed25519.rs
```diff
@@ -11,7 +11,26 @@ pub type PublicKey = ed25519_dalek::VerifyingKey;
 pub type PrivateKey = ed25519_dalek::SigningKey;
 
 #[cfg(not(feature = "std"))]
-use alloc::{string::ToString as _, vec::Vec};
+use alloc::{format, string::ToString as _, vec::Vec};
+
+fn parse_fixed_size<T, E, F, const SIZE: usize>(
+    payload: &[u8],
+    fixed_parser: F,
+) -> Result<T, ParseError>
+where
+    F: FnOnce(&[u8; SIZE]) -> Result<T, E>,
+    E: core::fmt::Display,
+{
+    let fixed_payload: [u8; SIZE] = payload.try_into().map_err(|_| {
+        ParseError(format!(
+            "the payload size is incorrect: expected {}, but got {}",
+            SIZE,
+            payload.len()
+        ))
+    })?;
+
+    fixed_parser(&fixed_payload).map_err(|err| ParseError(err.to_string()))
+}
 
 #[derive(Debug, Clone, Copy)]
 pub struct Ed25519Sha512;
@@ -28,17 +47,11 @@ impl Ed25519Sha512 {
     }
 
     pub fn parse_public_key(payload: &[u8]) -> Result<PublicKey, ParseError> {
-        PublicKey::from_bytes(arrayref::array_ref!(payload, 0, 32))
-            .map_err(|err| ParseError(err.to_string()))
+        parse_fixed_size(payload, PublicKey::from_bytes)
     }
 
     pub fn parse_private_key(payload: &[u8]) -> Result<PrivateKey, ParseError> {
-        <[u8; 64]>::try_from(payload)
-            .map_err(|err| err.to_string())
-            .and_then(|payload| {
-                PrivateKey::from_keypair_bytes(&payload).map_err(|err| err.to_string())
-            })
-            .map_err(ParseError)
+        parse_fixed_size(payload, PrivateKey::from_keypair_bytes)
     }
 
     pub fn sign(message: &[u8], sk: &PrivateKey) -> Vec<u8> {
@@ -142,4 +155,20 @@ mod test {
         };
         Ed25519Sha512::verify(MESSAGE_1, &signature, &p).unwrap();
     }
+
+    #[test]
+    fn invalid_parse_size_does_not_panic() {
+        // passing an empty slice (or some other slice that is not appropriately sized) should not cause a panic
+        // an error should be returned
+        let err = Ed25519Sha512::parse_public_key(&[]).unwrap_err();
+        assert_eq!(
+            err,
+            ParseError("the payload size is incorrect: expected 32, but got 0".to_string())
+        );
+        let err = Ed25519Sha512::parse_private_key(&[1, 2, 3]).unwrap_err();
+        assert_eq!(
+            err,
+            ParseError("the payload size is incorrect: expected 64, but got 3".to_string())
+        );
+    }
 }
```
