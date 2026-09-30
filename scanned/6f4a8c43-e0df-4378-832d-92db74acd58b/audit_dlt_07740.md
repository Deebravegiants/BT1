# [?] fix(node): ethstats conn/last_ping deadlock (#21463)

## Summary
Severity: Unknown
Chain: Ethereum
Component: paradigmxyz/reth
Published: 2026-02-11
Source: https://github.com/paradigmxyz/reth/commit/93d6b9782c14984a520d5b3cd6e988dc73d7c616
Type: security-commit

## Details
fix(node): ethstats conn/last_ping deadlock (#21463)

## Patch
### crates/node/ethstats/src/ethstats.rs
```diff
@@ -243,10 +243,17 @@ where
         let conn_ref = self.conn.clone();
         tokio::spawn(async move {
             sleep(PING_TIMEOUT).await;
-            let mut active = active_ping.lock().await;
-            if active.is_some() {
+            let timed_out = {
+                let mut active = active_ping.lock().await;
+                let timed_out = active.is_some();
+                if timed_out {
+                    *active = None;
+                }
+                timed_out
+            };
+
+            if timed_out {
                 debug!(target: "ethstats", "Ping timeout");
-                *active = None;
                 // Clear connection to trigger reconnect
                 if let Some(conn) = conn_ref.write().await.take() {
                     let _ = conn.close().await;
@@ -262,19 +269,22 @@ where
     /// Calculates the round-trip time from the last ping and sends it to
     /// the server. This is called when a pong response is received.
     async fn report_latency(&self) -> Result<(), EthStatsError> {
-        let conn = self.conn.read().await;
-        let conn = conn.as_ref().ok_or(EthStatsError::NotConnected)?;
+        let start = {
+            let mut active = self.last_ping.lock().await;
+            active.take()
+        };
 
-        let mut active = self.last_ping.lock().await;
-        if let Some(start) = active.take() {
+        if let Some(start) = start {
             let latency = start.elapsed().as_millis() as u64 / 2;
 
             debug!(target: "ethstats", "Reporting latency: {}ms", latency);
 
             let latency_msg = LatencyMsg { id: self.credentials.node_id.clone(), latency };
 
             let message = latency_msg.generate_latency_message();
-            conn.write_json(&message).await?
+            let conn = self.conn.read().await;
+            let conn = conn.as_ref().ok_or(EthStatsError::NotConnected)?;
+            conn.write_json(&message).await?;
         }
 
         Ok(())
@@ -750,7 +760,7 @@ mod tests {
     use reth_storage_api::noop::NoopProvider;
     use reth_transaction_pool::noop::NoopTransactionPool;
     use serde_json::json;
-    use tokio::net::TcpListener;
+    use tokio::{net::TcpListener, sync::Notify};
     use tokio_tungstenite::tungstenite::protocol::{frame::Utf8Bytes, Message};
 
     const TEST_HOST: &str = "127.0.0.1";
@@ -864,4 +874,50 @@ mod tests {
             "Should detect invalid URL format"
         );
     }
+
+    #[tokio::test(flavor = "current_thread")]
+    async fn report_latency_lock_order_regression() {
+        // Simulate a live connection so a pong handler (report_latency) can grab conn.read().
+        let (server_url, server_handle) = setup_mock_server().await;
+        let ethstats_url = format!("test-node:test-secret@{server_url}");
+
+        let network = NoopNetwork::default();
+        let provider = NoopProvider::default();
+        let pool = NoopTransactionPool::default();
+
+        let service = EthStatsService::new(&ethstats_url, network, provider, pool)
+            .await
+            .expect("Service should connect");
+
+        // Keep last_ping set to mimic an outstanding ping while a pong is being handled.
+        let mut last_ping_guard = service.last_ping.lock().await;
+        *last_ping_guard = Some(Instant::now());
+
+        let started = Arc::new(Notify::new());
+        let started_clone = started.clone();
+        let service_clone = service.clone();
+        let handle = tokio::spawn(async move {
+            started_clone.notify_one();
+            let _ = service_clone.report_latency().await;
+        });
+
+        // Let the pong handler start and (in the unfixed version) hold conn.read().
+        started.notified().await;
+        tokio::task::yield_now().await;
+
+        // This represents the timeout task trying to take conn.write() to close after a timeout.
+        // In the unfixed lock order, it would block because report_latency holds conn.read().
+        let write_guard =
+            tokio::time::timeout(std::time::Duration::from_millis(100), service.conn.write())
+                .await
+                .expect(
+                    "conn write lock should not be held while report_latency waits on last_ping",
+                );
+
+        drop(write_guard);
+        drop(last_ping_guard);
+
+        let _ = handle.await;
+        server_handle.abort();
+    }
 }
```
