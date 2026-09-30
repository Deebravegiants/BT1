# [?] fix cfx_call two phase panic

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2022-05-23
Source: https://github.com/Conflux-Chain/conflux-rust/commit/c844b0b1bb920592652328d19d99d5d5ece057d4
Type: security-commit

## Details
fix cfx_call two phase panic

## Patch
### core/src/executive/executive.rs
```diff
@@ -1016,6 +1016,7 @@ impl<
     ) -> DbResult<ExecutionOutcome> {
         let is_native_tx = tx.space() == Space::Native;
         let options = TransactOptions::virtual_call();
+        let value_and_fee = tx.value() + tx.gas() * tx.gas_price();
         // If tx.from is specified (is not zero)
         if !tx.sender().address.is_zero() {
             let balance = self.state.balance(&tx.sender())?;
@@ -1025,7 +1026,6 @@ impl<
             // gas_fee Then set tx.storage_limit to tx.from max
             // affordable amount
             if is_native_tx && tx.storage_limit().unwrap_or(0) == u64::MAX {
-                let value_and_fee = tx.value() + tx.gas() * tx.gas_price();
                 if balance > value_and_fee {
                     let available_storage_limit = (balance - value_and_fee)
                         / *DRIPS_PER_STORAGE_COLLATERAL_UNIT;
@@ -1057,7 +1057,9 @@ impl<
         };
         let balance = self.state.balance(&sender)?;
         // Give the sender a sufficient balance.
-        let needed_balance = U256::MAX / U256::from(2u64);
+        let needed_balance = value_and_fee
+            + U256::from(tx.storage_limit().unwrap_or(0))
+                * (*DRIPS_PER_STORAGE_COLLATERAL_UNIT);
         if balance < needed_balance {
             let balance_inc = needed_balance - balance;
             self.state.add_balance(
```
