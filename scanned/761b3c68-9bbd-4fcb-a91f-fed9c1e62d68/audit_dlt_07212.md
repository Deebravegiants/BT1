# [?] Merge pull request from GHSA-x236-qc46-7v8j

## Summary
Severity: Unknown
Chain: Solana
Component: solana-labs/solana
Published: 2022-07-19
Source: https://github.com/solana-labs/solana/commit/f0994c4ba10e4e535ec13f58533451a53a6657ee
Type: security-commit

## Details
Merge pull request from GHSA-x236-qc46-7v8j

* Restrict the usable port range of the validator such that adding QUIC_PORT_OFFSET never gets us an invalid port. Also validate this for incoming ContactInfos

* Require the proper port range in ContactInfo::valid_client_facing_addr

* Use asserts instead of panics, and enforce USABLE_PORT_RANGE for all the ports in ContactInfo

* Fix typo

* Make the quic client return errors on the quinn endpoint connect() call,
not just the result of awaiting the connect() call, as the connect()
call can itself fail realistically (e.g. due to expected/invalid IPs, etc)

* Update USABLE_PORT_RANGE to a better range and use port_range_validator to validate dynamic-port-range rather than a panic

* Fall back on UDP when the remote peer's tpu port is too large to have QUIC_PORT_OFFSET added to it

* Get rid of tpu port sanitization in ContactInfo

* Turn USABLE_PORT_RANGE into a Range and make connnection_cache fall back on UDP when the tpu port is out of range

* Fix build

* Dummy commit

* Reert dummy commit

* dummy commit

* revert dummy commit

* Fix typo

* Fix range validation

* Fix formatting

* Fix USABLE_PORT_RANGE

* Remove USABLE_PORT_RANGE

* Avoid creating a QuicLazyInitializedEndpoint when forcing the use of UDP

* Implement test for connection cache overflow

## Patch
### client/src/client_error.rs
```diff
@@ -1,7 +1,7 @@
 pub use reqwest;
 use {
-    crate::{rpc_request, rpc_response},
-    quinn::{ConnectError, WriteError},
+    crate::{nonblocking::quic_client::QuicError, rpc_request, rpc_response},
+    quinn::ConnectError,
     solana_faucet::faucet::FaucetError,
     solana_sdk::{
         signature::SignerError, transaction::TransactionError, transport::TransportError,
@@ -73,9 +73,9 @@ impl From<ClientErrorKind> for TransportError {
     }
 }
 
-impl From<WriteError> for ClientErrorKind {
-    fn from(write_error: WriteError) -> Self {
-        Self::Custom(format!("{:?}", write_error))
+impl From<QuicError> for ClientErrorKind {
+    fn from(quic_error: QuicError) -> Self {
+        Self::Custom(format!("{:?}", quic_error))
     }
 }
 
```

### client/src/connection_cache.rs
```diff
@@ -225,8 +225,9 @@ pub struct ConnectionCache {
     stats: Arc<ConnectionCacheStats>,
     last_stats: AtomicInterval,
     connection_pool_size: usize,
-    tpu_udp_socket: Option<Arc<UdpSocket>>,
+    tpu_udp_socket: Arc<UdpSocket>,
     client_certificate: Arc<QuicClientCertificate>,
+    use_quic: bool,
 }
 
 /// Models the pool of connections
@@ -259,7 +260,7 @@ impl ConnectionCache {
         // The minimum pool size is 1.
         let connection_pool_size = 1.max(connection_pool_size);
         Self {
-            tpu_udp_socket: None,
+            use_quic: true,
             connection_pool_size,
             ..Self::default()
         }
@@ -282,17 +283,18 @@ impl ConnectionCache {
         // The minimum pool size is 1.
         let connection_pool_size = 1.max(connection_pool_size);
         Self {
+            use_quic: false,
             connection_pool_size,
             ..Self::default()
         }
     }
 
     pub fn use_quic(&self) -> bool {
-        matches!(self.tpu_udp_socket, None)
+        self.use_quic
     }
 
-    fn create_endpoint(&self) -> Option<Arc<QuicLazyInitializedEndpoint>> {
-        if self.use_quic() {
+    fn create_endpoint(&self, force_use_udp: bool) -> Option<Arc<QuicLazyInitializedEndpoint>> {
+        if self.use_quic() && !force_use_udp {
             Some(Arc::new(QuicLazyInitializedEndpoint::new(
                 self.client_certificate.clone(),
             )))
@@ -302,12 +304,13 @@ impl ConnectionCache {
     }
 
     /// Create a lazy connection object under the exclusive lock of the cache map if there is not
-    /// enough unsed connections in the connection pool for the specified address.
+    /// enough used connections in the connection pool for the specified address.
     /// Returns CreateConnectionResult.
     fn create_connection(
         &self,
         lock_timing_ms: &mut u64,
         addr: &SocketAddr,
+        force_use_udp: bool,
     ) -> CreateConnectionResult {
         let mut get_connection_map_lock_measure = Measure::start("get_connection_map_lock_measure");
         let mut map = self.map.write().unwrap();
@@ -318,20 +321,21 @@ impl ConnectionCache {
 
         let (to_create_connection, endpoint) =
             map.get(addr)
-                .map_or((true, self.create_endpoint()), |pool| {
+                .map_or((true, self.create_endpoint(force_use_udp)), |pool| {
                     (
                         pool.need_new_connection(self.connection_pool_size),
                         pool.endpoint.clone(),
                     )
                 });
 
         let (cache_hit, num_evictions, eviction_timing_ms) = if to_create_connection {
-            let connection = match &self.tpu_udp_socket {
-                Some(socket) => BaseTpuConnection::Udp(socket.clone()),
-                None => BaseTpuConnection::Quic(Arc::new(QuicClient::new(
+            let connection = if !self.use_quic() || force_use_udp {
+                BaseTpuConnection::Udp(self.tpu_udp_socket.clone())
+            } else {
+                BaseTpuConnection::Quic(Arc::new(QuicClient::new(
                     endpoint.as_ref().unwrap().clone(),
                     *addr,
-                ))),
+                )))
             };
 
             let connection = Arc::new(connection);
@@ -388,7 +392,12 @@ impl ConnectionCache {
 
         let port_offset = if self.use_quic() { QUIC_PORT_OFFSET } else { 0 };
 
-        let addr = SocketAddr::new(addr.ip(), addr.port() + port_offset);
+        let port = addr
+            .port()
+            .checked_add(port_offset)
+            .unwrap_or_else(|| addr.port());
+        let force_use_udp = port == addr.port();
+        let addr = SocketAddr::new(addr.ip(), port);
 
         let mut lock_timing_ms = get_connection_map_lock_measure.as_ms();
 
@@ -408,7 +417,7 @@ impl ConnectionCache {
                 if pool.need_new_connection(self.connection_pool_size) {
                     // create more connection and put it in the pool
                     drop(map);
-                    self.create_connection(&mut lock_timing_ms, &addr)
+                    self.create_connection(&mut lock_timing_ms, &addr, force_use_udp)
                 } else {
                     let connection = pool.borrow_connection();
                     CreateConnectionResult {
@@ -423,7 +432,7 @@ impl ConnectionCache {
             None => {
                 // Upgrade to write access by dropping read lock and acquire write lock
                 drop(map);
-                self.create_connection(&mut lock_timing_ms, &addr)
+                self.create_connection(&mut lock_timing_ms, &addr, force_use_udp)
             }
         };
         get_connection_map_measure.stop();
@@ -516,16 +525,15 @@ impl Default for ConnectionCache {
             stats: Arc::new(ConnectionCacheStats::default()),
             last_stats: AtomicInterval::default(),
             connection_pool_size: DEFAULT_TPU_CONNECTION_POOL_SIZE,
-            tpu_udp_socket: (!DEFAULT_TPU_USE_QUIC).then(|| {
-                Arc::new(
-                    solana_net_utils::bind_with_any_port(IpAddr::V4(Ipv4Addr::new(0, 0, 0, 0)))
-                        .expect("Unable to bind to UDP socket"),
-                )
-            }),
+            tpu_udp_socket: Arc::new(
+                solana_net_utils::bind_with_any_port(IpAddr::V4(Ipv4Addr::new(0, 0, 0, 0)))
+                    .expect("Unable to bind to UDP socket"),
+            ),
             client_certificate: Arc::new(QuicClientCertificate {
                 certificates: certs,
                 key: priv_key,
             }),
+            use_quic: DEFAULT_TPU_USE_QUIC,
         }
     }
 }
@@ -596,7 +604,8 @@ mod tests {
         },
         rand::{Rng, SeedableRng},
         rand_chacha::ChaChaRng,
-        std::net::SocketAddr,
+        solana_sdk::quic::QUIC_PORT_OFFSET,
+        std::net::{IpAddr, Ipv4Addr, SocketAddr},
     };
 
     fn get_addr(rng: &mut ChaChaRng) -> SocketAddr {
@@ -651,4 +660,22 @@ mod tests {
         assert!(map.len() == MAX_CONNECTIONS);
         let _conn = map.get(&addr).expect("Address not found");
     }
+
+    // Test that we can get_connection with a connection cache configured for quic
+    // on an address with a port that, if QUIC_PORT_OFFSET were added to it, it would overflow to
+    // an invalid port.
+    #[test]
+    fn test_overflow_address() {
+        let port = u16::MAX - QUIC_PORT_OFFSET + 1;
+        assert!(port.checked_add(QUIC_PORT_OFFSET).is_none());
+        let addr = SocketAddr::new(IpAddr::V4(Ipv4Addr::new(127, 0, 0, 1)), port);
+        let connection_cache = ConnectionCache::new(1);
+
+        let conn = connection_cache.get_connection(&addr);
+        // We (intentionally) don't have an interface that allows us to distinguish between
+        // UDP and Quic connections, so check instead that the port is valid (non-zero)
+        // and is the same as the input port (falling back on UDP)
+        assert!(conn.tpu_addr().port() != 0);
+        assert!(conn.tpu_addr().port() == port);
+    }
 }
```

### client/src/nonblocking/quic_client.rs
```diff
@@ -12,8 +12,8 @@ use {
     itertools::Itertools,
     log::*,
     quinn::{
-        ClientConfig, ConnectionError, Endpoint, EndpointConfig, IdleTimeout, NewConnection,
-        VarInt, WriteError,
+        ClientConfig, ConnectError, ConnectionError, Endpoint, EndpointConfig, IdleTimeout,
+        NewConnection, VarInt, WriteError,
     },
     solana_measure::measure::Measure,
     solana_net_utils::VALIDATOR_PORT_RANGE,
@@ -35,6 +35,7 @@ use {
         thread,
         time::Duration,
     },
+    thiserror::Error,
     tokio::{sync::RwLock, time::timeout},
 };
 
@@ -71,6 +72,16 @@ pub struct QuicLazyInitializedEndpoint {
     client_certificate: Arc<QuicClientCertificate>,
 }
 
+#[derive(Error, Debug)]
+pub enum QuicError {
+    #[error(transparent)]
+    WriteError(#[from] WriteError),
+    #[error(transparent)]
+    ConnectionError(#[from] ConnectionError),
+    #[error(transparent)]
+    ConnectError(#[from] ConnectError),
+}
+
 impl QuicLazyInitializedEndpoint {
     pub fn new(client_certificate: Arc<QuicClientCertificate>) -> Self {
         Self {
@@ -163,13 +174,11 @@ impl QuicNewConnection {
         endpoint: Arc<QuicLazyInitializedEndpoint>,
         addr: SocketAddr,
         stats: &ClientStats,
-    ) -> Result<Self, WriteError> {
+    ) -> Result<Self, QuicError> {
         let mut make_connection_measure = Measure::start("make_connection_measure");
         let endpoint = endpoint.get_endpoint().await;
 
-        let connecting = endpoint
-            .connect(addr, "connect")
-            .expect("QuicNewConnection::make_connection endpoint.connect");
+        let connecting = endpoint.connect(addr, "connect")?;
         stats.total_connections.fetch_add(1, Ordering::Relaxed);
         if let Ok(connecting_result) = timeout(
             Duration::from_millis(QUIC_CONNECTION_HANDSHAKE_TIMEOUT_MS),
@@ -208,11 +217,8 @@ impl QuicNewConnection {
         &mut self,
         addr: SocketAddr,
         stats: &ClientStats,
-    ) -> Result<Arc<NewConnection>, WriteError> {
-        let connecting = self
-            .endpoint
-            .connect(addr, "connect")
-            .expect("QuicNewConnection::make_connection_0rtt endpoint.connect");
+    ) -> Result<Arc<NewConnection>, QuicError> {
+        let connecting = self.endpoint.connect(addr, "connect")?;
         stats.total_connections.fetch_add(1, Ordering::Relaxed);
         let connection = match connecting.into_0rtt() {
             Ok((connection, zero_rtt)) => {
@@ -272,7 +278,7 @@ impl QuicClient {
     async fn _send_buffer_using_conn(
         data: &[u8],
         connection: &NewConnection,
-    ) -> Result<(), WriteError> {
+    ) -> Result<(), QuicError> {
         let mut send_stream = connection.connection.open_uni().await?;
 
         send_stream.write_all(data).await?;
@@ -287,7 +293,7 @@ impl QuicClient {
         data: &[u8],
         stats: &ClientStats,
         connection_stats: Arc<ConnectionCacheStats>,
-    ) -> Result<Arc<NewConnection>, WriteError> {
+    ) -> Result<Arc<NewConnection>, QuicError> {
         let mut connection_try_count = 0;
         let mut last_connection_id = 0;
         let mut last_error = None;
@@ -390,7 +396,7 @@ impl QuicClient {
                     return Ok(connection);
                 }
                 Err(err) => match err {
-                    WriteError::ConnectionLost(_) => {
+                    QuicError::ConnectionError(_) => {
                         last_error = Some(err);
                     }
                     _ => {
```

### validator/src/lib.rs
```diff
@@ -5,6 +5,7 @@ use {
     fd_lock::{RwLock, RwLockWriteGuard},
     indicatif::{ProgressDrawTarget, ProgressStyle},
     solana_net_utils::MINIMUM_VALIDATOR_PORT_RANGE_WIDTH,
+    solana_sdk::quic::QUIC_PORT_OFFSET,
     std::{
         borrow::Cow,
         env,
@@ -98,6 +99,8 @@ pub fn port_range_validator(port_range: String) -> Result<(), String> {
                 start,
                 start + MINIMUM_VALIDATOR_PORT_RANGE_WIDTH
             ))
+        } else if end.checked_add(QUIC_PORT_OFFSET).is_none() {
+            Err("Invalid dynamic_port_range.".to_string())
         } else {
             Ok(())
         }
```
