# [?] apollo_l1_provider: panic if pending and calling get_txs or validate (#9365)

## Summary
Severity: Unknown
Chain: Starknet
Component: starkware-libs/sequencer
Published: 2025-09-18
Source: https://github.com/starkware-libs/sequencer/commit/6b3a0746745f546b2be4da7734e015c2a833c0be
Type: security-commit

## Details
apollo_l1_provider: panic if pending and calling get_txs or validate (#9365)

## Patch
### crates/apollo_l1_provider/src/l1_provider.rs
```diff
@@ -103,9 +103,13 @@ impl L1Provider {
                 );
                 Ok(txs)
             }
-            ProviderState::Pending | ProviderState::Bootstrap(_) => {
-                Err(L1ProviderError::OutOfSessionGetTransactions)
+            ProviderState::Pending => {
+                panic!(
+                    "get_txs called while in pending state. Panicking in order to restart the \
+                     provider and bootstrap again."
+                );
             }
+            ProviderState::Bootstrap(_) => Err(L1ProviderError::OutOfSessionGetTransactions),
             ProviderState::Validate => Err(L1ProviderError::GetTransactionConsensusBug),
         }
     }
@@ -128,9 +132,13 @@ impl L1Provider {
                 Ok(self.tx_manager.validate_tx(tx_hash, self.clock.unix_now()))
             }
             ProviderState::Propose => Err(L1ProviderError::ValidateTransactionConsensusBug),
-            ProviderState::Pending | ProviderState::Bootstrap(_) => {
-                Err(L1ProviderError::OutOfSessionValidate)
+            ProviderState::Pending => {
+                panic!(
+                    "validate called while in pending state. Panicking in order to restart the \
+                     provider and bootstrap again."
+                );
             }
+            ProviderState::Bootstrap(_) => Err(L1ProviderError::OutOfSessionValidate),
         }
     }
 
```

### crates/apollo_l1_provider/src/l1_provider_tests.rs
```diff
@@ -1,3 +1,4 @@
+use std::panic::{catch_unwind, AssertUnwindSafe};
 use std::sync::Arc;
 use std::time::Duration;
 
@@ -210,22 +211,19 @@ fn process_events_committed_txs() {
 }
 
 #[test]
-fn pending_state_errors() {
+fn pending_state_panics() {
     // Setup.
     let mut l1_provider = L1ProviderContentBuilder::new()
         .with_state(ProviderState::Pending)
         .with_txs([l1_handler(1)])
         .build_into_l1_provider();
 
     // Test.
-    assert_matches!(
-        l1_provider.get_txs(1, BlockNumber(0)).unwrap_err(),
-        L1ProviderError::OutOfSessionGetTransactions
-    );
+    assert!(catch_unwind(AssertUnwindSafe(|| { l1_provider.get_txs(1, BlockNumber(0)) })).is_err());
 
-    assert_matches!(
-        l1_provider.validate(tx_hash!(1), BlockNumber(0)).unwrap_err(),
-        L1ProviderError::OutOfSessionValidate
+    assert!(
+        catch_unwind(AssertUnwindSafe(|| { l1_provider.validate(tx_hash!(1), BlockNumber(0)) }))
+            .is_err()
     );
 }
 
```
