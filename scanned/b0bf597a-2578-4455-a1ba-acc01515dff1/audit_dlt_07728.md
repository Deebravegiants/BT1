# [?] fix(rpc): reject block timestamp overflow in eth_simulateV1 (#26767)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-08-21
Source: https://github.com/paradigmxyz/reth/commit/7b3432d950030875b23c5c4df7c9f53a7caa4868
Type: security-commit

## Details
fix(rpc): reject block timestamp overflow in eth_simulateV1 (#26767)

Co-authored-by: Matthias Seitz <matthias.seitz@outlook.de>

## Patch
### crates/rpc/rpc-eth-types/src/simulate.rs
```diff
@@ -216,7 +216,13 @@ where
         if gap > 1 {
             for i in 1..gap {
                 let filler_number = prev_number + i;
-                let filler_time = prev_timestamp + timestamp_increment;
+                let filler_time =
+                    prev_timestamp.checked_add(timestamp_increment).ok_or_else(|| {
+                        EthApiError::other(EthSimulateError::BlockTimestampInvalid {
+                            got: prev_timestamp,
+                            parent: prev_timestamp,
+                        })
+                    })?;
                 out.push(SimBlock {
                     block_overrides: Some(BlockOverrides {
                         number: Some(U256::from(filler_number)),
@@ -241,7 +247,12 @@ where
             }
             t
         } else {
-            let t = prev_timestamp + timestamp_increment;
+            let t = prev_timestamp.checked_add(timestamp_increment).ok_or_else(|| {
+                EthApiError::other(EthSimulateError::BlockTimestampInvalid {
+                    got: prev_timestamp,
+                    parent: prev_timestamp,
+                })
+            })?;
             overrides.time = Some(t);
             t
         };
@@ -755,6 +766,46 @@ mod tests {
         assert!(matches!(err, EthApiError::Other(_)));
     }
 
+    #[test]
+    fn sanitize_chain_rejects_timestamp_overflow() {
+        // A block may set any timestamp above its parent's, including `u64::MAX`. The following
+        // block then defaults to `prev + increment`, which must not wrap.
+        let parent = parent_at(0, 0);
+        let blocks: Vec<SimBlock<TransactionRequest>> = vec![
+            SimBlock {
+                block_overrides: Some(BlockOverrides {
+                    time: Some(u64::MAX),
+                    ..Default::default()
+                }),
+                ..Default::default()
+            },
+            SimBlock::default(),
+        ];
+
+        let err = sanitize_chain(blocks, &parent, Chain::mainnet().id(), 256).unwrap_err();
+        assert!(matches!(err, EthApiError::Other(_)));
+    }
+
+    #[test]
+    fn sanitize_chain_rejects_filler_timestamp_overflow() {
+        // Same, but the wrap would happen while generating filler blocks for a number gap.
+        let parent = parent_at(0, 0);
+        let blocks = vec![
+            SimBlock {
+                block_overrides: Some(BlockOverrides {
+                    number: Some(U256::from(1)),
+                    time: Some(u64::MAX),
+                    ..Default::default()
+                }),
+                ..Default::default()
+            },
+            block_with_number(4),
+        ];
+
+        let err = sanitize_chain(blocks, &parent, Chain::mainnet().id(), 256).unwrap_err();
+        assert!(matches!(err, EthApiError::Other(_)));
+    }
+
     #[test]
     fn sanitize_chain_enforces_max_blocks() {
         let parent = parent_at(0, 0);
```
