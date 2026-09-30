# [?] fix(wallet): do not panic on an unknown consensus item variant

## Summary
Severity: Unknown
Chain: Fedimint
Component: fedimint/fedimint
Published: 2026-08-06
Source: https://github.com/fedimint/fedimint/commit/6dd783df3ead00a5438c3d33140348fe390f7726
Type: security-commit

## Details
fix(wallet): do not panic on an unknown consensus item variant

`WalletConsensusItem` carries an `#[encodable_default]` variant so that a
peer which predates a new item type can still decode a session log. That
makes decoding deliberately lenient: an unknown discriminant decodes into
`Default { variant, bytes }` rather than failing.

The classic wallet module then treated that variant as unreachable and
panicked on it. A consensus item's discriminant is chosen by whichever
peer proposes it, so a single malicious guardian -- well inside the `f`
of `n = 3f + 1` fault bound -- can put `Default { variant: 99 }` in its
AlephBFT unit batch and panic every honest guardian at once. The panic
unwinds a root task-group task, which trips `TaskPanicGuard::drop` and
exits the process, and because the item never reaches `AcceptedItemKey`
the persisted unit is replayed on restart, so the federation crash-loops
rather than recovering.

`f9034270d` fixed exactly this class one layer up, in the consensus
engine's own `ConsensusItem` dispatch, but the sweep never reached the
per-module handlers. Classic wallet was the last one left: ln, lnv2 and
walletv2 all already return an error here.

Rejecting the item instead of panicking is consensus-safe by the same
argument that fix used. Processing runs identically on every guardian,
so an unknown variant that reached consensus would have panicked all of
them at that ordered item and kept doing so on every restart. A
federation that is still running therefore has no such item in its
history, and the new rejection can only ever fire where the old
behaviour halted the federation instead.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_011hiuVTowKNSSYVtxwQTdP9

## Patch
### modules/fedimint-wallet-server/src/lib.rs
```diff
@@ -730,7 +730,7 @@ impl ServerModule for Wallet {
                 );
             }
             WalletConsensusItem::Default { variant, .. } => {
-                panic!("Received wallet consensus item with unknown variant {variant}");
+                bail!("Unknown wallet consensus item received, variant={variant}");
             }
         }
 
```

### modules/fedimint-wallet-tests/tests/tests.rs
```diff
@@ -1733,6 +1733,73 @@ async fn verify_auto_consensus_voting() -> anyhow::Result<()> {
     Ok(())
 }
 
+/// `WalletConsensusItem` carries an `#[encodable_default]` variant, so an
+/// unknown discriminant decodes successfully rather than failing. Consensus
+/// items are ordered before they are interpreted and a peer chooses its own,
+/// so a single peer can put an unknown variant in front of every other
+/// guardian. Rejecting the item has to be an error and never a panic: a panic
+/// here unwinds a root task-group task and exits the process, and because the
+/// item is never recorded as accepted it is replayed on restart.
+#[tokio::test(flavor = "multi_thread")]
+async fn unknown_consensus_item_variant_is_rejected_without_panicking() -> anyhow::Result<()> {
+    skip_if_not_wallet_test_group!("1");
+    let fixtures = fixtures();
+    let bitcoin = fixtures.bitcoin();
+    let _bitcoin = bitcoin.lock_exclusive().await;
+    let db = MemDatabase::new().into_database();
+    let task_group = TaskGroup::new();
+
+    let (wallet_server_cfg, _) = build_wallet_server_configs()?;
+    let module_instance_id = 1;
+
+    let wallet = fedimint_wallet_server::Wallet::new(
+        wallet_server_cfg[0].to_typed()?,
+        &db,
+        &task_group,
+        PeerId::from(0),
+        DynGlobalApi::new(
+            ConnectorRegistry::build_from_testing_env()?.bind().await?,
+            [(
+                PeerId::from(0),
+                SafeUrl::from_str("ws://dummy.xyz").unwrap(),
+            )]
+            .into(),
+            None,
+        )?
+        .with_module(module_instance_id),
+        ServerBitcoinRpcMonitor::new(
+            fixtures.server_bitcoin_rpc(),
+            Duration::from_secs(1),
+            &TaskGroup::new(),
+        ),
+    )
+    .await?;
+
+    let mut dbtx = db.begin_transaction().await;
+
+    let error = wallet
+        .process_consensus_item(
+            &mut dbtx
+                .to_ref_with_prefix_module_id(module_instance_id)
+                .0
+                .into_nc(),
+            fedimint_wallet_common::WalletConsensusItem::Default {
+                variant: 99,
+                bytes: vec![],
+            },
+            PeerId::from(1),
+        )
+        .await
+        .expect_err("an unknown consensus item variant must be rejected");
+
+    assert!(
+        error.to_string().contains("99"),
+        "the rejection should name the unknown variant, got: {error}"
+    );
+
+    Ok(())
+}
+
 async fn sync_wallet_to_block(
     dbtx: &mut DatabaseTransaction<'_>,
     wallet: &mut fedimint_wallet_server::Wallet,
```
