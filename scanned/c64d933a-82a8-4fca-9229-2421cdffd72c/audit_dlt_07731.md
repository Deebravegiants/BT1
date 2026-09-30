# [?] fix(cli): avoid u64 underflow in setup_without_evm for genesis-block header (#23728)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-04-26
Source: https://github.com/paradigmxyz/reth/commit/bd4cd28a8df764a912c807085ff6d54cd7b5c198
Type: security-commit

## Details
fix(cli): avoid u64 underflow in setup_without_evm for genesis-block header (#23728)

## Patch
### crates/cli/commands/src/init_state/without_evm.rs
```diff
@@ -50,8 +50,13 @@ where
     info!(target: "reth::cli", new_tip = ?header.num_hash(), "Setting up dummy EVM chain before importing state.");
 
     let static_file_provider = provider_rw.static_file_provider();
-    // Write EVM dummy data up to `header - 1` block
-    append_dummy_chain(&static_file_provider, header.number() - 1, header_factory)?;
+    // Write EVM dummy data up to `header - 1` block. Skip when the supplied
+    // header is at block 0: `header.number() - 1` would underflow in u64 to
+    // `u64::MAX`, sending `append_dummy_chain` into a 1..=u64::MAX loop that
+    // exhausts memory before failing.
+    if header.number() > 0 {
+        append_dummy_chain(&static_file_provider, header.number() - 1, header_factory)?;
+    }
 
     info!(target: "reth::cli", "Appending first valid block.");
 
@@ -191,7 +196,13 @@ mod tests {
     use alloy_primitives::{address, b256};
     use reth_db_common::init::init_genesis;
     use reth_provider::{test_utils::create_test_provider_factory, DatabaseProviderFactory};
-    use std::io::Write;
+    use std::{
+        io::Write,
+        sync::{
+            atomic::{AtomicU64, Ordering},
+            Arc,
+        },
+    };
     use tempfile::NamedTempFile;
 
     #[test]
@@ -264,4 +275,45 @@ mod tests {
 
         assert_eq!(actual_next_height, expected_next_height);
     }
+
+    /// Regression: a header at block 0 used to send `append_dummy_chain` into
+    /// a `1..=u64::MAX` loop because `header.number() - 1` underflowed in
+    /// u64. The guard `if header.number() > 0` skips the dummy-chain step
+    /// when there is no pre-genesis range to backfill, so `header_factory`
+    /// is never invoked.
+    #[test]
+    fn test_setup_without_evm_skips_dummy_chain_for_genesis_header() {
+        let header = Header { number: 0, ..Default::default() };
+        let header_hash = header.hash_slow();
+
+        let provider_factory = create_test_provider_factory();
+        init_genesis(&provider_factory).unwrap();
+        let provider_rw = provider_factory.database_provider_rw().unwrap();
+
+        let factory_calls = Arc::new(AtomicU64::new(0));
+        let factory_calls_inner = Arc::clone(&factory_calls);
+
+        // The Result of `setup_without_evm` itself is not asserted: with
+        // `number == 0` plus a genesis already written by `init_genesis`,
+        // the subsequent `append_first_block` may legitimately fail. The
+        // bug under test is the OOM in the dummy-chain loop, observable
+        // through the factory-call counter below.
+        let _ = setup_without_evm(
+            &provider_rw,
+            SealedHeader::new(header, header_hash),
+            move |number| {
+                // Bound calls so a regression cannot exhaust the test
+                // runner's memory; the only correct value here is 0.
+                let n = factory_calls_inner.fetch_add(1, Ordering::Relaxed);
+                assert!(n < 8, "header_factory must not be invoked for a genesis-block header");
+                Header { number, ..Default::default() }
+            },
+        );
+
+        assert_eq!(
+            factory_calls.load(Ordering::Relaxed),
+            0,
+            "append_dummy_chain must be skipped when header.number() == 0"
+        );
+    }
 }
```
