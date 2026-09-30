# [?] Fix an overflow during balance calculation when waiting for compound transaction acceptance. (#393)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2024-01-15
Source: https://github.com/kaspanet/rusty-kaspa/commit/fb5e304f558810bcd70fb16e3afb97759a39c28c
Type: security-commit

## Details
Fix an overflow during balance calculation when waiting for compound transaction acceptance. (#393)

* Fix balance calculation overflow when waiting for compound transaction acceptance.

* account for fees in compound transactions

## Patch
### wallet/core/src/utxo/context.rs
```diff
@@ -498,23 +498,23 @@ impl UtxoContext {
                     consumed += tx.aggregate_input_value();
                 } else {
                     // compound tx has no payment value
-                    // we skip them, accumulating only fees
-                    // as fees are the only component that will
-                    // reduce the final balance after the
-                    // compound process
-                    outgoing += tx.fees();
+                    outgoing += tx.fees() + tx.aggregate_output_value();
+                    consumed += tx.aggregate_input_value()
                 }
             }
         }
 
-        Balance::new(
-            (mature + consumed) - outgoing,
-            pending,
-            outgoing,
-            context.mature.len(),
-            context.pending.len(),
-            context.stasis.len(),
-        )
+        // TODO - remove this check once we are confident that
+        // this condition does not occur. This is a temporary
+        // log for a fixed bug, but we want to keep the check
+        // just in case.
+        if mature + consumed < outgoing {
+            log_error!("Error: outgoing transaction value exceeds available balance");
+        }
+
+        let mature = (mature + consumed).saturating_sub(outgoing);
+
+        Balance::new(mature, pending, outgoing, context.mature.len(), context.pending.len(), context.stasis.len())
     }
 
     pub(crate) async fn handle_utxo_added(&self, utxos: Vec<UtxoEntryReference>, current_daa_score: u64) -> Result<()> {
```

### wallet/core/src/utxo/outgoing.rs
```diff
@@ -57,6 +57,10 @@ impl OutgoingTransaction {
         self.inner.pending_transaction.aggregate_input_value()
     }
 
+    pub fn aggregate_output_value(&self) -> u64 {
+        self.inner.pending_transaction.aggregate_output_value()
+    }
+
     pub fn pending_transaction(&self) -> &PendingTransaction {
         &self.inner.pending_transaction
     }
```
