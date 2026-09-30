# [?] Fix total_evm_tokens underflow in eth_estimateGas.

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-04-06
Source: https://github.com/Conflux-Chain/conflux-rust/commit/dcef8bb8d6ebd8296c91d8698fa4f96bbcb8a5ae
Type: security-commit

## Details
Fix total_evm_tokens underflow in eth_estimateGas.

## Patch
### core/src/executive/executive.rs
```diff
@@ -1016,15 +1016,22 @@ impl<
         let sender = tx.sender();
         let balance = self.state.balance(&sender)?;
         // Give the sender a sufficient balance.
-        let needed_balance = U256::MAX / U256::from(2);
+        let needed_balance = U256::MAX / U256::from(2u64);
         self.state.set_nonce(&sender, &tx.nonce())?;
         if balance < needed_balance {
+            let balance_inc = needed_balance - balance;
             self.state.add_balance(
                 &sender,
-                &(needed_balance - balance),
+                &balance_inc,
                 CleanupMode::NoEmpty,
                 self.spec.account_start_nonce,
             )?;
+            // Make sure statistics are also correct and will not violate any
+            // underlying assumptions.
+            self.state.add_total_issued(balance_inc);
+            if tx.sender().space == Space::Ethereum {
+                self.state.add_total_evm_tokens(balance_inc);
+            }
         }
         let options = TransactOptions::virtual_call();
         self.transact(tx, options)
```
