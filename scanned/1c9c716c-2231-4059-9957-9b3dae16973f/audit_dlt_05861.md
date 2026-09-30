# [?] fix(op-reth): commit RW txn before init_from_state_dump to avoid MDBX writer deadlock (#20485)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-05-04
Source: https://github.com/ethereum-optimism/optimism/commit/e582a2885ad7898c1b9c67f708a97fc8a38ca0db
Type: security-commit

## Details
fix(op-reth): commit RW txn before init_from_state_dump to avoid MDBX writer deadlock (#20485)

`init_from_state_dump` was being called while `provider_rw` (a RW MDBX
transaction acquired earlier in the function for the optional
without-OVM bedrock setup) was still alive. Since `init_from_state_dump`
now takes a `DatabaseProviderFactory` and opens its own RW transaction
internally, and MDBX permits only one writer at a time, the inner txn
blocked forever waiting for the outer one — surfacing as
"Process stalled, awaiting read-write transaction lock" right after
"Initiating state dump".

Commit `provider_rw` before invoking `init_from_state_dump` so the
outer writer lock is released first.

Fixes #20464

Co-authored-by: Claude Opus 4.7 (1M context) <noreply@anthropic.com>

## Patch
### rust/op-reth/crates/cli/src/commands/init_state.rs
```diff
@@ -12,7 +12,8 @@ use reth_optimism_primitives::{
 };
 use reth_primitives_traits::{SealedHeader, header::HeaderMut};
 use reth_provider::{
-    BlockNumReader, DatabaseProviderFactory, StaticFileProviderFactory, StaticFileWriter,
+    BlockNumReader, DBProvider, DatabaseProviderFactory, StaticFileProviderFactory,
+    StaticFileWriter,
 };
 use std::{io::BufReader, sync::Arc};
 use tracing::info;
@@ -95,6 +96,11 @@ impl<C: ChainSpecParser<ChainSpec = OpChainSpec>> InitStateCommandOp<C> {
             ));
         }
 
+        // Commit the RW provider before `init_from_state_dump`: that call opens its own
+        // RW transaction via `provider_factory`, and MDBX permits only one writer at a time —
+        // holding `provider_rw` here would deadlock the inner txn.
+        provider_rw.commit()?;
+
         info!(target: "reth::cli", "Initiating state dump");
 
         let reader = BufReader::new(reth_fs_util::open(self.init_state.state)?);
```
