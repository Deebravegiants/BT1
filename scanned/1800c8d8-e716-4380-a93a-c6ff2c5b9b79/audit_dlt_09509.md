# [?] fix: ignore dust underflows in order fills rpc (#5352)

## Summary
Severity: Unknown
Chain: Chainflip
Component: chainflip-io/chainflip-backend
Published: 2024-10-24
Source: https://github.com/chainflip-io/chainflip-backend/commit/1bf4d90209e134e60b2bcc815e66aecd8df5e746
Type: security-commit

## Details
fix: ignore dust underflows in order fills rpc (#5352)

fix: ignore dust underflow

## Patch
### state-chain/custom-rpc/src/order_fills.rs
```diff
@@ -66,7 +66,17 @@ fn order_fills_for_pool<'a>(
 						if let Some((previous_collected, _)) = option_previous_order_state {
 							(
 								collected.fees - previous_collected.fees,
-								collected.sold_amount - previous_collected.sold_amount,
+								collected
+									.sold_amount
+									.checked_sub(previous_collected.sold_amount)
+									.unwrap_or_else(|| {
+										log::info!(
+															"Ignored dust sold_amount underflow. Current: {}, Previous: {}",
+															collected.sold_amount,
+															previous_collected.sold_amount
+														);
+										0.into()
+									}),
 								collected.bought_amount - previous_collected.bought_amount,
 							)
 						} else {
```
