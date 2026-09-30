# [?] fix(mirror): fix a crash in the mirror traffic generator (#12168)

## Summary
Severity: Unknown
Chain: NEAR
Component: near/nearcore
Published: 2024-10-04
Source: https://github.com/near/nearcore/commit/a9bf310048cc036537e59394ce4d6cd414dfd966
Type: security-commit

## Details
fix(mirror): fix a crash in the mirror traffic generator (#12168)

In queue_block(), we lock the TxTracker struct and add some data to it
related to the current block's worth of transactions we're queuing. This
includes references to transactions that will be queued to the
tx_block_queue passed to that function. But we actually add these to the
tx_block_queue only after we release the lock on the TxTracker, so
another thread that's waiting for that lock might start looking through
it and trying to find the transactions whose references were added to
the TxTracker in queue_block(), but before these blocks get added to the
tx_block_queue. This leads to a possible crash in get_tx() if we try to
look up one of these transactions:

```
thread 'actix-rt|system:0|arbiter:0' panicked at tools/mirror/src/chain_tracker.rs:366:14:
called `Result::unwrap()` on an `Err` value: 100
stack backtrace:
   0: rust_begin_unwind
   1: core::panicking::panic_fmt
   2: core::result::unwrap_failed
   3: near_mirror::chain_tracker::TxTracker::get_tx
   4: near_mirror::chain_tracker::TxTracker::try_set_nonces
```

We can fix it by keeping the lock on the TxTracker until after we queue
this new batch of transactions onto the tx_block_queue. This is a more
involved change than it would seem, because we can't hold the lock
across await points, and so we need to add some logic to do the async
operations before we take the lock. In the end we get logic here that is
closer to what it looked like before
https://github.com/near/nearcore/pull/11916. In the future it would make
things simpler to move the tx_block_queue back into the TxTracker, but
for now this should work

## Patch
### tools/mirror/src/chain_tracker.rs
```diff
@@ -240,46 +240,66 @@ impl TxTracker {
         }
     }
 
-    async fn initialize_target_nonce(
-        lock: &Mutex<Self>,
+    // Makes sure that there's something written in the DB for this access key.
+    // This function is called before calling initialize_target_nonce(), which sets
+    // in-memory data associated with this nonce. It would make sense to do this part at the same time,
+    // But since we can't hold the lock across awaits, we need to do this separately first if we want to
+    // keep the lock on Self for the entirety of sections of code that make updates to it.
+    //
+    // So this function must be called before calling initialize_target_nonce() for a given access key
+    async fn store_target_nonce(
         target_view_client: &Addr<ViewClientActor>,
         db: &DB,
         access_key: &(AccountId, PublicKey),
+    ) -> anyhow::Result<()> {
+        if crate::read_target_nonce(db, &access_key.0, &access_key.1)?.is_some() {
+            return Ok(());
+        }
+        let nonce =
+            crate::fetch_access_key_nonce(target_view_client, &access_key.0, &access_key.1).await?;
+        let t = LatestTargetNonce { nonce, pending_outcomes: HashSet::new() };
+        crate::put_target_nonce(db, &access_key.0, &access_key.1, &t)?;
+
+        Ok(())
+    }
+
+    fn initialize_target_nonce(
+        &mut self,
+        db: &DB,
+        access_key: &(AccountId, PublicKey),
         source_height: Option<BlockHeight>,
     ) -> anyhow::Result<()> {
-        let info = match crate::read_target_nonce(db, &access_key.0, &access_key.1)? {
-            Some(t) => NonceInfo {
-                target_nonce: TargetNonce {
-                    nonce: t.nonce,
-                    pending_outcomes: t
-                        .pending_outcomes
-                        .into_iter()
-                        .map(NonceUpdater::ChainObjectId)
-                        .collect(),
-                },
-                last_height: source_height,
-                txs_awaiting_nonce: BTreeSet::new(),
-                queued_txs: BTreeSet::new(),
+        // We unwrap() because store_target_nonce() must be called before calling this function.
+        let t = crate::read_target_nonce(db, &access_key.0, &access_key.1)?.unwrap();
+        let info = NonceInfo {
+            target_nonce: TargetNonce {
+                nonce: t.nonce,
+                pending_outcomes: t
+                    .pending_outcomes
+                    .into_iter()
+                    .map(NonceUpdater::ChainObjectId)
+                    .collect(),
             },
-            None => {
-                let nonce =
-                    crate::fetch_access_key_nonce(target_view_client, &access_key.0, &access_key.1)
-                        .await?;
-                let t = LatestTargetNonce { nonce, pending_outcomes: HashSet::new() };
-                crate::put_target_nonce(db, &access_key.0, &access_key.1, &t)?;
-                NonceInfo {
-                    target_nonce: TargetNonce { nonce: t.nonce, pending_outcomes: HashSet::new() },
-                    last_height: source_height,
-                    txs_awaiting_nonce: BTreeSet::new(),
-                    queued_txs: BTreeSet::new(),
-                }
-            }
+            last_height: source_height,
+            txs_awaiting_nonce: BTreeSet::new(),
+            queued_txs: BTreeSet::new(),
         };
-        let mut me = lock.lock().unwrap();
-        me.nonces.insert(access_key.clone(), info);
+        self.nonces.insert(access_key.clone(), info);
         Ok(())
     }
 
+    fn get_target_nonce<'a>(
+        &'a mut self,
+        db: &DB,
+        access_key: &(AccountId, PublicKey),
+        source_height: Option<BlockHeight>,
+    ) -> anyhow::Result<&'a mut NonceInfo> {
+        if !self.nonces.contains_key(access_key) {
+            self.initialize_target_nonce(db, &access_key, source_height)?;
+        }
+        Ok(self.nonces.get_mut(access_key).unwrap())
+    }
+
     pub(crate) async fn next_nonce(
         lock: &Mutex<Self>,
         target_view_client: &Addr<ViewClientActor>,
@@ -290,12 +310,9 @@ impl TxTracker {
     ) -> anyhow::Result<TargetNonce> {
         let source_height = Some(source_height);
         let access_key = (signer_id.clone(), public_key.clone());
-        if !lock.lock().unwrap().nonces.contains_key(&access_key) {
-            Self::initialize_target_nonce(lock, target_view_client, db, &access_key, source_height)
-                .await?;
-        }
+        Self::store_target_nonce(target_view_client, db, &access_key).await?;
         let mut me = lock.lock().unwrap();
-        let info = me.nonces.get_mut(&access_key).unwrap();
+        let info = me.get_target_nonce(db, &access_key, source_height).unwrap();
         if source_height > info.last_height {
             info.last_height = source_height;
         }
@@ -320,16 +337,16 @@ impl TxTracker {
         secret_key: &SecretKey,
     ) -> anyhow::Result<TargetNonce> {
         let access_key = (signer_id.clone(), public_key.clone());
-        if !lock.lock().unwrap().nonces.contains_key(&access_key) {
-            Self::initialize_target_nonce(lock, target_view_client, db, &access_key, None).await?;
-            let mut me = lock.lock().unwrap();
+        Self::store_target_nonce(target_view_client, db, &access_key).await?;
+        let mut me = lock.lock().unwrap();
+        if !me.nonces.contains_key(&access_key) {
+            me.initialize_target_nonce(db, &access_key, None)?;
             let info = me.nonces.get_mut(&access_key).unwrap();
             if let Some(nonce) = &mut info.target_nonce.nonce {
                 *nonce += 1;
             }
             return Ok(info.target_nonce.clone());
         }
-        let mut me = lock.lock().unwrap();
         let mut first_nonce = None;
         let txs = me.nonces.get(&access_key).unwrap().queued_txs.clone();
         if !txs.is_empty() {
@@ -369,79 +386,82 @@ impl TxTracker {
         &mut chunk.txs[tx_ref.tx_idx]
     }
 
-    async fn insert_access_key_updates(
-        lock: &Mutex<Self>,
-        target_view_client: &Addr<ViewClientActor>,
+    // This function sets in-memory info for any access keys that will be touched by this transaction (`tx_ref`).
+    // store_target_nonce() must have been called beforehand for each of these.
+    fn insert_access_key_updates(
+        &mut self,
         db: &DB,
         tx_ref: &TxRef,
         nonce_updates: &HashSet<(AccountId, PublicKey)>,
         source_height: BlockHeight,
     ) -> anyhow::Result<()> {
         let source_height = Some(source_height);
         for access_key in nonce_updates.iter() {
-            if !lock.lock().unwrap().nonces.contains_key(access_key) {
-                Self::initialize_target_nonce(
-                    lock,
-                    target_view_client,
-                    db,
-                    &access_key,
-                    source_height,
-                )
-                .await?;
-            }
-            let mut me = lock.lock().unwrap();
-            let info = me.nonces.get_mut(&access_key).unwrap();
+            let info = self.get_target_nonce(db, &access_key, source_height).unwrap();
 
             if info.last_height < source_height {
                 info.last_height = source_height;
             }
             info.target_nonce.pending_outcomes.insert(NonceUpdater::TxRef(tx_ref.clone()));
         }
         if !nonce_updates.is_empty() {
-            let mut me = lock.lock().unwrap();
-            assert!(me
+            assert!(self
                 .updater_to_keys
                 .insert(NonceUpdater::TxRef(tx_ref.clone()), nonce_updates.clone())
                 .is_none());
         }
         Ok(())
     }
 
-    // This is the non-async portion of queue_block() that returns a list of access key updates we need
-    // to call insert_access_key_updates() for, which we'll do after calling this function. Otherwise
-    // we would have to lock and unlock the mutex on every transaction to avoid holding it across await points
-    fn queue_txs<'a>(
-        lock: &Mutex<Self>,
-        block: &'a MappedBlock,
-    ) -> anyhow::Result<Vec<(TxRef, &'a HashSet<(AccountId, PublicKey)>)>> {
-        let mut nonce_updates = Vec::new();
-        let mut me = lock.lock().unwrap();
-        me.height_queued = Some(block.source_height);
-        me.next_heights.pop_front().unwrap();
+    async fn store_access_key_updates(
+        block: &MappedBlock,
+        target_view_client: &Addr<ViewClientActor>,
+        db: &DB,
+    ) -> anyhow::Result<()> {
+        for c in block.chunks.iter() {
+            for tx in c.txs.iter() {
+                let updates = match tx {
+                    crate::TargetChainTx::Ready(tx) => &tx.nonce_updates,
+                    crate::TargetChainTx::AwaitingNonce(tx) => &tx.nonce_updates,
+                };
+                for access_key in updates.iter() {
+                    Self::store_target_nonce(target_view_client, db, access_key).await?;
+                }
+            }
+        }
+        Ok(())
+    }
+
+    fn queue_txs(&mut self, block: &MappedBlock, db: &DB) -> anyhow::Result<()> {
+        self.height_queued = Some(block.source_height);
+        self.next_heights.pop_front().unwrap();
 
         for c in block.chunks.iter() {
             if !c.txs.is_empty() {
-                me.nonempty_height_queued = Some(block.source_height);
+                self.nonempty_height_queued = Some(block.source_height);
             }
             for (tx_idx, tx) in c.txs.iter().enumerate() {
                 let tx_ref =
                     TxRef { source_height: block.source_height, shard_id: c.shard_id, tx_idx };
                 match tx {
                     crate::TargetChainTx::Ready(tx) => {
-                        let info = me
+                        let info = self
                             .nonces
                             .get_mut(&(
                                 tx.target_tx.transaction.signer_id().clone(),
                                 tx.target_tx.transaction.public_key().clone(),
                             ))
                             .unwrap();
                         info.queued_txs.insert(tx_ref.clone());
-                        if !tx.nonce_updates.is_empty() {
-                            nonce_updates.push((tx_ref, &tx.nonce_updates));
-                        }
+                        self.insert_access_key_updates(
+                            db,
+                            &tx_ref,
+                            &tx.nonce_updates,
+                            block.source_height,
+                        )?;
                     }
                     crate::TargetChainTx::AwaitingNonce(tx) => {
-                        let info = me
+                        let info = self
                             .nonces
                             .get_mut(&(
                                 tx.target_tx.signer_id().clone(),
@@ -450,14 +470,17 @@ impl TxTracker {
                             .unwrap();
                         info.txs_awaiting_nonce.insert(tx_ref.clone());
                         info.queued_txs.insert(tx_ref.clone());
-                        if !tx.nonce_updates.is_empty() {
-                            nonce_updates.push((tx_ref, &tx.nonce_updates));
-                        }
+                        self.insert_access_key_updates(
+                            db,
+                            &tx_ref,
+                            &tx.nonce_updates,
+                            block.source_height,
+                        )?;
                     }
                 };
             }
         }
-        Ok(nonce_updates)
+        Ok(())
     }
 
     pub(crate) async fn queue_block(
@@ -467,18 +490,9 @@ impl TxTracker {
         target_view_client: &Addr<ViewClientActor>,
         db: &DB,
     ) -> anyhow::Result<()> {
-        let key_updates = Self::queue_txs(lock, &block)?;
-        for (tx_ref, nonce_updates) in key_updates {
-            Self::insert_access_key_updates(
-                lock,
-                target_view_client,
-                db,
-                &tx_ref,
-                nonce_updates,
-                block.source_height,
-            )
-            .await?;
-        }
+        Self::store_access_key_updates(&block, target_view_client, db).await?;
+        let mut me = lock.lock().unwrap();
+        me.queue_txs(&block, db)?;
         tx_block_queue.lock().unwrap().push_back(block);
         Ok(())
     }
```

### tools/mirror/src/lib.rs
```diff
@@ -1989,6 +1989,9 @@ impl<T: ChainAccess> TxMirror<T> {
         let tracker2 = tracker.clone();
         let index_target_thread = actix::Arbiter::new();
 
+        // TODO: Consider moving this back to the TxTracker struct. Separating these made certain things easier, but now it
+        // means we need to be careful about the lock order to avoid deadlocks. We keep the convention that the TxTracker is
+        // always locked first.
         let tx_block_queue = Arc::new(Mutex::new(VecDeque::new()));
 
         let tx_block_queue2 = tx_block_queue.clone();
```
