# [?] fix(rosetta): reject SECP256K1 keys instead of panicking (#15309)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2026-03-05
Source: https://github.com/near/nearcore/commit/940991dae5c243c92fd8fd27f7364629104f83f9
Type: security-commit

## Details
fix(rosetta): reject SECP256K1 keys instead of panicking (#15309)

The `/construction/payloads` endpoint panics when a SECP256K1 public key
is provided, crashing the entire neard process.

This PR fixes the incorrect behavior. Now requests with unsupported key
types return `{"code":400,"message":"Invalid Input: SECP256K1 keys are
not supported in Rosetta","retryable":false}` and the panic is not
triggered.

## Patch
### chain/rosetta-rpc/src/lib.rs
```diff
@@ -776,7 +776,7 @@ async fn construction_payloads(
         unsigned_transaction: unsigned_transaction.into(),
         payloads: vec![models::SigningPayload {
             account_identifier: signer_account_id.into(),
-            signature_type: Some(signer_public_access_key.key_type().into()),
+            signature_type: Some(signer_public_access_key.key_type().try_into()?),
             hex_bytes: transaction_hash.as_ref().to_vec().into(),
         }],
     }))
```

### chain/rosetta-rpc/src/models.rs
```diff
@@ -1332,13 +1332,15 @@ pub(crate) enum SignatureType {
      * Schnorr1, */
 }
 
-impl From<near_crypto::KeyType> for SignatureType {
-    fn from(key_type: near_crypto::KeyType) -> Self {
+impl TryFrom<near_crypto::KeyType> for SignatureType {
+    type Error = crate::errors::ErrorKind;
+
+    fn try_from(key_type: near_crypto::KeyType) -> Result<Self, Self::Error> {
         match key_type {
-            near_crypto::KeyType::ED25519 => Self::Ed25519,
-            near_crypto::KeyType::SECP256K1 => {
-                unimplemented!("SECP256K1 keys are not implemented in Rosetta yet")
-            }
+            near_crypto::KeyType::ED25519 => Ok(Self::Ed25519),
+            near_crypto::KeyType::SECP256K1 => Err(crate::errors::ErrorKind::InvalidInput(
+                "SECP256K1 keys are not supported in Rosetta".to_string(),
+            )),
         }
     }
 }
@@ -1439,3 +1441,20 @@ pub(crate) struct FTMetadataResponse {
 pub(crate) struct FTAccountBalanceResponse {
     pub amount: u128,
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+
+    #[test]
+    fn test_signature_type_try_from_ed25519() {
+        let result = SignatureType::try_from(near_crypto::KeyType::ED25519);
+        assert_eq!(result.unwrap(), SignatureType::Ed25519);
+    }
+
+    #[test]
+    fn test_signature_type_try_from_secp256k1_returns_error() {
+        let result = SignatureType::try_from(near_crypto::KeyType::SECP256K1);
+        assert!(result.is_err());
+    }
+}
```
