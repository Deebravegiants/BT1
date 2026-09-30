# [?] Fix a gRPC server deadlock bug caused by duplicate connections (#239)

## Summary
Severity: Unknown
Chain: Kaspa
Component: kaspanet/rusty-kaspa
Published: 2023-08-13
Source: https://github.com/kaspanet/rusty-kaspa/commit/d372345c70e056c436411d61606bf56ac0a2f81a
Type: security-commit

## Details
Fix a gRPC server deadlock bug caused by duplicate connections (#239)

* Fix a deadlock in case of duplicate connection with the same identity

* Use "GRPC" instead of "gRPC" in log messages

## Patch
### rpc/grpc/client/src/error.rs
```diff
@@ -9,10 +9,10 @@ pub enum Error {
     #[error("Error: {0}")]
     String(String),
 
-    #[error("gRPC invalid address schema {0}")]
+    #[error("GRPC invalid address schema {0}")]
     GrpcAddressSchema(String),
 
-    #[error("gRPC client error {0}")]
+    #[error("GRPC client error {0}")]
     TonicStatus(#[from] tonic::Status),
 
     /// RPC call timeout
```

### rpc/grpc/client/src/lib.rs
```diff
@@ -424,7 +424,7 @@ impl Inner {
         // Start the response receiving task
         inner.clone().spawn_response_receiver_task(stream);
 
-        trace!("gRPC client: connected");
+        trace!("GRPC client: connected");
         Ok(inner)
     }
 
@@ -466,16 +466,16 @@ impl Inner {
         let mut server_features = ServerFeatures::default();
         match stream.message().await? {
             Some(ref msg) => {
-                trace!("gRPC client: try_connect - GetInfo got a response");
+                trace!("GRPC client: try_connect - GetInfo got a response");
                 let response: RpcResult<GetInfoResponse> = msg.try_into();
                 if let Ok(response) = response {
                     server_features.handle_stop_notify = response.has_notify_command;
                     server_features.handle_message_id = response.has_message_id;
                 }
             }
             None => {
-                trace!("gRPC client: try_connect - stream closed by the server");
-                return Err(Error::String("gRPC stream was closed by the server".to_string()));
+                trace!("GRPC client: try_connect - stream closed by the server");
+                return Err(Error::String("GRPC stream was closed by the server".to_string()));
             }
         }
 
@@ -517,7 +517,7 @@ impl Inner {
             }
         }
 
-        trace!("gRPC client: reconnected");
+        trace!("GRPC client: reconnected");
         Ok(())
     }
 
@@ -568,7 +568,7 @@ impl Inner {
             let mut request: KaspadRequest = request.into();
             request.id = id;
 
-            trace!("gRPC client: resolver call: {:?}", request);
+            trace!("GRPC client: resolver call: {:?}", request);
             if request.payload.is_some() {
                 let receiver = self.resolver().register_request(op, &request);
                 self.request_sender.send(request).await.map_err(|_| Error::ChannelRecvError)?;
@@ -588,12 +588,12 @@ impl Inner {
 
         // The task can only be spawned once
         if self.timeout_is_running.compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst).is_err() {
-            trace!("gRPC client: timeout task - spawn request ignored since already spawned");
+            trace!("GRPC client: timeout task - spawn request ignored since already spawned");
             return;
         }
 
         tokio::spawn(async move {
-            trace!("gRPC client: timeout task - started");
+            trace!("GRPC client: timeout task - started");
             let shutdown = self.timeout_shutdown.request.listener.clone().fuse();
             pin_mut!(shutdown);
 
@@ -605,7 +605,7 @@ impl Inner {
                 select! {
                     _ = shutdown => { break; },
                     _ = delay => {
-                        trace!("gRPC client: timeout task - running");
+                        trace!("GRPC client: timeout task - running");
                         let timeout = Duration::from_millis(self.timeout_duration);
                         self.resolver().remove_expired_requests(timeout);
                     },
@@ -614,7 +614,7 @@ impl Inner {
             self.timeout_is_running.store(false, Ordering::SeqCst);
             self.timeout_shutdown.response.trigger.trigger();
 
-            trace!("gRPC client: timeout task - terminated");
+            trace!("GRPC client: timeout task - terminated");
         });
     }
 
@@ -624,15 +624,15 @@ impl Inner {
 
         // The task can only be spawned once
         if self.receiver_is_running.compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst).is_err() {
-            trace!("gRPC client: response receiver task - spawn ignored since already spawned");
+            trace!("GRPC client: response receiver task - spawn ignored since already spawned");
             return;
         }
 
         // Send connection event
         self.send_connection_event(ConnectionEvent::Connected);
 
         tokio::spawn(async move {
-            trace!("gRPC client: response receiver task - started");
+            trace!("GRPC client: response receiver task - started");
             loop {
                 let shutdown = self.receiver_shutdown.request.listener.clone();
                 pin_mut!(shutdown);
@@ -649,15 +649,15 @@ impl Inner {
                                         self.handle_response(response);
                                     },
                                     None =>{
-                                        trace!("gRPC client: response receiver task - the connection to the server is closed");
+                                        trace!("GRPC client: response receiver task - the connection to the server is closed");
 
                                         // A reconnection is needed
                                         break;
                                     }
                                 }
                             },
                             Err(err) => {
-                                trace!("gRPC client: response receiver task - the response receiver gets an error from the server: {:?}", err);
+                                trace!("GRPC client: response receiver task - the response receiver gets an error from the server: {:?}", err);
                             }
                         }
                     }
@@ -676,7 +676,7 @@ impl Inner {
                 self.receiver_shutdown.response.trigger.trigger();
             }
 
-            trace!("gRPC client: response receiver task - terminated");
+            trace!("GRPC client: response receiver task - terminated");
         });
     }
 
@@ -691,12 +691,12 @@ impl Inner {
 
         // The task can only be spawned once
         if self.connector_is_running.compare_exchange(false, true, Ordering::SeqCst, Ordering::SeqCst).is_err() {
-            trace!("gRPC client: connection monitor task - spawn ignored since already spawned");
+            trace!("GRPC client: connection monitor task - spawn ignored since already spawned");
             return;
         }
 
         tokio::spawn(async move {
-            trace!("gRPC client: connection monitor task - started");
+            trace!("GRPC client: connection monitor task - started");
             let shutdown = self.connector_shutdown.request.listener.clone().fuse();
             pin_mut!(shutdown);
             loop {
@@ -706,14 +706,14 @@ impl Inner {
                 select! {
                     _ = shutdown => { break; },
                     _ = delay => {
-                        trace!("gRPC client: connection monitor task - running");
+                        trace!("GRPC client: connection monitor task - running");
                         if !self.is_connected() {
                             match self.clone().reconnect(notifier.clone(), subscriptions.clone()).await {
                                 Ok(_) => {
-                                    trace!("gRPC client: reconnection to server succeeded");
+                                    trace!("GRPC client: reconnection to server succeeded");
                                 },
                                 Err(err) => {
-                                    trace!("gRPC client: reconnection to server failed with error {err:?}");
+                                    trace!("GRPC client: reconnection to server failed with error {err:?}");
                                 }
                             }
                         }
@@ -722,28 +722,28 @@ impl Inner {
             }
             self.connector_is_running.store(false, Ordering::SeqCst);
             self.connector_shutdown.response.trigger.trigger();
-            trace!("gRPC client: connection monitor task - terminating");
+            trace!("GRPC client: connection monitor task - terminating");
         });
     }
 
     fn handle_response(&self, response: KaspadResponse) {
         if response.is_notification() {
-            trace!("gRPC client: handle_response received a notification");
+            trace!("GRPC client: handle_response received a notification");
             match Notification::try_from(&response) {
                 Ok(notification) => {
                     let event: EventType = (&notification).into();
-                    trace!("gRPC client: handle_response received notification: {:?}", event);
+                    trace!("GRPC client: handle_response received notification: {:?}", event);
 
                     // Here we ignore any returned error
                     match self.notification_channel.try_send(notification) {
                         Ok(_) => {}
                         Err(err) => {
-                            trace!("gRPC client: error while trying to send a notification to the notifier: {:?}", err);
+                            trace!("GRPC client: error while trying to send a notification to the notifier: {:?}", err);
                         }
                     }
                 }
                 Err(err) => {
-                    trace!("gRPC client: handle_response error converting response into notification: {:?}", err);
+                    trace!("GRPC client: handle_response error converting response into notification: {:?}", err);
                 }
             }
         } else if response.payload.is_some() {
@@ -756,7 +756,7 @@ impl Inner {
         self.stop_timeout_monitor().await?;
         self.stop_response_receiver_task().await?;
         self.request_receiver.close();
-        trace!("gRPC client: disconnected");
+        trace!("GRPC client: disconnected");
         Ok(())
     }
 
@@ -804,17 +804,17 @@ impl Inner {
 #[async_trait]
 impl SubscriptionManager for Inner {
     async fn start_notify(&self, _: ListenerId, scope: Scope) -> NotifyResult<()> {
-        trace!("gRPC client: start_notify: {:?}", scope);
+        trace!("GRPC client: start_notify: {:?}", scope);
         self.start_notify_to_client(scope).await.map_err(|err| NotifyError::General(err.to_string()))?;
         Ok(())
     }
 
     async fn stop_notify(&self, _: ListenerId, scope: Scope) -> NotifyResult<()> {
         if self.handle_stop_notify() {
-            trace!("gRPC client: stop_notify: {:?}", scope);
+            trace!("GRPC client: stop_notify: {:?}", scope);
             self.stop_notify_to_client(scope).await.map_err(|err| NotifyError::General(err.to_string()))?;
         } else {
-            trace!("gRPC client: stop_notify ignored because not supported by the server: {:?}", scope);
+            trace!("GRPC client: stop_notify ignored because not supported by the server: {:?}", scope);
         }
         Ok(())
     }
```

### rpc/grpc/server/src/connection.rs
```diff
@@ -72,21 +72,21 @@ impl Connection {
         let connection_clone = connection.clone();
         let outgoing_route = connection.inner.outgoing_route.clone();
         // Start the connection receive loop
-        debug!("gRPC: Connection receive loop - starting for client {}", connection);
+        debug!("GRPC: Connection receive loop - starting for client {}", connection);
         tokio::spawn(async move {
             let listener_id: Lazy<ListenerId, _> = Lazy::new(|| notifier.clone().register_new_listener(connection.clone()));
             loop {
                 select! {
                     biased; // We use biased polling so that the shutdown signal is always checked first
 
                     _ = &mut shutdown_receiver => {
-                        debug!("gRPC: Connection receive loop - shutdown signal received, exiting connection receive loop, client-id: {}", connection.identity());
+                        debug!("GRPC: Connection receive loop - shutdown signal received, exiting connection receive loop, client-id: {}", connection.identity());
                         break;
                     }
 
                     res = incoming_stream.message() => match res {
                         Ok(Some(request)) => {
-                            //trace!("gRPC: request: {:?}, client-id: {}", request, connection.identity());
+                            //trace!("GRPC: request: {:?}, client-id: {}", request, connection.identity());
 
                             let response = match request.is_subscription() {
                                 true => {
@@ -101,38 +101,38 @@ impl Connection {
                                     match outgoing_route.send(Ok(response)).await {
                                         Ok(()) => {},
                                         Err(e) => {
-                                            debug!("gRPC: Connection receive loop - send error {} for client: {}", e, connection);
+                                            debug!("GRPC: Connection receive loop - send error {} for client: {}", e, connection);
                                             break;
                                         },
                                     }
                                 }
                                 Err(e) => {
-                                    debug!("gRPC: Connection receive loop - request handling error {} for client: {}", e, connection);
+                                    debug!("GRPC: Connection receive loop - request handling error {} for client: {}", e, connection);
                                     break;
                                 }
                             }
 
                         }
                         Ok(None) => {
-                            debug!("gRPC: Connection receive loop - incoming stream ended from client {}", connection);
+                            debug!("GRPC: Connection receive loop - incoming stream ended from client {}", connection);
                             break;
                         }
                         Err(err) => {
                             {
                                 if let Some(io_err) = match_for_io_error(&err) {
                                     if io_err.kind() == ErrorKind::BrokenPipe {
-                                        debug!("gRPC: Connection receive loop - client {} disconnected, broken pipe", connection);
+                                        debug!("GRPC: Connection receive loop - client {} disconnected, broken pipe", connection);
                                         break;
                                     }
                                 }
-                                debug!("gRPC: Connection receive loop - network error: {} from client {}", err, connection);
+                                debug!("GRPC: Connection receive loop - network error: {} from client {}", err, connection);
                             }
                             break;
                         }
                     }
                 }
             }
-            debug!("gRPC: Connection receive loop - terminated for client {}", connection);
+            debug!("GRPC: Connection receive loop - terminated for client {}", connection);
             if let Ok(listener_id) = Lazy::into_value(listener_id) {
                 let _ = notifier.unregister_listener(listener_id);
             }
@@ -142,6 +142,10 @@ impl Connection {
         connection_clone
     }
 
+    pub fn ptr_eq(this: &Self, other: &Self) -> bool {
+        Arc::ptr_eq(&this.inner, &other.inner)
+    }
+
     pub fn net_address(&self) -> SocketAddr {
         self.inner.net_address
     }
@@ -565,7 +569,7 @@ impl ConnectionT for Connection {
             // The typical case is the manager terminating all connections.
             return false;
         }
-        self.inner.manager.unregister(self.net_address());
+        self.inner.manager.unregister(self.clone());
         true
     }
 
```

### rpc/grpc/server/src/connection_handler.rs
```diff
@@ -78,7 +78,7 @@ impl ConnectionHandler {
 
             match serve_result {
                 Ok(_) => info!("GRPC Server stopped on: {}", serve_address),
-                Err(err) => panic!("gRPC Server {serve_address} stopped with error: {err:?}"),
+                Err(err) => panic!("GRPC Server {serve_address} stopped with error: {err:?}"),
             }
         });
         termination_sender
@@ -90,7 +90,7 @@ impl ConnectionHandler {
     }
 
     pub fn start(&self) {
-        debug!("gRPC: Starting the connection handler");
+        debug!("GRPC: Starting the connection handler");
 
         // Start the internal notifier
         self.notifier().start();
@@ -100,7 +100,7 @@ impl ConnectionHandler {
     }
 
     pub async fn stop(&self) -> RpcResult<()> {
-        debug!("gRPC: Stopping the connection handler");
+        debug!("GRPC: Stopping the connection handler");
 
         // Refuse new incoming connections
         self.running.store(false, Ordering::SeqCst);
@@ -143,7 +143,7 @@ impl Rpc for ConnectionHandler {
             ));
         }
 
-        debug!("gRPC: incoming message stream from {:?}", remote_address);
+        debug!("GRPC: incoming message stream from {:?}", remote_address);
 
         // Build the in/out pipes
         let (outgoing_route, outgoing_receiver) = mpsc_channel(Self::outgoing_route_channel_size());
```

### rpc/grpc/server/src/manager.rs
```diff
@@ -1,8 +1,12 @@
 use crate::connection::Connection;
-use kaspa_core::debug;
+use kaspa_core::{debug, info, warn};
 use kaspa_notify::connection::Connection as ConnectionT;
 use parking_lot::RwLock;
-use std::{collections::HashMap, net::SocketAddr, sync::Arc};
+use std::{
+    collections::{hash_map::Entry::Occupied, HashMap},
+    net::SocketAddr,
+    sync::Arc,
+};
 
 #[derive(Clone, Debug)]
 pub struct Manager {
@@ -16,17 +20,32 @@ impl Manager {
     }
 
     pub fn register(&self, connection: Connection) {
-        debug!("gRPC: Register a new connection from {connection}");
-        self.connections.write().insert(connection.identity(), connection).map(|x| x.close());
+        debug!("GRPC: registering a new connection from {connection}");
+        let mut connections_write = self.connections.write();
+        let previous_connection = connections_write.insert(connection.identity(), connection.clone());
+        info!("GRPC: new incoming connection {} #{}", connection, connections_write.len());
+
+        // Release the write lock to prevent a deadlock if a previous connection exists and must be closed
+        drop(connections_write);
+
+        if let Some(previous_connection) = previous_connection {
+            previous_connection.close();
+            warn!("GRPC: removing connection with duplicate identity: {}", previous_connection.identity());
+        }
     }
 
     pub fn is_full(&self) -> bool {
         self.connections.read().len() >= self.max_connections
     }
 
-    pub fn unregister(&self, net_address: SocketAddr) {
-        if let Some(connection) = self.connections.write().remove(&net_address) {
-            debug!("gRPC: Unregister the gRPC connection from {connection}");
+    pub fn unregister(&self, connection: Connection) {
+        if let Occupied(entry) = self.connections.write().entry(connection.identity()) {
+            // We search for the connection by identity, but make sure to delete it only if it's actually the same object.
+            // This is extremely important in cases of duplicate connection rejection etc.
+            if Connection::ptr_eq(entry.get(), &connection) {
+                entry.remove_entry();
+                debug!("GRPC: unregistering connection from {connection}");
+            }
         }
     }
 
```
