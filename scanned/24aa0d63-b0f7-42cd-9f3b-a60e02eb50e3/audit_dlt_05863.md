# [?] fix(kona-node): handle missing L1 origin block in sequencer instead of panicking (#19945)

## Summary
Severity: Unknown
Chain: Optimism
Component: ethereum-optimism/optimism
Published: 2026-04-08
Source: https://github.com/ethereum-optimism/optimism/commit/8e333b19ec185321c7c7ae85e4b5f7a087b9a220
Type: security-commit

## Details
fix(kona-node): handle missing L1 origin block in sequencer instead of panicking (#19945)

The origin selector could panic with `unreachable!()` when
`get_block_by_hash` returned `Ok(None)` — e.g. during an L1 reorg or
sync lag. Replace the panic with an `OriginNotFound` error and trigger
an engine reset in the sequencer actor so the node recovers gracefully.

A real-world example of this bug is in [this] ci run.

[this]: https://app.circleci.com/pipelines/github/ethereum-optimism/optimism/121941/workflows/391e49ef-49fb-4a52-a18b-c73e3bb0ee9d/jobs/4753970/tests

Co-authored-by: Claude Opus 4.6 (1M context) <noreply@anthropic.com>

## Patch
### op-acceptance-tests/tests/sync/elsync/reorg/sync_test.go
```diff
@@ -114,6 +114,15 @@ func TestUnsafeGapFillAfterUnsafeReorg_RestartL2CL(gt *testing.T) {
 	// assertions.go:387:             	            	operation failed permanently after 30 attempts: expected head to reorg 0x893d77533b0ff9b37a92090679bf256d987b4535f06186ec71f29e68ddccd9a5:14, but got 0x893d77533b0ff9b37a92090679bf256d987b4535f06186ec71f29e68ddccd9a5:14
 	// assertions.go:387:             	Test:       	TestUnsafeGapFillAfterUnsafeReorg_RestartL2CL
 	sysgo.SkipOnKonaNode(t, "not supported (timeout)")
+	// Example error with op-reth:
+	//
+	// assertions.go:387:
+	// Error Trace:	/op-devstack/dsl/l2_el.go:430
+	//             				/op-acceptance-tests/tests/sync/elsync/reorg/sync_test.go:218
+	// Error:      	Received unexpected error:
+	//             	operation failed permanently after 50 attempts: expected head to match: unsafe
+	// Test:       	TestUnsafeGapFillAfterUnsafeReorg_RestartL2CL
+	sysgo.FlakyOnOpReth(t, "")
 	sys := newReorgSystem(t)
 	require := t.Require()
 	logger := t.Logger()
```

### rust/kona/crates/node/service/src/actors/sequencer/actor.rs
```diff
@@ -13,7 +13,7 @@ use crate::{
                 update_conductor_commitment_duration_metrics, update_seal_duration_metrics,
                 update_total_transactions_sequenced,
             },
-            origin_selector::OriginSelector,
+            origin_selector::{L1OriginSelectorError, OriginSelector},
         },
     },
 };
@@ -225,6 +225,15 @@ where
             .await
         {
             Ok(l1_origin) => l1_origin,
+            Err(L1OriginSelectorError::OriginNotFound(hash)) => {
+                warn!(
+                    target: "sequencer",
+                    %hash,
+                    "L1 origin block not found, resetting engine"
+                );
+                self.engine_client.reset_engine_forkchoice().await?;
+                return Ok(None);
+            }
             Err(err) => {
                 warn!(
                     target: "sequencer",
```

### rust/kona/crates/node/service/src/actors/sequencer/origin_selector.rs
```diff
@@ -70,7 +70,7 @@ impl<P: L1OriginSelectorProvider + Send + Sync> OriginSelector for L1OriginSelec
         }
 
         let Some(current) = self.current else {
-            unreachable!("Current L1 origin should always be set by `select_origins`");
+            return Err(L1OriginSelectorError::OriginNotFound(unsafe_head.l1_origin.hash));
         };
 
         let max_seq_drift = self.cfg.max_sequencer_drift(current.timestamp);
@@ -128,7 +128,12 @@ impl<P: L1OriginSelectorProvider> L1OriginSelector<P> {
         in_recovery_mode: bool,
     ) -> Result<(), L1OriginSelectorError> {
         if in_recovery_mode {
-            self.current = self.l1.get_block_by_hash(unsafe_head.l1_origin.hash).await?;
+            self.current = Some(
+                self.l1
+                    .get_block_by_hash(unsafe_head.l1_origin.hash)
+                    .await?
+                    .ok_or(L1OriginSelectorError::OriginNotFound(unsafe_head.l1_origin.hash))?,
+            );
             self.next = self.l1.get_block_by_number(unsafe_head.l1_origin.number + 1).await?;
             return Ok(());
         }
@@ -141,9 +146,12 @@ impl<P: L1OriginSelectorProvider> L1OriginSelector<P> {
             self.next = None;
         } else {
             // Find the current origin block, as it is missing.
-            let current = self.l1.get_block_by_hash(unsafe_head.l1_origin.hash).await?;
-
-            self.current = current;
+            self.current = Some(
+                self.l1
+                    .get_block_by_hash(unsafe_head.l1_origin.hash)
+                    .await?
+                    .ok_or(L1OriginSelectorError::OriginNotFound(unsafe_head.l1_origin.hash))?,
+            );
             self.next = None;
         }
 
@@ -185,6 +193,9 @@ pub enum L1OriginSelectorError {
         "Waiting for more L1 data to be available to select the next L1 origin block. Current L1 origin: {0:?}"
     )]
     NotEnoughData(BlockInfo),
+    /// The L1 origin block could not be found by its hash.
+    #[error("L1 origin block not found for hash: {0}")]
+    OriginNotFound(B256),
 }
 
 /// L1 [`BlockInfo`] provider interface for the [`L1OriginSelector`].
@@ -493,4 +504,129 @@ mod test {
             assert!(matches!(next_err, L1OriginSelectorError::NotEnoughData(_)));
         }
     }
+
+    #[tokio::test]
+    async fn test_next_l1_origin_recovery_mode_found() {
+        const L2_BLOCK_TIME: u64 = 2;
+
+        let cfg = Arc::new(RollupConfig {
+            block_time: L2_BLOCK_TIME,
+            max_sequencer_drift: 600,
+            ..Default::default()
+        });
+
+        let mut provider = MockOriginSelectorProvider::default();
+        provider.with_block(BlockInfo {
+            parent_hash: B256::ZERO,
+            hash: B256::with_last_byte(1),
+            number: 1,
+            timestamp: 12,
+        });
+        provider.with_block(BlockInfo {
+            parent_hash: B256::with_last_byte(1),
+            hash: B256::with_last_byte(2),
+            number: 2,
+            timestamp: 24,
+        });
+
+        let mut selector = L1OriginSelector::new(cfg, provider);
+
+        let unsafe_head = L2BlockInfo {
+            block_info: BlockInfo {
+                hash: B256::ZERO,
+                number: 5,
+                timestamp: 10,
+                ..Default::default()
+            },
+            l1_origin: NumHash { number: 1, hash: B256::with_last_byte(1) },
+            seq_num: 0,
+        };
+
+        let origin = selector.next_l1_origin(unsafe_head, true).await.unwrap();
+        assert_eq!(origin.number, 1);
+        assert_eq!(origin.hash, B256::with_last_byte(1));
+    }
+
+    #[tokio::test]
+    async fn test_next_l1_origin_recovery_mode_not_found() {
+        const L2_BLOCK_TIME: u64 = 2;
+
+        let cfg = Arc::new(RollupConfig {
+            block_time: L2_BLOCK_TIME,
+            max_sequencer_drift: 600,
+            ..Default::default()
+        });
+
+        let provider = MockOriginSelectorProvider::default();
+        let mut selector = L1OriginSelector::new(cfg, provider);
+
+        let unsafe_head = L2BlockInfo {
+            block_info: BlockInfo {
+                hash: B256::ZERO,
+                number: 5,
+                timestamp: 10,
+                ..Default::default()
+            },
+            l1_origin: NumHash { number: 1, hash: B256::with_last_byte(1) },
+            seq_num: 0,
+        };
+
+        let result = selector.next_l1_origin(unsafe_head, true).await;
+        assert!(matches!(
+            result,
+            Err(L1OriginSelectorError::OriginNotFound(hash)) if hash == B256::with_last_byte(1)
+        ));
+    }
+
+    #[tokio::test]
+    async fn test_next_l1_origin_normal_mode_origin_not_found() {
+        const L2_BLOCK_TIME: u64 = 2;
+
+        let cfg = Arc::new(RollupConfig {
+            block_time: L2_BLOCK_TIME,
+            max_sequencer_drift: 600,
+            ..Default::default()
+        });
+
+        let mut provider = MockOriginSelectorProvider::default();
+        provider.with_block(BlockInfo {
+            parent_hash: B256::ZERO,
+            hash: B256::ZERO,
+            number: 0,
+            timestamp: 0,
+        });
+
+        let mut selector = L1OriginSelector::new(cfg, provider);
+
+        // First call: set current to block 0.
+        let unsafe_head_epoch0 = L2BlockInfo {
+            block_info: BlockInfo {
+                hash: B256::ZERO,
+                number: 0,
+                timestamp: 0,
+                ..Default::default()
+            },
+            l1_origin: NumHash { number: 0, hash: B256::ZERO },
+            seq_num: 0,
+        };
+        let _ = selector.next_l1_origin(unsafe_head_epoch0, false).await.unwrap();
+
+        // Second call: reference a non-existent L1 origin hash, triggering the else branch.
+        let unsafe_head_missing = L2BlockInfo {
+            block_info: BlockInfo {
+                hash: B256::ZERO,
+                number: 1,
+                timestamp: L2_BLOCK_TIME,
+                ..Default::default()
+            },
+            l1_origin: NumHash { number: 99, hash: B256::with_last_byte(0xFF) },
+            seq_num: 0,
+        };
+
+        let result = selector.next_l1_origin(unsafe_head_missing, false).await;
+        assert!(matches!(
+            result,
+            Err(L1OriginSelectorError::OriginNotFound(hash)) if hash == B256::with_last_byte(0xFF)
+        ));
+    }
 }
```
