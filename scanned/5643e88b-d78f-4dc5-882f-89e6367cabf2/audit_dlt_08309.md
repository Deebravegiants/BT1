# [?] bug: fix deadlock when having multiple websocket listeners in `anchor-client` (#4250)

## Summary
Severity: Unknown
Chain: Solana
Component: otter-sec/anchor
Published: 2026-03-24
Source: https://github.com/otter-sec/anchor/commit/fa694cea498fea9bef974ce5d4e0858ca4da5cef
Type: security-commit

## Details
bug: fix deadlock when having multiple websocket listeners in `anchor-client` (#4250)

## Patch
### CHANGELOG.md
```diff
@@ -13,6 +13,7 @@ The minor version will be incremented upon a breaking change and the patch versi
 ### Features
 
 ### Fixes
+- client: Fix deadlock when having multiple websocket listeners ([#4250](https://github.com/solana-foundation/anchor/pull/4250)).
 
 ### Breaking
 
```

### Cargo.lock
```diff
@@ -255,6 +255,7 @@ dependencies = [
  "solana-account-decoder",
  "solana-commitment-config",
  "solana-instruction",
+ "solana-keypair",
  "solana-program",
  "solana-pubsub-client",
  "solana-rpc-client",
@@ -264,6 +265,7 @@ dependencies = [
  "solana-transaction",
  "thiserror 1.0.69",
  "tokio",
+ "tokio-tungstenite",
  "url",
 ]
 
```

### client/Cargo.toml
```diff
@@ -37,3 +37,7 @@ solana-transaction.workspace = true
 thiserror = "1"
 tokio = { version = "1", features = ["rt", "sync"] }
 url = "2"
+
+[dev-dependencies]
+solana-keypair.workspace = true
+tokio-tungstenite = "0.28"
```

### client/src/blocking.rs
```diff
@@ -12,10 +12,10 @@ use solana_signature::Signature;
 use solana_signer::Signer;
 use solana_transaction::Transaction;
 
-use std::{marker::PhantomData, ops::Deref, sync::Arc};
+use std::{marker::PhantomData, ops::Deref};
 use tokio::{
     runtime::{Builder, Handle},
-    sync::RwLock,
+    sync::OnceCell,
 };
 
 impl EventUnsubscriber<'_> {
@@ -43,7 +43,7 @@ impl<C: Deref<Target = impl Signer> + Clone> Program<C> {
         Ok(Self {
             program_id,
             cfg,
-            sub_client: Arc::new(RwLock::new(None)),
+            sub_client: OnceCell::new(),
             internal_rpc_client: rpc_client,
             rt,
         })
```

### client/src/lib.rs
```diff
@@ -89,12 +89,10 @@ use std::pin::Pin;
 use std::sync::Arc;
 use std::vec::IntoIter;
 use thiserror::Error;
+use tokio::sync::OnceCell;
 use tokio::{
     runtime::Handle,
-    sync::{
-        mpsc::{unbounded_channel, UnboundedReceiver},
-        RwLock,
-    },
+    sync::mpsc::{unbounded_channel, UnboundedReceiver},
     task::JoinHandle,
 };
 
@@ -230,7 +228,7 @@ impl EventUnsubscriber<'_> {
 pub struct Program<C> {
     program_id: Pubkey,
     cfg: Config<C>,
-    sub_client: Arc<RwLock<Option<PubsubClient>>>,
+    sub_client: OnceCell<Arc<PubsubClient>>,
     #[cfg(not(feature = "async"))]
     rt: tokio::runtime::Runtime,
     internal_rpc_client: AsyncRpcClient,
@@ -297,20 +295,6 @@ impl<C: Deref<Target = impl Signer> + Clone> Program<C> {
         })
     }
 
-    async fn init_sub_client_if_needed(&self) -> Result<(), ClientError> {
-        let lock = &self.sub_client;
-        let mut client = lock.write().await;
-
-        if client.is_none() {
-            let sub_client = PubsubClient::new(self.cfg.cluster.ws_url())
-                .await
-                .map_err(Box::new)?;
-            *client = Some(sub_client);
-        }
-
-        Ok(())
-    }
-
     async fn on_internal<T: anchor_lang::Event + anchor_lang::AnchorDeserialize>(
         &self,
         mut f: impl FnMut(&EventContext, T) + Send + 'static,
@@ -321,41 +305,45 @@ impl<C: Deref<Target = impl Signer> + Clone> Program<C> {
         ),
         ClientError,
     > {
-        self.init_sub_client_if_needed().await?;
+        let client = self
+            .sub_client
+            .get_or_try_init(|| async {
+                PubsubClient::new(self.cfg.cluster.ws_url())
+                    .await
+                    .map(Arc::new)
+                    .map_err(|e| ClientError::SolanaClientPubsubError(Box::new(e)))
+            })
+            .await?
+            .clone();
+
         let (tx, rx) = unbounded_channel::<_>();
         let config = RpcTransactionLogsConfig {
             commitment: self.cfg.options,
         };
         let program_id_str = self.program_id.to_string();
         let filter = RpcTransactionLogsFilter::Mentions(vec![program_id_str.clone()]);
 
-        let lock = Arc::clone(&self.sub_client);
-
         let handle = tokio::spawn(async move {
-            if let Some(ref client) = *lock.read().await {
-                let (mut notifications, unsubscribe) = client
-                    .logs_subscribe(filter, config)
-                    .await
-                    .map_err(Box::new)?;
-
-                tx.send(unsubscribe).map_err(|e| {
-                    ClientError::SolanaClientPubsubError(Box::new(
-                        PubsubClientError::RequestFailed {
-                            message: "Unsubscribe failed".to_string(),
-                            reason: e.to_string(),
-                        },
-                    ))
-                })?;
-
-                while let Some(logs) = notifications.next().await {
-                    let ctx = EventContext {
-                        signature: logs.value.signature.parse().unwrap(),
-                        slot: logs.context.slot,
-                    };
-                    let events = parse_logs_response(logs, &program_id_str)?;
-                    for e in events {
-                        f(&ctx, e);
-                    }
+            let (mut notifications, unsubscribe) = client
+                .logs_subscribe(filter, config)
+                .await
+                .map_err(Box::new)?;
+
+            tx.send(unsubscribe).map_err(|e| {
+                ClientError::SolanaClientPubsubError(Box::new(PubsubClientError::RequestFailed {
+                    message: "Unsubscribe failed".to_string(),
+                    reason: e.to_string(),
+                }))
+            })?;
+
+            while let Some(logs) = notifications.next().await {
+                let ctx = EventContext {
+                    signature: logs.value.signature.parse().unwrap(),
+                    slot: logs.context.slot,
+                };
+                let events = parse_logs_response(logs, &program_id_str)?;
+                for e in events {
+                    f(&ctx, e);
                 }
             }
             Ok::<(), ClientError>(())
@@ -744,7 +732,10 @@ fn parse_logs_response<T: anchor_lang::Event + anchor_lang::AnchorDeserialize>(
 
 #[cfg(test)]
 mod tests {
+    use futures::{SinkExt, StreamExt};
     use solana_rpc_client_api::response::RpcResponseContext;
+    use std::sync::atomic::{AtomicU64, Ordering};
+    use tokio_tungstenite::tungstenite::Message;
 
     // Creating a mock struct that implements `anchor_lang::events`
     // for type inference in `test_logs`
@@ -916,4 +907,92 @@ mod tests {
 
         Ok(())
     }
+
+    /// Regression test that registering multiple event listeners does not deadlock.
+    #[test]
+    fn multiple_listeners_no_deadlock() {
+        // Spin up a tiny mock websocket server that responds to `logsSubscribe`
+        // JSON-RPC requests with a valid subscription id.
+        let rt = tokio::runtime::Builder::new_multi_thread()
+            .enable_all()
+            .build()
+            .unwrap();
+
+        let (addr_tx, addr_rx) = std::sync::mpsc::channel();
+
+        rt.spawn(async move {
+            let listener = tokio::net::TcpListener::bind("127.0.0.1:0").await.unwrap();
+            let addr = listener.local_addr().unwrap();
+            addr_tx.send(addr).unwrap();
+
+            static SUB_ID: AtomicU64 = AtomicU64::new(0);
+
+            loop {
+                let (stream, _) = listener.accept().await.unwrap();
+                tokio::spawn(async move {
+                    let mut ws = tokio_tungstenite::accept_async(stream).await.unwrap();
+                    while let Some(Ok(Message::Text(_))) = ws.next().await {
+                        let sub_id = SUB_ID.fetch_add(1, Ordering::Relaxed);
+                        // The PubsubClient sends sequential integer ids starting at 0.
+                        let resp =
+                            format!(r#"{{"jsonrpc":"2.0","result":{sub_id},"id":{sub_id}}}"#);
+                        ws.send(Message::Text(resp.into())).await.unwrap();
+                    }
+                });
+            }
+        });
+
+        let addr = addr_rx.recv().unwrap();
+        let ws_url = format!("ws://{}", addr);
+
+        let client = super::Client::new(
+            super::Cluster::Custom(ws_url.clone(), ws_url),
+            std::sync::Arc::new(solana_keypair::Keypair::new()),
+        );
+        let program = client.program(Pubkey::new_unique()).unwrap();
+
+        // With the old RwLock-based code, the second call would deadlock.
+        // Use a timeout to ensure the test fails instead of hanging forever.
+        let (done_tx, done_rx) = std::sync::mpsc::channel();
+        let handle = std::thread::spawn(move || {
+            #[cfg(not(feature = "async"))]
+            {
+                let _listener1 = program
+                    .on::<MockEvent>(|_ctx, _event| {})
+                    .expect("first listener");
+
+                let _listener2 = program
+                    .on::<MockEvent>(|_ctx, _event| {})
+                    .expect("second listener");
+            }
+
+            #[cfg(feature = "async")]
+            {
+                let rt = tokio::runtime::Builder::new_current_thread()
+                    .enable_all()
+                    .build()
+                    .unwrap();
+                rt.block_on(async {
+                    let _listener1 = program
+                        .on::<MockEvent>(|_ctx, _event| {})
+                        .await
+                        .expect("first listener");
+
+                    let _listener2 = program
+                        .on::<MockEvent>(|_ctx, _event| {})
+                        .await
+                        .expect("second listener");
+                });
+            }
+
+            let _ = done_tx.send(());
+        });
+
+        // If this times out, the deadlock is still present.
+        done_rx
+            .recv_timeout(std::time::Duration::from_secs(5))
+            .expect("registering two listeners should not deadlock");
+
+        handle.join().unwrap();
+    }
 }
```

### client/src/nonblocking.rs
```diff
@@ -10,7 +10,7 @@ use solana_signature::Signature;
 use solana_signer::Signer;
 use solana_transaction::Transaction;
 use std::{marker::PhantomData, ops::Deref, sync::Arc};
-use tokio::sync::RwLock;
+use tokio::sync::OnceCell;
 
 impl<'a> EventUnsubscriber<'a> {
     /// Unsubscribe gracefully.
@@ -51,7 +51,7 @@ impl<C: Deref<Target = impl Signer> + Clone> Program<C> {
         Ok(Self {
             program_id,
             cfg,
-            sub_client: Arc::new(RwLock::new(None)),
+            sub_client: OnceCell::new(),
             internal_rpc_client: rpc_client,
         })
     }
```
