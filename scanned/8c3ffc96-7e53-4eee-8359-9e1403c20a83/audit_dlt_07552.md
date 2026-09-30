# [?] fix: resolve panic on `TransactionPlan::auth_hash` for missing memos

## Summary
Severity: Unknown
Chain: Penumbra
Component: penumbra-zone/penumbra
Published: 2022-09-12
Source: https://github.com/penumbra-zone/penumbra/commit/ba2973fb5f84064801ca30ffe361fbdd9d44e994
Type: security-commit

## Details
fix: resolve panic on `TransactionPlan::auth_hash` for missing memos

If for whatever reason the memo key is absent, it is
filled with a dummy value. I'm intentionally not implementing
`Default::default` for `PayloadKey` because this functionality
should not be exposed for `PayloadKey`s in general.

## Patch
### crypto/src/symmetric.rs
```diff
@@ -98,6 +98,12 @@ impl TryFrom<Vec<u8>> for PayloadKey {
     }
 }
 
+impl From<[u8; 32]> for PayloadKey {
+    fn from(bytes: [u8; 32]) -> Self {
+        Self(*Key::from_slice(&bytes))
+    }
+}
+
 /// Represents a symmetric `ChaCha20Poly1305` key.
 ///
 /// Used for encrypting and decrypting [`OvkWrappedKey`] material used to decrypt
```

### transaction/src/auth_hash.rs
```diff
@@ -138,10 +138,17 @@ impl TransactionPlan {
         for spend in self.spend_plans() {
             state.update(spend.spend_body(fvk).auth_hash().as_bytes());
         }
+
+        // If the memo_key is None, then there is no memo, and we populate the memo key
+        // field with a dummy key.
+        let dummy_payload_key: PayloadKey = [0u8; 32].into();
         for output in self.output_plans() {
             state.update(
                 output
-                    .output_body(fvk.outgoing(), &memo_key.clone().unwrap())
+                    .output_body(
+                        fvk.outgoing(),
+                        memo_key.as_ref().unwrap_or(&dummy_payload_key),
+                    )
                     .auth_hash()
                     .as_bytes(),
             );
```

### transaction/src/plan/action/output.rs
```diff
@@ -101,7 +101,7 @@ impl OutputPlan {
         let ovk_wrapped_key = note.encrypt_key(&self.esk, ovk, value_commitment);
 
         let wrapped_memo_key = WrappedMemoKey::encrypt(
-            memo_key,
+            &memo_key,
             self.esk.clone(),
             note.transmission_key(),
             &note.diversified_generator(),
```

### transaction/src/plan/build.rs
```diff
@@ -68,12 +68,16 @@ impl TransactionPlan {
         }
 
         // Build the transaction's outputs.
+        let dummy_payload_key: PayloadKey = [0u8; 32].into();
+        // If the memo_key is None, then there is no memo, and we populate the memo key
+        // field with a dummy key.
         for output_plan in self.output_plans() {
             // Outputs subtract from the transaction's value balance.
             synthetic_blinding_factor -= output_plan.value_blinding;
-            actions.push(Action::Output(
-                output_plan.output(fvk.outgoing(), &memo_key.clone().unwrap()),
-            ));
+            actions.push(Action::Output(output_plan.output(
+                fvk.outgoing(),
+                memo_key.as_ref().unwrap_or(&dummy_payload_key),
+            )));
         }
 
         // Build the transaction's swaps.
```
