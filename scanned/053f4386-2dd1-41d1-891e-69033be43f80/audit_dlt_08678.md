# [?] Prevent gas overflows from being ignored during VP execution

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2024-03-27
Source: https://github.com/namada-net/namada/commit/18f120362d91258f94e2288260550e0e24e2afb2
Type: security-commit

## Details
Prevent gas overflows from being ignored during VP execution

## Patch
### crates/gas/src/lib.rs
```diff
@@ -5,6 +5,7 @@ use std::fmt::Display;
 use std::ops::Div;
 
 use namada_core::borsh::{BorshDeserialize, BorshSchema, BorshSerialize};
+use namada_core::hints;
 use namada_macros::BorshDeserializer;
 #[cfg(feature = "migrations")]
 use namada_migrations::*;
@@ -194,6 +195,8 @@ pub struct TxGasMeter {
 /// Gas metering in a validity predicate
 #[derive(Debug, Clone)]
 pub struct VpGasMeter {
+    /// Track gas overflow
+    gas_overflow: bool,
     /// The transaction gas limit
     tx_gas_limit: Gas,
     /// The gas consumed by the transaction before the Vp
@@ -295,10 +298,17 @@ impl TxGasMeter {
 
 impl GasMetering for VpGasMeter {
     fn consume(&mut self, gas: u64) -> Result<()> {
-        self.current_gas = self
-            .current_gas
-            .checked_add(gas.into())
-            .ok_or(Error::GasOverflow)?;
+        if self.gas_overflow {
+            hints::cold();
+            return Err(Error::GasOverflow);
+        }
+
+        self.current_gas =
+            self.current_gas.checked_add(gas.into()).ok_or_else(|| {
+                hints::cold();
+                self.gas_overflow = true;
+                Error::GasOverflow
+            })?;
 
         let current_total = self
             .initial_gas
@@ -313,7 +323,12 @@ impl GasMetering for VpGasMeter {
     }
 
     fn get_tx_consumed_gas(&self) -> Gas {
-        self.initial_gas
+        if !self.gas_overflow {
+            self.initial_gas
+        } else {
+            hints::cold();
+            u64::MAX.into()
+        }
     }
 
     fn get_gas_limit(&self) -> Gas {
@@ -325,6 +340,7 @@ impl VpGasMeter {
     /// Initialize a new VP gas meter from the `TxGasMeter`
     pub fn new_from_tx_meter(tx_gas_meter: &TxGasMeter) -> Self {
         Self {
+            gas_overflow: false,
             tx_gas_limit: tx_gas_meter.tx_gas_limit,
             initial_gas: tx_gas_meter.transaction_gas,
             current_gas: Gas::default(),
```
