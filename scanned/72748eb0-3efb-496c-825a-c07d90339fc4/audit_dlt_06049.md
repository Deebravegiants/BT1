# [?] Fix non-deterministic tests (#944)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2026-04-06
Source: https://github.com/kaspanet/rusty-kaspa/commit/3be6630fea6eccc87c906b632f3cd1ec2152907a
Type: security-commit

## Details
Fix non-deterministic tests (#944)

* Increase SYNC_MAX_DELAY

* Increase mine_block timeout duration

* Increase test_writer_reentrance timeout

* Ignore underflows when dropping a UtxosChangedSubscription

* Fix integration tests to use 100 as FD limit

* Make TEST_FD_LIMIT maximum for tests, in case OS limit is lower

* Remove OS free port allocation and just use a random port instead

* clippy

* Increase timeout_duration for mine_block

## Patch
### notify/src/notifier.rs
```diff
@@ -544,7 +544,7 @@ pub mod test_helpers {
     use async_channel::Sender;
     use std::time::Duration;
 
-    pub const SYNC_MAX_DELAY: Duration = Duration::from_secs(2);
+    pub const SYNC_MAX_DELAY: Duration = Duration::from_secs(10);
 
     pub type TestConnection = ChannelConnection<TestNotification>;
     pub type TestNotifier = Notifier<TestNotification, ChannelConnection<TestNotification>>;
```

### notify/src/subscription/single.rs
```diff
@@ -383,11 +383,17 @@ impl Display for UtxosChangedSubscription {
 
 impl Drop for UtxosChangedSubscription {
     fn drop(&mut self) {
-        trace!(
-            "UtxosChangedSubscription: {} in total (drop {})",
-            UTXOS_CHANGED_SUBSCRIPTIONS.fetch_sub(1, Ordering::SeqCst) - 1,
-            self
-        );
+        // TODO: subscriptions were updated with `UTXOS_CHANGED_SUBSCRIPTIONS.fetch_sub(1, Ordering::SeqCst) - 1`
+        // before, but due to some race condition it overflowed in some cases. Since the counter is only used for
+        // logging purposes, we can afford to have an inaccurate count rather than risking an underflow panic.
+        // It's still worth investigating the root cause of the race condition and fixing it.
+        let subscriptions =
+            match UTXOS_CHANGED_SUBSCRIPTIONS.fetch_update(Ordering::SeqCst, Ordering::SeqCst, |count| count.checked_sub(1)) {
+                Ok(previous) => previous - 1,
+                Err(current) => current,
+            };
+
+        trace!("UtxosChangedSubscription: {} in total (drop {})", subscriptions, self);
     }
 }
 
```

### testing/integration/src/common/daemon.rs
```diff
@@ -6,7 +6,7 @@ use kaspa_grpc_server::service::GrpcService;
 use kaspa_notify::subscription::context::SubscriptionContext;
 use kaspa_rpc_core::notify::mode::NotificationMode;
 use kaspa_rpc_service::service::RpcCoreService;
-use kaspa_utils::triggers::Listener;
+use kaspa_utils::{networking::ContextualNetAddress, triggers::Listener};
 use kaspad_lib::{args::Args, daemon::create_core_with_runtime};
 use parking_lot::RwLock;
 use std::{ops::Deref, sync::Arc, time::Duration};
@@ -96,25 +96,26 @@ pub struct Daemon {
     _appdir_tempdir: TempDir,
 }
 
-impl Daemon {
-    pub fn fill_args_with_random_ports(args: &mut Args) {
-        // This should ask the OS to allocate free port for socket 1 to 4.
-        let socket1 = std::net::TcpListener::bind(format!("127.0.0.1:{}", args.rpclisten.map_or(0, |x| x.normalize(0).port))).unwrap();
-        let rpc_port = socket1.local_addr().unwrap().port();
-
-        let socket2 = std::net::TcpListener::bind(format!("127.0.0.1:{}", args.listen.map_or(0, |x| x.normalize(0).port))).unwrap();
-        let p2p_port = socket2.local_addr().unwrap().port();
-
-        let socket3 = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
-        let rpc_json_port = socket3.local_addr().unwrap().port();
+fn free_port() -> u16 {
+    loop {
+        let port = rand::random::<u16>() % (u16::MAX - 1024) + 1024;
+        if let Ok(listener) = std::net::TcpListener::bind(format!("127.0.0.1:{}", port)) {
+            drop(listener);
+            return port;
+        }
+    }
+}
 
-        let socket4 = std::net::TcpListener::bind("127.0.0.1:0").unwrap();
-        let rpc_borsh_port = socket4.local_addr().unwrap().port();
+fn port_from_address(addr: Option<ContextualNetAddress>) -> u16 {
+    addr.and_then(|x| if x.has_port() { Some(x.normalize(0).port) } else { None }).unwrap_or_else(free_port)
+}
 
-        drop(socket1);
-        drop(socket2);
-        drop(socket3);
-        drop(socket4);
+impl Daemon {
+    pub fn fill_args_with_random_ports(args: &mut Args) {
+        let rpc_port = port_from_address(args.rpclisten);
+        let p2p_port = port_from_address(args.listen);
+        let rpc_json_port = free_port();
+        let rpc_borsh_port = free_port();
 
         args.rpclisten = Some(format!("0.0.0.0:{rpc_port}").try_into().unwrap());
         args.listen = Some(format!("0.0.0.0:{p2p_port}").try_into().unwrap());
```

### testing/integration/src/common/utils.rs
```diff
@@ -192,24 +192,19 @@ pub async fn mine_block(pay_address: Address, submitting_client: &GrpcClient, li
     let block_hash = header.hash;
     submitting_client.submit_block(template.block, false).await.unwrap();
 
+    let timeout_duration = Duration::from_millis(10_000);
+
     // Wait for each listening client to get notified the submitted block was added to the DAG
     for client in listening_clients.iter() {
-        let block_daa_score: u64 = match timeout(Duration::from_millis(500), client.block_added_listener().unwrap().receiver.recv())
-            .await
-            .unwrap()
-            .unwrap()
-        {
-            Notification::BlockAdded(BlockAddedNotification { block }) => {
-                assert_eq!(block.header.hash, block_hash);
-                block.header.daa_score
-            }
-            _ => panic!("wrong notification type"),
-        };
-        match timeout(Duration::from_millis(500), client.virtual_daa_score_changed_listener().unwrap().receiver.recv())
-            .await
-            .unwrap()
-            .unwrap()
-        {
+        let block_daa_score: u64 =
+            match timeout(timeout_duration, client.block_added_listener().unwrap().receiver.recv()).await.unwrap().unwrap() {
+                Notification::BlockAdded(BlockAddedNotification { block }) => {
+                    assert_eq!(block.header.hash, block_hash);
+                    block.header.daa_score
+                }
+                _ => panic!("wrong notification type"),
+            };
+        match timeout(timeout_duration, client.virtual_daa_score_changed_listener().unwrap().receiver.recv()).await.unwrap().unwrap() {
             Notification::VirtualDaaScoreChanged(VirtualDaaScoreChangedNotification { virtual_daa_score }) => {
                 assert_eq!(virtual_daa_score, block_daa_score + 1);
             }
```

### testing/integration/src/rpc_tests.rs
```diff
@@ -53,7 +53,7 @@ async fn sanity_test() {
         ..Default::default()
     };
 
-    let fd_total_budget = fd_budget::limit();
+    let fd_total_budget = fd_budget::test_limit();
     let mut daemon = Daemon::new_random_with_args(args, fd_total_budget);
     let client = daemon.start().await;
     let (sender, _) = async_channel::unbounded();
```

### testing/integration/src/tasks/daemon.rs
```diff
@@ -148,7 +148,7 @@ impl DaemonTask {
 impl Task for DaemonTask {
     fn start(&self, stop_signal: SingleTrigger) -> Vec<JoinHandle<()>> {
         let ready_signal = self.ready_signal.trigger.clone();
-        let fd_total_budget = fd_budget::limit();
+        let fd_total_budget = fd_budget::test_limit();
         let mut daemon = Daemon::with_manager(self.client_manager.clone(), fd_total_budget);
         let task = tokio::spawn(async move {
             warn!("Daemon task starting...");
```

### utils/src/fd_budget.rs
```diff
@@ -61,10 +61,18 @@ pub fn try_set_fd_limit(limit: u64) -> std::io::Result<u64> {
     }
 }
 
+const TEST_FD_LIMIT: i32 = 100;
+
+// Many tests can be run in parallel, and each of them may acquire some FDs, so we set a lower limit for tests to avoid hitting the actual OS limit.
+// Note: Integration tests need to explicitly use this constant and not `limit()`, since they set `#[cfg(test)]` to false.
+pub fn test_limit() -> i32 {
+    limit().min(TEST_FD_LIMIT)
+}
+
 pub fn limit() -> i32 {
     cfg_if::cfg_if! {
         if #[cfg(test)] {
-            100
+            TEST_FD_LIMIT
         }
         else if #[cfg(target_os = "windows")] {
             rlimit::getmaxstdio() as i32
@@ -78,10 +86,6 @@ pub fn limit() -> i32 {
     }
 }
 
-pub fn remainder() -> i32 {
-    limit() - ACQUIRED_FD.load(Ordering::Relaxed)
-}
-
 #[cfg(test)]
 mod tests {
     use super::*;
```

### utils/src/sync/rwlock.rs
```diff
@@ -136,9 +136,9 @@ mod tests {
             rx.await.unwrap();
             // Make sure the reader acquires the lock during writer yields. We give the test a few chances to acquire
             // in order to make sure it passes also in slow CI environments where the OS thread-scheduler might take its time
-            let read = timeout(Duration::from_millis(18), l.read()).await.unwrap_or_else(|_| panic!("failed at iteration {i}"));
+            let read = timeout(Duration::from_millis(36), l.read()).await.unwrap_or_else(|_| panic!("failed at iteration {i}"));
             drop(read);
-            timeout(Duration::from_millis(500), tokio::task::spawn_blocking(move || h.join())).await.unwrap().unwrap().unwrap();
+            timeout(Duration::from_millis(1000), tokio::task::spawn_blocking(move || h.join())).await.unwrap().unwrap().unwrap();
         }
     }
 
```
