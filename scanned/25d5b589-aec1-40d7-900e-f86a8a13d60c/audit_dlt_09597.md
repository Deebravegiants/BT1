# [?] Fix join deadlock when dropping SocketWorker. (#1714)

## Summary
Severity: Unknown
Chain: Conflux
Component: Conflux-Chain/conflux-rust
Published: 2020-07-27
Source: https://github.com/Conflux-Chain/conflux-rust/commit/6b8e82b2304d2837f26a760e7b808e3f5ba74320
Type: security-commit

## Details
Fix join deadlock when dropping SocketWorker. (#1714)

* Fix join deadlock when dropping SocketWorker.

* fmt.

* Remove unnecessary outer loop in `work_loop`.

## Patch
### Cargo.lock
```diff
@@ -870,6 +870,16 @@ dependencies = [
  "itertools 0.8.2",
 ]
 
+[[package]]
+name = "crossbeam-channel"
+version = "0.4.3"
+source = "registry+https://github.com/rust-lang/crates.io-index"
+checksum = "09ee0cc8804d5393478d743b035099520087a5186f3b93fa58cec08fa62407b6"
+dependencies = [
+ "cfg-if",
+ "crossbeam-utils",
+]
+
 [[package]]
 name = "crossbeam-deque"
 version = "0.7.3"
@@ -1849,6 +1859,7 @@ checksum = "141340095b15ed7491bd3d4ced9d20cebfb826174b6bb03386381f62b01e3d77"
 name = "io"
 version = "0.1.0"
 dependencies = [
+ "crossbeam-channel",
  "crossbeam-deque",
  "fnv",
  "lazy_static",
```

### util/io/Cargo.toml
```diff
@@ -10,6 +10,7 @@ edition = "2018"
 fnv = "1.0"
 mio = { version = "0.6.19" }
 crossbeam-deque = "0.7"
+crossbeam-channel = "0.4"
 parking_lot = "0.10"
 log = "0.4"
 slab = "0.4"
```

### util/io/src/service_mio.rs
```diff
@@ -34,10 +34,7 @@ use parking_lot::{Mutex, RwLock};
 use slab::Slab;
 use std::{
     collections::HashMap,
-    sync::{
-        mpsc::{self, Sender as AsyncSender},
-        Arc, Condvar as SCondvar, Mutex as SMutex, Weak,
-    },
+    sync::{Arc, Condvar as SCondvar, Mutex as SMutex, Weak},
     thread::{self, JoinHandle},
     time::Duration,
 };
@@ -263,7 +260,8 @@ where Message: Send + Sync
     workers: Vec<Worker>,
     worker_channel: crossbeam_deque::Worker<Work<Message>>,
     work_ready: Arc<SCondvar>,
-    socket_workers: Vec<(AsyncSender<Work<Message>>, SocketWorker)>,
+    socket_workers:
+        Vec<(crossbeam_channel::Sender<Work<Message>>, SocketWorker)>,
     network_poll: Arc<Poll>,
 }
 
@@ -300,7 +298,7 @@ where Message: Send + Sync + 'static
         let num_socket_workers = 4;
         let socket_workers = (0..num_socket_workers)
             .map(|i| {
-                let (tx, rx) = mpsc::channel();
+                let (tx, rx) = crossbeam_channel::unbounded();
                 (
                     tx,
                     SocketWorker::new(
```

### util/io/src/worker.rs
```diff
@@ -22,17 +22,20 @@ use crate::{
     service_mio::{HandlerId, IoChannel, IoContext},
     IoHandler, LOCAL_STACK_SIZE,
 };
+use crossbeam_channel;
 use crossbeam_deque;
 use std::{
     sync::{
         atomic::{AtomicBool, Ordering as AtomicOrdering},
-        mpsc::Receiver,
         Arc,
     },
     thread::{self, JoinHandle},
 };
 
-use std::sync::{Condvar as SCondvar, Mutex as SMutex};
+use std::{
+    sync::{Condvar as SCondvar, Mutex as SMutex},
+    time::Duration,
+};
 
 const STACK_SIZE: usize = 16 * 1024 * 1024;
 
@@ -57,9 +60,12 @@ pub struct SocketWorker {
 impl SocketWorker {
     /// Creates a socket worker instance
     pub fn new<Message>(
-        index: usize, rx: Receiver<Work<Message>>, channel: IoChannel<Message>,
+        index: usize, rx: crossbeam_channel::Receiver<Work<Message>>,
+        channel: IoChannel<Message>,
     ) -> SocketWorker
-    where Message: Send + Sync + 'static {
+    where
+        Message: Send + Sync + 'static,
+    {
         let deleting = Arc::new(AtomicBool::new(false));
         let mut worker = SocketWorker {
             thread: None,
@@ -79,22 +85,18 @@ impl SocketWorker {
     }
 
     fn work_loop<Message>(
-        rx: Receiver<Work<Message>>, channel: IoChannel<Message>,
-        deleting: Arc<AtomicBool>,
+        rx: crossbeam_channel::Receiver<Work<Message>>,
+        channel: IoChannel<Message>, deleting: Arc<AtomicBool>,
     ) where
         Message: Send + Sync + 'static,
     {
-        loop {
-            if deleting.load(AtomicOrdering::Acquire) {
-                return;
-            }
-            while !deleting.load(AtomicOrdering::Acquire) {
-                // TODO recv_timeout() may panic, not sure if it's the cause for
-                // returning SendError on the sender
-                match rx.recv() {
-                    Ok(work) => SocketWorker::do_work(work, channel.clone()),
-                    _ => break,
-                }
+        while !deleting.load(AtomicOrdering::Acquire) {
+            // Add timeout because if the worker is dropped, we can check
+            // `deleting` without blocking forever.
+            match rx.recv_timeout(Duration::from_millis(500)) {
+                Ok(work) => SocketWorker::do_work(work, channel.clone()),
+                Err(crossbeam_channel::RecvTimeoutError::Timeout) => continue,
+                Err(crossbeam_channel::RecvTimeoutError::Disconnected) => break,
             }
         }
     }
```
