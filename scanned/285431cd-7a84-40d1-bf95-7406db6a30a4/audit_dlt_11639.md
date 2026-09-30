# [?] Fix overflow in reading gas_price (#985)

## Summary
Severity: Unknown
Chain: Polkadot
Component: polkadot-evm/frontier
Published: 2023-02-06
Source: https://github.com/polkadot-evm/frontier/commit/e52e5bda1f7cc3659beb0d521bd61baa483c1a90
Type: security-commit

## Details
Fix overflow in reading gas_price (#985)

* Fix overflow in reading gas_price

* Saturating conversion

## Patch
### client/rpc/src/eth/cache/mod.rs
```diff
@@ -348,7 +348,7 @@ where
 			let base_fee = client.runtime_api().gas_price(&id).unwrap_or_default();
 			let receipts = handler.current_receipts(&id);
 			let mut result = FeeHistoryCacheItem {
-				base_fee: base_fee.as_u64(),
+				base_fee: if base_fee > U256::from(u64::MAX) { u64::MAX } else { base_fee.low_u64() },
 				gas_used_ratio: 0f64,
 				rewards: Vec::new(),
 			};
```
