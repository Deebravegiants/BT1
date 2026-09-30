# [?] Avoid panicking on non-found note pos

## Summary
Severity: Unknown
Chain: Namada
Component: namada-net/namada
Published: 2025-09-05
Source: https://github.com/namada-net/namada/commit/d7804da89c3349eb71af09676e60181430301d3b
Type: security-commit

## Details
Avoid panicking on non-found note pos

## Patch
### crates/shielded_token/src/masp/shielded_sync/dispatcher.rs
```diff
@@ -8,7 +8,7 @@ use std::sync::atomic::{self, AtomicBool, AtomicUsize};
 use std::task::{Context, Poll};
 
 use borsh::{BorshDeserialize, BorshSerialize};
-use eyre::{WrapErr, eyre};
+use eyre::{ContextCompat, WrapErr, eyre};
 use futures::future::{Either, select};
 use futures::task::AtomicWaker;
 use masp_primitives::sapling::ViewingKey;
@@ -383,7 +383,17 @@ where
                 )?;
             }
 
-            let first_note_pos = self.ctx.note_index[&masp_indexed_tx];
+            let first_note_pos = self
+                .ctx
+                .note_index
+                .get(&masp_indexed_tx)
+                .copied()
+                .with_context(|| {
+                    format!(
+                        "Could not locate the first note position of the MASP \
+                         tx at {masp_indexed_tx:?}"
+                    )
+                })?;
 
             for vk_index in 0..self.ctx.pos_map.len() {
                 let vk = self.ctx.pos_map.get_index(vk_index).unwrap().0;
```
