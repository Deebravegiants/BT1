# [?] Fix miner forced-tx deadlock (#14453)

## Summary
Severity: Unknown
Chain: Tooling
Component: foundry-rs/foundry
Published: 2026-04-28
Source: https://github.com/foundry-rs/foundry/commit/5864f675120ce4f619871f9001555bc387331120
Type: security-commit

## Details
Fix miner forced-tx deadlock (#14453)

## Patch
### crates/anvil/src/eth/miner.rs
```diff
@@ -11,7 +11,7 @@ use parking_lot::{RawRwLock, RwLock, lock_api::RwLockWriteGuard};
 use std::{
     fmt,
     sync::Arc,
-    task::{Context, Poll, ready},
+    task::{Context, Poll},
     time::Duration,
 };
 use tokio::time::{Interval, MissedTickBehavior};
@@ -107,13 +107,13 @@ impl<T> Miner<T> {
         cx: &mut Context<'_>,
     ) -> Poll<Vec<Arc<PoolTransaction<T>>>> {
         self.inner.register(cx);
-        let next = ready!(self.mode.write().poll(pool, cx));
         if let Some(mut transactions) = self.force_transactions.take() {
-            transactions.extend(next);
-            Poll::Ready(transactions)
-        } else {
-            Poll::Ready(next)
+            if let Poll::Ready(next) = self.mode.write().poll(pool, cx) {
+                transactions.extend(next);
+            }
+            return Poll::Ready(transactions);
         }
+        self.mode.write().poll(pool, cx)
     }
 }
 
@@ -300,3 +300,44 @@ impl fmt::Debug for ReadyTransactionMiner {
             .finish_non_exhaustive()
     }
 }
+
+#[cfg(test)]
+mod tests {
+    use super::*;
+    use alloy_primitives::{Address, hex};
+    use alloy_rlp::Decodable;
+    use anvil_core::eth::transaction::PendingTransaction;
+    use foundry_primitives::FoundryTxEnvelope;
+    use futures::task::noop_waker;
+
+    fn forced_tx() -> PoolTransaction<FoundryTxEnvelope> {
+        let raw = hex::decode("f86b02843b9aca00830186a094d3e8763675e4c425df46cc3b5c0f6cbdac39604687038d7ea4c68000802ba00eb96ca19e8a77102767a41fc85a36afd5c61ccb09911cec5d3e86e193d9c5aea03a456401896b1b6055311536bf00a718568c744d8c1f9df59879e8350220ca18").unwrap();
+        let tx = FoundryTxEnvelope::decode(&mut &raw[..]).unwrap();
+        let sender: Address = "0x95222290DD7278Aa3Ddd389Cc1E1d165CC4BAfe5".parse().unwrap();
+        let pending = PendingTransaction::with_impersonated(tx, sender);
+        PoolTransaction::new(pending)
+    }
+
+    #[test]
+    fn poll_consumes_forced_transactions_before_mode_is_ready() {
+        let forced = forced_tx();
+        let forced_hash = forced.hash();
+
+        let pool = Arc::new(Pool::default());
+        let mut miner = Miner::new(MiningMode::None).with_forced_transactions(Some(vec![forced]));
+
+        let waker = noop_waker();
+        let mut cx = Context::from_waker(&waker);
+
+        let polled = miner.poll(&pool, &mut cx);
+        let txs = match polled {
+            Poll::Ready(txs) => txs,
+            Poll::Pending => panic!("expected forced transactions to be returned immediately"),
+        };
+        assert_eq!(txs.len(), 1);
+        assert_eq!(txs[0].hash(), forced_hash);
+
+        // Forced transactions are consumed exactly once.
+        assert!(miner.poll(&pool, &mut cx).is_pending());
+    }
+}
```
