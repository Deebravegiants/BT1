# [?] prevent balance overflow in anvil_addBalance (#13457)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-02-17
Source: https://github.com/foundry-rs/foundry/commit/94d1caab9fef5d99107f1a5e6cf7313eb23e2a4c
Type: security-commit

## Details
prevent balance overflow in anvil_addBalance (#13457)

Co-authored-by: Matthias Seitz <matthias.seitz@outlook.de>

## Patch
### crates/anvil/src/eth/api.rs
```diff
@@ -2184,7 +2184,7 @@ impl EthApi {
     pub async fn anvil_add_balance(&self, address: Address, balance: U256) -> Result<()> {
         node_info!("anvil_addBalance");
         let current_balance = self.backend.get_balance(address, None).await?;
-        self.backend.set_balance(address, current_balance + balance).await?;
+        self.backend.set_balance(address, current_balance.saturating_add(balance)).await?;
         Ok(())
     }
 
```

### crates/anvil/tests/it/traces.rs
```diff
@@ -1243,7 +1243,7 @@ async fn test_debug_trace_transaction_pre_state_tracer() {
     "nonce": 1
   },
   "0x70997970c51812dc3a010c7d01b50e0d17dc79c8": {
-    "balance": "0x56bc75e2d630fffff"
+    "balance": "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
   },
   "0xe7f1725e7734ce288f8367e1bb143e90bb3f0512": {
     "balance": "0x0",
```
