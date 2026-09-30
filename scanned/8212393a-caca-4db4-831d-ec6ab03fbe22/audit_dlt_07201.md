# [?] Fix deadlock in chain tip watch channel (#3378)

## Summary
Severity: Unknown
Chain: Zcash
Component: ZcashFoundation/zebra
Published: 2022-01-24
Source: https://github.com/ZcashFoundation/zebra/commit/ebd94b2e60c01f74042db4a5899b294659d5f207
Type: security-commit

## Details
Fix deadlock in chain tip watch channel (#3378)

* Avoid sequential borrows in `LatestChainTip`

Calling `watch::Receiver::borrow` more than once in the same scope can
cause a deadlock. The instrumented methods were calling `borrow` twice
to record instrumented fields.

This refactors things to ensure `borrow` is only called once to record
the fields and perform any actions with the chain tip block.

* Remove `borrow()` calls in `ChainTipChange`

Refactor to use a `LatestChainTip` instance instead, which safely
protects the internal `watch::Receiver` so that it is not borrowed more
than once in the same scope.

* Add a paragraph to the Asynchronous guide

Warn against using two borrow guards in the same scope, and describe why
that can lead to a deadlock.

## Patch
### book/src/dev/rfcs/0011-async-rust-in-zebra.md
```diff
@@ -564,6 +564,13 @@ For example, [`tokio::sync::watch::Receiver::borrow`](https://docs.rs/tokio/1.15
 holds a read lock, so the borrowed data should always be cloned.
 Use `Arc` for efficient clones if needed.
 
+Never have two active watch borrow guards in the same scope, because that can cause a deadlock. The
+`watch::Sender` may start acquiring a write lock while the first borrow guard is active but the
+second one isn't. That means that the first read lock was acquired, but the second never will be
+because starting to acquire the write lock blocks any other read locks from being acquired. At the
+same time, the write lock will also never finish acquiring, because it waits for all read locks to
+be released, and the first read lock won't be released before the second read lock is acquired.
+
 In all of these cases:
 - make critical sections as short as possible, and
 - do not depend on other tasks or locks inside the critical section.
```

### zebra-state/src/service/chain_tip.rs
```diff
@@ -131,8 +131,8 @@ impl ChainTipSender {
             active_value: None,
         };
 
-        let current = LatestChainTip::new(receiver.clone());
-        let change = ChainTipChange::new(receiver, network);
+        let current = LatestChainTip::new(receiver);
+        let change = ChainTipChange::new(current.clone(), network);
 
         sender.update(initial_tip);
 
@@ -246,47 +246,80 @@ impl LatestChainTip {
     fn new(receiver: watch::Receiver<ChainTipData>) -> Self {
         Self { receiver }
     }
+
+    /// Retrieve a result `R` from the current [`ChainTipBlock`], if it's available.
+    ///
+    /// This helper method is a shorter way to borrow the value from the [`watch::Receiver`] and
+    /// extract some information from it, while also adding the current chain tip block's fields as
+    /// records to the current span.
+    ///
+    /// A single read lock is kept during the execution of the method, and it is dropped at the end
+    /// of it.
+    ///
+    /// # Correctness
+    ///
+    /// To prevent deadlocks:
+    ///
+    /// - `receiver.borrow()` should not be called before this method while in the same scope.
+    /// - `receiver.borrow()` should not be called inside the `action` closure.
+    ///
+    /// It is important to avoid calling `borrow` more than once in the same scope, which
+    /// effectively tries to acquire two read locks to the shared data in the watch channel. If
+    /// that is done, there's a chance that the [`watch::Sender`] tries to send a value, which
+    /// starts acquiring a write-lock, and prevents further read-locks from being acquired until
+    /// the update is finished.
+    ///
+    /// What can happen in that scenario is:
+    ///
+    /// 1. The receiver manages to acquire a read-lock for the first `borrow`
+    /// 2. The sender starts acquiring the write-lock
+    /// 3. The receiver fails to acquire a read-lock for the second `borrow`
+    ///
+    /// Now both the sender and the receivers hang, because the sender won't release the lock until
+    /// it can update the value, and the receiver won't release its first read-lock until it
+    /// acquires the second read-lock and finishes what it's doing.
+    fn with_chain_tip_block<R>(&self, action: impl FnOnce(&ChainTipBlock) -> R) -> Option<R> {
+        let span = tracing::Span::current();
+        let borrow_guard = self.receiver.borrow();
+        let chain_tip_block = borrow_guard.as_ref();
+
+        span.record(
+            "height",
+            &tracing::field::debug(chain_tip_block.map(|block| block.height)),
+        );
+        span.record(
+            "hash",
+            &tracing::field::debug(chain_tip_block.map(|block| block.hash)),
+        );
+        span.record(
+            "transaction_count",
+            &tracing::field::debug(chain_tip_block.map(|block| block.transaction_hashes.len())),
+        );
+
+        chain_tip_block.map(action)
+    }
 }
 
 impl ChainTip for LatestChainTip {
     /// Return the height of the best chain tip.
-    #[instrument(
-        skip(self),
-        fields(
-            height = ?self.receiver.borrow().as_ref().map(|block| block.height),
-            hash = ?self.receiver.borrow().as_ref().map(|block| block.hash),
-        ))]
+    #[instrument(skip(self))]
     fn best_tip_height(&self) -> Option<block::Height> {
-        self.receiver.borrow().as_ref().map(|block| block.height)
+        self.with_chain_tip_block(|block| block.height)
     }
 
     /// Return the block hash of the best chain tip.
-    #[instrument(
-        skip(self),
-        fields(
-            height = ?self.receiver.borrow().as_ref().map(|block| block.height),
-            hash = ?self.receiver.borrow().as_ref().map(|block| block.hash),
-        ))]
+    #[instrument(skip(self))]
     fn best_tip_hash(&self) -> Option<block::Hash> {
-        self.receiver.borrow().as_ref().map(|block| block.hash)
+        self.with_chain_tip_block(|block| block.hash)
     }
 
     /// Return the mined transaction IDs of the transactions in the best chain tip block.
     ///
     /// All transactions with these mined IDs should be rejected from the mempool,
     /// even if their authorizing data is different.
-    #[instrument(
-        skip(self),
-        fields(
-            height = ?self.receiver.borrow().as_ref().map(|block| block.height),
-            hash = ?self.receiver.borrow().as_ref().map(|block| block.hash),
-            transaction_count = ?self.receiver.borrow().as_ref().map(|block| block.transaction_hashes.len()),
-        ))]
+    #[instrument(skip(self))]
     fn best_tip_mined_transaction_ids(&self) -> Arc<[transaction::Hash]> {
-        self.receiver
-            .borrow()
-            .as_ref()
-            .map(|block| block.transaction_hashes.clone())
+        self.with_chain_tip_block(|block| block.transaction_hashes.clone())
             .unwrap_or_else(|| Arc::new([]))
     }
 }
@@ -306,7 +339,7 @@ impl ChainTip for LatestChainTip {
 #[derive(Debug)]
 pub struct ChainTipChange {
     /// The receiver for the current chain tip's data.
-    receiver: watch::Receiver<ChainTipData>,
+    latest_chain_tip: LatestChainTip,
 
     /// The most recent [`block::Hash`] provided by this instance.
     ///
@@ -377,8 +410,6 @@ impl ChainTipChange {
     #[instrument(
         skip(self),
         fields(
-            current_height = ?self.receiver.borrow().as_ref().map(|block| block.height),
-            current_hash = ?self.receiver.borrow().as_ref().map(|block| block.hash),
             last_change_hash = ?self.last_change_hash,
             network = ?self.network,
         ))]
@@ -400,25 +431,25 @@ impl ChainTipChange {
     #[instrument(
         skip(self),
         fields(
-            current_height = ?self.receiver.borrow().as_ref().map(|block| block.height),
-            current_hash = ?self.receiver.borrow().as_ref().map(|block| block.hash),
             last_change_hash = ?self.last_change_hash,
             network = ?self.network,
         ))]
     pub fn last_tip_change(&mut self) -> Option<TipAction> {
-        // Obtain the tip block.
-        let block = self.best_tip_block()?;
+        let block = self.latest_chain_tip.with_chain_tip_block(|block| {
+            if Some(block.hash) != self.last_change_hash {
+                Some(block.clone())
+            } else {
+                // Ignore an unchanged tip.
+                None
+            }
+        })??;
 
-        // Ignore an unchanged tip.
-        if Some(block.hash) == self.last_change_hash {
-            return None;
-        }
+        let block_hash = block.hash;
+        let tip_action = self.action(block);
 
-        let action = self.action(block.clone());
+        self.last_change_hash = Some(block_hash);
 
-        self.last_change_hash = Some(block.hash);
-
-        Some(action)
+        Some(tip_action)
     }
 
     /// Return an action based on `block` and the last change we returned.
@@ -466,10 +497,10 @@ impl ChainTipChange {
         }
     }
 
-    /// Create a new [`ChainTipChange`] from a watch channel receiver and [`Network`].
-    fn new(receiver: watch::Receiver<ChainTipData>, network: Network) -> Self {
+    /// Create a new [`ChainTipChange`] from a [`LatestChainTip`] receiver and [`Network`].
+    fn new(latest_chain_tip: LatestChainTip, network: Network) -> Self {
         Self {
-            receiver,
+            latest_chain_tip,
             last_change_hash: None,
             network,
         }
@@ -485,37 +516,38 @@ impl ChainTipChange {
             // after the change notification.
             // Any block update after the change will do,
             // we'll catch up with the tip after the next change.
-            self.receiver.changed().await?;
-
-            // Wait until there is actually Some block,
-            // so we don't have `Option`s inside `TipAction`s.
-            if let Some(block) = self.best_tip_block() {
-                // Wait until we have a new block
-                //
-                // last_tip_change() updates last_change_hash, but it doesn't call receiver.changed().
-                // So code that uses both sync and async methods can have spurious pending changes.
-                //
-                // TODO: use `receiver.borrow_and_update()` in `best_tip_block()`,
-                //       once we upgrade to tokio 1.0 (#2200)
-                //       and remove this extra check
-                if Some(block.hash) != self.last_change_hash {
-                    return Ok(block);
-                }
+            self.latest_chain_tip.receiver.changed().await?;
+
+            // Wait until we have a new block
+            //
+            // last_tip_change() updates last_change_hash, but it doesn't call receiver.changed().
+            // So code that uses both sync and async methods can have spurious pending changes.
+            //
+            // TODO: use `receiver.borrow_and_update()` in `with_chain_tip_block()`,
+            //       once we upgrade to tokio 1.0 (#2200)
+            //       and remove this extra check
+            let new_block = self
+                .latest_chain_tip
+                .with_chain_tip_block(|block| {
+                    if Some(block.hash) != self.last_change_hash {
+                        Some(block.clone())
+                    } else {
+                        None
+                    }
+                })
+                .flatten();
+
+            if let Some(block) = new_block {
+                return Ok(block);
             }
         }
     }
-
-    /// Return the current best [`ChainTipBlock`],
-    /// or `None` if no block has been committed yet.
-    fn best_tip_block(&self) -> Option<ChainTipBlock> {
-        self.receiver.borrow().clone()
-    }
 }
 
 impl Clone for ChainTipChange {
     fn clone(&self) -> Self {
         Self {
-            receiver: self.receiver.clone(),
+            latest_chain_tip: self.latest_chain_tip.clone(),
 
             // clear the previous change hash, so the first action is a reset
             last_change_hash: None,
```
