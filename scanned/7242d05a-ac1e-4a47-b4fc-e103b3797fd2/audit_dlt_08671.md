# [?] Fixes possible expiration overflow in masp tx construction

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2025-07-04
Source: https://github.com/namada-net/namada/commit/73f3bb15ba8143cbf649103b9ecf3af698823104
Type: security-commit

## Details
Fixes possible expiration overflow in masp tx construction

## Patch
### crates/shielded_token/src/masp/shielded_wallet.rs
```diff
@@ -1156,10 +1156,13 @@ pub trait ShieldedApi<U: ShieldedUtils + MaybeSend + MaybeSync>:
             Some(expiration) => {
                 // Try to match a DateTime expiration with a plausible
                 // corresponding block height
-                let last_block_height = Self::query_block(context.client())
-                    .await
-                    .map_err(|e| TransferErr::General(e.to_string()))?
-                    .unwrap_or(1);
+                let last_block_height = u32::try_from(
+                    Self::query_block(context.client())
+                        .await
+                        .map_err(|e| TransferErr::General(e.to_string()))?
+                        .unwrap_or(1),
+                )
+                .map_err(|e| TransferErr::General(e.to_string()))?;
                 let max_block_time =
                     Self::query_max_block_time_estimate(context.client())
                         .await
@@ -1175,14 +1178,20 @@ pub trait ShieldedApi<U: ShieldedUtils + MaybeSend + MaybeSync>:
                         / i64::try_from(max_block_time.0).unwrap(),
                 )
                 .map_err(|e| TransferErr::General(e.to_string()))?;
-                u32::try_from(last_block_height)
-                    .map_err(|e| TransferErr::General(e.to_string()))?
-                    + delta_blocks
+                match checked!(last_block_height + delta_blocks) {
+                    Ok(height) if height <= u32::MAX - 20 => height,
+                    _ => {
+                        return Err(TransferErr::General(
+                            "The provided expiration exceeds the maximum \
+                             allowed"
+                                .to_string(),
+                        ));
+                    }
+                }
             }
             None => {
-                // NOTE: The masp library doesn't support optional
-                // expiration so we set the max to mimic
-                // a never-expiring tx. We also need to
+                // NOTE: The masp library doesn't support optional expiration so
+                // we set the max to mimic a never-expiring tx. We also need to
                 // remove 20 which is going to be added back by the builder
                 u32::MAX - 20
             }
```

### crates/vm/src/host_env.rs
```diff
@@ -1793,7 +1793,10 @@ where
 
 /// Getting the block height function exposed to the wasm VM VP
 /// environment. The height is that of the block to which the current
-/// transaction is being applied.
+/// transaction is being applied if we are in between the `FinalizeBlock`
+/// and the `Commit` phases. For all the other phases we return the block height
+/// of next block that the consensus process will decide upon (i.e. the block
+/// height of the last committed block + 1)
 pub fn vp_get_block_height<MEM, D, H, EVAL, CA>(
     env: &mut VpVmEnv<MEM, D, H, EVAL, CA>,
 ) -> Result<u64>
```

### crates/vp/src/vp_host_fns.rs
```diff
@@ -211,16 +211,24 @@ where
 }
 
 /// Getting the block height. The height is that of the block to which the
-/// current transaction is being applied.
+/// current transaction is being applied if we are in between the
+/// `FinalizeBlock` and the `Commit` phases. For all the other phases we return
+/// the block height of next block that the consensus process will decide upon
+/// (i.e. the block height of the last committed block + 1)
 pub fn get_block_height<S>(
     gas_meter: &RefCell<VpGasMeter>,
     state: &S,
 ) -> Result<BlockHeight>
 where
     S: StateRead + Debug,
 {
-    let (height, gas) = state.in_mem().get_block_height();
+    let (mut height, gas) = state.in_mem().get_block_height();
     add_gas(gas_meter, gas)?;
+    if state.in_mem().header.is_none() {
+        // When not finalizing a decided block, increase the block height to
+        // match that of the next block that will be proposed
+        height = height.next_height();
+    }
     Ok(height)
 }
 
```
