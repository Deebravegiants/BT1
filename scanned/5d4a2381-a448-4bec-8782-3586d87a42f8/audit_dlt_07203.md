# [?] Avoid a panic when downcasting to redjubjub::Error fails (#1363)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2020-11-24
Source: https://github.com/ZcashFoundation/zebra/commit/2d60c00fb068178d7cb765133d24241575baff9b
Type: security-commit

## Details
Avoid a panic when downcasting to redjubjub::Error fails (#1363)

Instead, format the original error as a string, to provide better
diagnostics.

Temporary fix for #1357, the permanent fix ticket is #1186.

## Patch
### zebra-consensus/src/error.rs
```diff
@@ -67,13 +67,20 @@ pub enum TransactionError {
 
     #[error("bindingSig MUST represent a valid signature under the transaction binding validating key bvk of SigHash")]
     RedJubjub(redjubjub::Error),
+
+    // temporary error type until #1186 is fixed
+    #[error("Downcast from BoxError to redjubjub::Error failed")]
+    InternalDowncastError(String),
 }
 
 impl From<BoxError> for TransactionError {
     fn from(err: BoxError) -> Self {
         match err.downcast::<redjubjub::Error>() {
             Ok(e) => TransactionError::RedJubjub(*e),
-            Err(e) => panic!(e),
+            Err(e) => TransactionError::InternalDowncastError(format!(
+                "downcast to redjubjub::Error failed, original error: {:?}",
+                e
+            )),
         }
     }
 }
```
