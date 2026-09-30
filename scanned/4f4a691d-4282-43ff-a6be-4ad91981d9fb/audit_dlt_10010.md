# [?] Avoid panicking in trace RPC (#447)

## Summary
Severity: Unknown
Chain: Moonbeam
Component: moonbeam-foundation/moonbeam
Published: 2021-05-26
Source: https://github.com/moonbeam-foundation/moonbeam/commit/387f0388df1361238f95319e69b61e6a7ce9eca6
Type: security-commit

## Details
Avoid panicking in trace RPC (#447)

In case of problems an RPC handler should return an error and log a warning instead of panicking.

## Patch
### client/rpc/trace/src/lib.rs
```diff
@@ -824,8 +824,18 @@ where
 		let extrinsics = backend
 			.blockchain()
 			.body(substrate_block_id)
-			.unwrap()
-			.unwrap();
+			.map_err(|e| {
+				internal_err(format!(
+					"Blockchain error when fetching extrinsics of block {} : {:?}",
+					height, e
+				))
+			})?
+			.ok_or_else(|| {
+				internal_err(format!(
+					"Could not find block {} when fetching extrinsics.",
+					height
+				))
+			})?;
 
 		// Trace the block.
 		let mut traces: Vec<_> = api
@@ -849,7 +859,17 @@ where
 			trace.block_number = height;
 			trace.transaction_hash = eth_transactions
 				.get(trace.transaction_position as usize)
-				.expect("amount of eth transactions should match")
+				.ok_or_else(|| {
+					tracing::warn!(
+						"Bug: A transaction has been replayed while it shouldn't (in block {}).",
+						height
+					);
+
+					internal_err(format!(
+						"Bug: A transaction has been replayed while it shouldn't (in block {}).",
+						height
+					))
+				})?
 				.transaction_hash;
 
 			// Reformat error messages.
```
