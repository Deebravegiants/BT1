# [?] RPC Corrections and deadlock fix (#640)

## Summary
Severity: Unknown
Chain: Ethereum
Component: sigp/lighthouse
Published: 2019-11-29
Source: https://github.com/sigp/lighthouse/commit/12e32bd789e8f597c3e05db662b1110890e2527d
Type: security-commit

## Details
RPC Corrections and deadlock fix (#640)

* Correct goodbye handling and fix deadlock

* Correct typo

## Patch
### beacon_node/eth2-libp2p/src/lib.rs
```diff
@@ -22,7 +22,6 @@ pub use libp2p::enr::Enr;
 pub use libp2p::gossipsub::{Topic, TopicHash};
 pub use libp2p::multiaddr;
 pub use libp2p::Multiaddr;
-pub use libp2p::{core::ConnectedPoint, swarm::NetworkBehaviour};
 pub use libp2p::{
     gossipsub::{GossipsubConfig, GossipsubConfigBuilder},
     PeerId, Swarm,
```

### beacon_node/eth2-libp2p/src/rpc/codec/ssz.rs
```diff
@@ -45,7 +45,6 @@ impl Encoder for SSZInboundCodec {
                     RPCResponse::Status(res) => res.as_ssz_bytes(),
                     RPCResponse::BlocksByRange(res) => res, // already raw bytes
                     RPCResponse::BlocksByRoot(res) => res,  // already raw bytes
-                    RPCResponse::Goodbye => unreachable!("Never encode or decode this message"),
                 }
             }
             RPCErrorResponse::InvalidRequest(err) => err.as_ssz_bytes(),
```

### beacon_node/eth2-libp2p/src/rpc/handler.rs
```diff
@@ -1,4 +1,4 @@
-use super::methods::{RPCErrorResponse, RPCResponse, RequestId};
+use super::methods::{RPCErrorResponse, RequestId};
 use super::protocol::{RPCError, RPCProtocol, RPCRequest};
 use super::RPCEvent;
 use crate::rpc::protocol::{InboundFramed, OutboundFramed};
@@ -208,7 +208,6 @@ where
         // drop the stream and return a 0 id for goodbye "requests"
         if let r @ RPCRequest::Goodbye(_) = req {
             self.events_out.push(RPCEvent::Request(0, r));
-            warn!(self.log, "Goodbye Received");
             return;
         }
 
@@ -245,14 +244,6 @@ where
 
         // add the stream to substreams if we expect a response, otherwise drop the stream.
         match rpc_event {
-            RPCEvent::Request(id, RPCRequest::Goodbye(_)) => {
-                // notify the application layer, that a goodbye has been sent, so the application can
-                // drop and remove the peer
-                self.events_out.push(RPCEvent::Response(
-                    id,
-                    RPCErrorResponse::Success(RPCResponse::Goodbye),
-                ));
-            }
             RPCEvent::Request(id, request) if request.expect_response() => {
                 // new outbound request. Store the stream and tag the output.
                 let delay_key = self
```

### beacon_node/eth2-libp2p/src/rpc/methods.rs
```diff
@@ -139,9 +139,6 @@ pub enum RPCResponse {
 
     /// A response to a get BLOCKS_BY_ROOT request.
     BlocksByRoot(Vec<u8>),
-
-    /// A Goodbye message has been sent
-    Goodbye,
 }
 
 /// Indicates which response is being terminated by a stream termination response.
@@ -208,7 +205,6 @@ impl RPCErrorResponse {
                 RPCResponse::Status(_) => false,
                 RPCResponse::BlocksByRange(_) => true,
                 RPCResponse::BlocksByRoot(_) => true,
-                RPCResponse::Goodbye => false,
             },
             RPCErrorResponse::InvalidRequest(_) => true,
             RPCErrorResponse::ServerError(_) => true,
@@ -252,7 +248,6 @@ impl std::fmt::Display for RPCResponse {
             RPCResponse::Status(status) => write!(f, "{}", status),
             RPCResponse::BlocksByRange(_) => write!(f, "<BlocksByRange>"),
             RPCResponse::BlocksByRoot(_) => write!(f, "<BlocksByRoot>"),
-            RPCResponse::Goodbye => write!(f, "Goodbye Sent"),
         }
     }
 }
```

### beacon_node/eth2-libp2p/src/service.rs
```diff
@@ -9,19 +9,24 @@ use futures::prelude::*;
 use futures::Stream;
 use libp2p::core::{
     identity::Keypair, multiaddr::Multiaddr, muxing::StreamMuxerBox, nodes::Substream,
-    transport::boxed::Boxed,
+    transport::boxed::Boxed, ConnectedPoint,
 };
-use libp2p::{core, secio, PeerId, Swarm, Transport};
+use libp2p::{core, secio, swarm::NetworkBehaviour, PeerId, Swarm, Transport};
 use slog::{crit, debug, info, trace, warn};
+use smallvec::SmallVec;
 use std::fs::File;
 use std::io::prelude::*;
 use std::io::{Error, ErrorKind};
 use std::time::Duration;
+use std::time::Instant;
 
 type Libp2pStream = Boxed<(PeerId, StreamMuxerBox), Error>;
 type Libp2pBehaviour = Behaviour<Substream<StreamMuxerBox>>;
 
 const NETWORK_KEY_FILENAME: &str = "key";
+/// The time in milliseconds to wait before banning a peer. This allows for any Goodbye messages to be
+/// flushed and protocols to be negotiated.
+const BAN_PEER_TIMEOUT: u64 = 200;
 
 /// The configuration and state of the libp2p components for the beacon node.
 pub struct Service {
@@ -32,8 +37,11 @@ pub struct Service {
     /// This node's PeerId.
     pub local_peer_id: PeerId,
 
+    /// A current list of peers to ban after a given timeout.
+    peers_to_ban: SmallVec<[(PeerId, Instant); 4]>,
+
     /// Indicates if the listening address have been verified and compared to the expected ENR.
-    pub verified_listen_address: bool,
+    verified_listen_address: bool,
 
     /// The libp2p logger handle.
     pub log: slog::Logger,
@@ -156,10 +164,19 @@ impl Service {
         Ok(Service {
             local_peer_id,
             swarm,
+            peers_to_ban: SmallVec::new(),
             verified_listen_address: false,
             log,
         })
     }
+
+    /// Adds a peer to be banned after a timeout period.
+    pub fn disconnect_and_ban_peer(&mut self, peer_id: PeerId) {
+        self.peers_to_ban.push((
+            peer_id,
+            Instant::now() + Duration::from_millis(BAN_PEER_TIMEOUT),
+        ));
+    }
 }
 
 impl Stream for Service {
@@ -200,22 +217,43 @@ impl Stream for Service {
                     }
                 },
                 Ok(Async::Ready(None)) => unreachable!("Swarm stream shouldn't end"),
-                Ok(Async::NotReady) => {
-                    // check to see if the address is different to the config. If so, update our ENR
-                    if !self.verified_listen_address {
-                        let multiaddr = Swarm::listeners(&self.swarm).next();
-                        if let Some(multiaddr) = multiaddr {
-                            if let Some(socket_addr) = multiaddr_to_socket_addr(multiaddr) {
-                                self.swarm.update_local_enr_socket(socket_addr, true);
-                            }
-                        }
-                    }
-
-                    break;
-                }
+                Ok(Async::NotReady) => break,
                 _ => break,
             }
         }
+        // swarm is not ready
+        // check to see if the address is different to the config. If so, update our ENR
+        if !self.verified_listen_address {
+            let multiaddr = Swarm::listeners(&self.swarm).next();
+            if let Some(multiaddr) = multiaddr {
+                if let Some(socket_addr) = multiaddr_to_socket_addr(multiaddr) {
+                    self.swarm.update_local_enr_socket(socket_addr, true);
+                }
+            }
+        }
+
+        // check if there are peers to ban
+        while !self.peers_to_ban.is_empty() {
+            if self.peers_to_ban[0].1 < Instant::now() {
+                let (peer_id, _) = self.peers_to_ban.remove(0);
+                warn!(self.log, "Disconnecting and banning peer"; "peer_id" => format!("{:?}", peer_id));
+                Swarm::ban_peer_id(&mut self.swarm, peer_id.clone());
+                // TODO: Correctly notify protocols of the disconnect
+                // TODO: Also remove peer from the DHT: https://github.com/sigp/lighthouse/issues/629
+                let dummy_connected_point = ConnectedPoint::Dialer {
+                    address: "/ip4/0.0.0.0"
+                        .parse::<Multiaddr>()
+                        .expect("valid multiaddr"),
+                };
+                self.swarm
+                    .inject_disconnected(&peer_id, dummy_connected_point);
+                // inform the behaviour that the peer has been banned
+                self.swarm.peer_banned(peer_id);
+            } else {
+                break;
+            }
+        }
+
         Ok(Async::NotReady)
     }
 }
```

### beacon_node/network/src/message_handler.rs
```diff
@@ -194,9 +194,6 @@ impl<T: BeaconChainTypes> MessageHandler<T> {
                             }
                         }
                     }
-                    RPCResponse::Goodbye => {
-                        // A goodbye was successfully sent, ignore it
-                    }
                 }
             }
             RPCErrorResponse::StreamTermination(response_type) => {
```

### beacon_node/network/src/service.rs
```diff
@@ -4,15 +4,12 @@ use crate::NetworkConfig;
 use beacon_chain::{BeaconChain, BeaconChainTypes};
 use core::marker::PhantomData;
 use eth2_libp2p::Service as LibP2PService;
-use eth2_libp2p::{
-    rpc::{RPCErrorResponse, RPCRequest, RPCResponse},
-    ConnectedPoint, Enr, Libp2pEvent, Multiaddr, NetworkBehaviour, PeerId, Swarm, Topic,
-};
+use eth2_libp2p::{rpc::RPCRequest, Enr, Libp2pEvent, Multiaddr, PeerId, Swarm, Topic};
 use eth2_libp2p::{PubsubMessage, RPCEvent};
 use futures::prelude::*;
 use futures::Stream;
-use parking_lot::{Mutex, MutexGuard};
-use slog::{debug, info, trace, warn};
+use parking_lot::Mutex;
+use slog::{debug, info, trace};
 use std::sync::Arc;
 use tokio::runtime::TaskExecutor;
 use tokio::sync::{mpsc, oneshot};
@@ -158,9 +155,6 @@ fn network_service(
     propagation_percentage: Option<u8>,
 ) -> impl futures::Future<Item = (), Error = eth2_libp2p::error::Error> {
     futures::future::poll_fn(move || -> Result<_, eth2_libp2p::error::Error> {
-        // keep a list of peers to disconnect, once all channels are processed, remove the peers.
-        let mut peers_to_ban = Vec::new();
-
         // processes the network channel before processing the libp2p swarm
         loop {
             // poll the network channel
@@ -218,7 +212,7 @@ fn network_service(
                         }
                     }
                     NetworkMessage::Disconnect { peer_id } => {
-                        peers_to_ban.push(peer_id);
+                        libp2p_service.lock().disconnect_and_ban_peer(peer_id);
                     }
                 },
                 Ok(Async::NotReady) => break,
@@ -233,21 +227,15 @@ fn network_service(
 
         loop {
             // poll the swarm
-            match libp2p_service.lock().poll() {
+            let mut locked_service = libp2p_service.lock();
+            match locked_service.poll() {
                 Ok(Async::Ready(Some(event))) => match event {
                     Libp2pEvent::RPC(peer_id, rpc_event) => {
                         trace!(log, "Received RPC"; "RPC" => format!("{}", rpc_event));
 
-                        // if we received or sent a Goodbye message, drop and ban the peer
-                        match rpc_event {
-                            RPCEvent::Request(_, RPCRequest::Goodbye(_))
-                            | RPCEvent::Response(
-                                _,
-                                RPCErrorResponse::Success(RPCResponse::Goodbye),
-                            ) => {
-                                peers_to_ban.push(peer_id.clone());
-                            }
-                            _ => {}
+                        // if we received a Goodbye message, drop and ban the peer
+                        if let RPCEvent::Request(_, RPCRequest::Goodbye(_)) = rpc_event {
+                            locked_service.disconnect_and_ban_peer(peer_id.clone());
                         };
                         message_handler_send
                             .try_send(HandlerMessage::RPC(peer_id, rpc_event))
@@ -283,32 +271,10 @@ fn network_service(
             }
         }
 
-        while !peers_to_ban.is_empty() {
-            let service = libp2p_service.lock();
-            disconnect_peer(service, peers_to_ban.pop().expect("element exists"), &log);
-        }
-
         Ok(Async::NotReady)
     })
 }
 
-fn disconnect_peer(mut service: MutexGuard<LibP2PService>, peer_id: PeerId, log: &slog::Logger) {
-    warn!(log, "Disconnecting and banning peer"; "peer_id" => format!("{:?}", peer_id));
-    Swarm::ban_peer_id(&mut service.swarm, peer_id.clone());
-    // TODO: Correctly notify protocols of the disconnect
-    // TOOD: Also remove peer from the DHT: https://github.com/sigp/lighthouse/issues/629
-    let dummy_connected_point = ConnectedPoint::Dialer {
-        address: "/ip4/0.0.0.0"
-            .parse::<Multiaddr>()
-            .expect("valid multiaddr"),
-    };
-    service
-        .swarm
-        .inject_disconnected(&peer_id, dummy_connected_point);
-    // inform the behaviour that the peer has been banned
-    service.swarm.peer_banned(peer_id);
-}
-
 /// Types of messages that the network service can receive.
 #[derive(Debug)]
 pub enum NetworkMessage {
```

### beacon_node/src/cli.rs
```diff
@@ -282,7 +282,7 @@ pub fn cli_app<'a, 'b>() -> App<'a, 'b> {
                     .short("m")
                     .value_name("MINUTES")
                     .required(true)
-                    .default_value("0")
+                    .default_value("30")
                     .help("The maximum number of minutes that will have elapsed before genesis"))
             )
             /*
```

### validator_client/src/config.rs
```diff
@@ -36,8 +36,11 @@ pub struct Config {
 impl Default for Config {
     /// Build a new configuration from defaults.
     fn default() -> Self {
+        let mut data_dir = dirs::home_dir().unwrap_or_else(|| PathBuf::from("."));
+        data_dir.push(".lighthouse");
+        data_dir.push("validators");
         Self {
-            data_dir: PathBuf::from(".lighthouse/validators"),
+            data_dir,
             key_source: <_>::default(),
             http_server: DEFAULT_HTTP_SERVER.to_string(),
         }
```
