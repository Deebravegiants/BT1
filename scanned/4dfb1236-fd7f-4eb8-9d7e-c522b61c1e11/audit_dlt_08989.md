# [?] [fix] #3393: Break communication deadlock loop in actors

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2023-04-18
Source: https://github.com/hyperledger-iroha/iroha/commit/a7228c8c3d2212a8b0253ced0e6114e1635c2092
Type: security-commit

## Details
[fix] #3393: Break communication deadlock loop in actors

Signed-off-by: Shanin Roman <shanin1000@yandex.ru>

## Patch
### core/src/block_sync.rs
```diff
@@ -270,7 +270,7 @@ pub mod message {
                 data,
                 peer_id: peer.clone(),
             };
-            network.post(message).await;
+            network.post(message);
         }
     }
 }
```

### core/src/sumeragi/main_loop.rs
```diff
@@ -160,7 +160,7 @@ impl Sumeragi {
             data: NetworkMessage::SumeragiPacket(Box::new(packet.into())),
             peer_id: peer.clone(),
         };
-        self.network.post_blocking(post);
+        self.network.post(post);
     }
 
     #[allow(clippy::needless_pass_by_value, single_use_lifetimes)] // TODO: uncomment when anonymous lifetimes are stable
```

### p2p/src/lib.rs
```diff
@@ -94,3 +94,59 @@ impl From<io::Error> for Error {
 
 /// Result shorthand.
 pub type Result<T, E = Error> = core::result::Result<T, E>;
+
+/// Module for unbounded channel with attached length of the channel.
+pub(crate) mod unbounded_with_len {
+    use std::sync::{atomic::AtomicUsize, Arc};
+
+    use tokio::sync::mpsc;
+
+    /// Create unbounded channel with attached length.
+    pub fn unbounded_channel<T>() -> (Sender<T>, Receiver<T>) {
+        let (sender, receiver) = mpsc::unbounded_channel();
+        let len = Arc::new(AtomicUsize::new(1));
+        (
+            Sender {
+                sender,
+                len: Arc::clone(&len),
+            },
+            Receiver { receiver, len },
+        )
+    }
+
+    pub struct Receiver<T> {
+        receiver: mpsc::UnboundedReceiver<T>,
+        len: Arc<AtomicUsize>,
+    }
+
+    #[derive(Clone)]
+    pub struct Sender<T> {
+        sender: mpsc::UnboundedSender<T>,
+        len: Arc<AtomicUsize>,
+    }
+
+    impl<T> Receiver<T> {
+        pub async fn recv(&mut self) -> Option<T>
+        where
+            T: Send,
+        {
+            let message = self.receiver.recv().await?;
+            self.len.fetch_sub(1, std::sync::atomic::Ordering::SeqCst);
+            Some(message)
+        }
+
+        pub fn len(&self) -> usize {
+            self.len
+                .load(std::sync::atomic::Ordering::SeqCst)
+                .saturating_sub(1)
+        }
+    }
+
+    impl<T> Sender<T> {
+        pub fn send(&self, message: T) -> Result<(), mpsc::error::SendError<T>> {
+            self.sender.send(message)?;
+            self.len.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
+            Ok(())
+        }
+    }
+}
```

### p2p/src/network.rs
```diff
@@ -23,7 +23,7 @@ use crate::{
         message::*,
         Connection, ConnectionId,
     },
-    Error,
+    unbounded_with_len, Error,
 };
 
 /// [`NetworkBase`] actor handle.
@@ -39,7 +39,9 @@ pub struct NetworkBaseHandle<T: Pload, K: Kex, E: Enc> {
     /// [`DisconnectPeer`] message receiver
     disconnect_peer_sender: mpsc::Sender<DisconnectPeer>,
     /// Sender of [`Post`] message
-    post_sender: mpsc::Sender<Post<T>>,
+    // NOTE: it's ok for this channel to be unbounded.
+    // Because post messages originates inside system and there rate is configurable.
+    post_sender: unbounded_with_len::Sender<Post<T>>,
     /// Key exchange used by network
     _key_exchange: core::marker::PhantomData<K>,
     /// Encryptor used by the network
@@ -76,7 +78,7 @@ impl<T: Pload, K: Kex + Sync, E: Enc + Sync> NetworkBaseHandle<T, K, E> {
             mpsc::channel(1);
         let (connect_peer_sender, connect_peer_receiver) = mpsc::channel(1);
         let (disconnect_peer_sender, disconnect_peer_receiver) = mpsc::channel(1);
-        let (post_sender, post_receiver) = mpsc::channel(1);
+        let (post_sender, post_receiver) = unbounded_with_len::unbounded_channel();
         let (peer_message_sender, peer_message_receiver) = mpsc::channel(1);
         let network = NetworkBase {
             listen_addr,
@@ -123,6 +125,14 @@ impl<T: Pload, K: Kex + Sync, E: Enc + Sync> NetworkBaseHandle<T, K, E> {
         self.online_peers_receiver.borrow_and_update().clone()
     }
 
+    /// Send [`Post<T>`] message on network actor.
+    pub fn post(&self, msg: Post<T>) {
+        self.post_sender
+            .send(msg)
+            .map_err(|_| ())
+            .expect("NetworkBase must accept messages until there is at least one handle to it")
+    }
+
     /// Wait for update of [`OnlinePeers`].
     pub async fn wait_online_peers_update(&mut self) -> OnlinePeers {
         self.online_peers_receiver
@@ -159,7 +169,6 @@ macro_rules! impl_handle_methods {
 }
 
 impl_handle_methods! {
-    post (post_blocking): Post<T> => post_sender,
     connect_peer (connect_peer_blocking): ConnectPeer => connect_peer_sender,
     disconnect_peer (disconnect_peer_blocking): DisconnectPeer => disconnect_peer_sender,
 }
@@ -189,7 +198,7 @@ struct NetworkBase<T: Pload, K: Kex, E: Enc> {
     /// [`DisconnectPeer`] message receiver
     disconnect_peer_receiver: mpsc::Receiver<DisconnectPeer>,
     /// Receiver of [`Post`] message
-    post_receiver: mpsc::Receiver<Post<T>>,
+    post_receiver: unbounded_with_len::Receiver<Post<T>>,
     /// Channel to gather messages from all peers
     peer_message_receiver: mpsc::Receiver<PeerMessage<T>>,
     /// Sender for peer messages to provide clone of sender inside peer
@@ -248,7 +257,11 @@ impl<T: Pload, K: Kex, E: Enc> NetworkBase<T, K, E> {
                         iroha_logger::info!("All handles to network actor are dropped. Shutting down...");
                         break;
                     };
-                    self.post(post).await
+                    let post_receiver_len = self.post_receiver.len();
+                    if post_receiver_len > 100 {
+                        iroha_logger::warn!(size=post_receiver_len, "Network post messages are pilling up in the queue");
+                    }
+                    self.post(post)
                 }
                 else => break,
             }
@@ -343,12 +356,12 @@ impl<T: Pload, K: Kex, E: Enc> NetworkBase<T, K, E> {
         }
     }
 
-    async fn post(&mut self, Post { data, peer_id }: Post<T>) {
+    fn post(&mut self, Post { data, peer_id }: Post<T>) {
         iroha_logger::trace!(peer=%peer_id, "Post message");
         match self.peers.get(&peer_id.public_key) {
             Some(peer) => {
-                if peer.handle.post(data).await.is_err() {
-                    iroha_logger::error!(peer=%peer_id, "Peer not found. Message not sent.");
+                if peer.handle.post(data).is_err() {
+                    iroha_logger::error!(peer=%peer_id, "Failed to send message to peer");
                     self.peers.remove(&peer_id.public_key);
                     self.remove_online_peer(&peer_id);
                 }
@@ -357,7 +370,7 @@ impl<T: Pload, K: Kex, E: Enc> NetworkBase<T, K, E> {
                 #[cfg(debug_assertions)]
                 iroha_logger::trace!("Not sending message to myself")
             }
-            _ => iroha_logger::warn!(peer=%peer_id, "Didn't find peer to send message"),
+            _ => iroha_logger::warn!(peer=%peer_id, "Peer not found. Message not sent."),
         }
     }
 
```

### p2p/src/peer.rs
```diff
@@ -27,6 +27,7 @@ pub mod handles {
     //! Module with functions to start peer actor and handle to interact with it.
 
     use super::{run::RunPeerArgs, *};
+    use crate::unbounded_with_len;
 
     /// Start Peer in [`state::Connecting`] state
     pub fn connecting<T: Pload, K: Kex, E: Enc>(
@@ -68,16 +69,18 @@ pub mod handles {
 
     /// Peer actor handle.
     pub struct PeerHandle<T: Pload> {
-        pub(super) post_sender: mpsc::Sender<T>,
+        // NOTE: it's ok for this channel to be unbounded.
+        // Because post messages originate inside the system and their rate is configurable..
+        pub(super) post_sender: unbounded_with_len::Sender<T>,
     }
 
     impl<T: Pload> PeerHandle<T> {
         /// Post message `T` on Peer
         ///
         /// # Errors
         /// Fail if peer terminated
-        pub async fn post(&self, msg: T) -> Result<(), mpsc::error::SendError<T>> {
-            self.post_sender.send(msg).await
+        pub fn post(&self, msg: T) -> Result<(), mpsc::error::SendError<T>> {
+            self.post_sender.send(msg)
         }
     }
 }
@@ -91,6 +94,7 @@ mod run {
         state::{ConnectedFrom, Connecting, Ready},
         *,
     };
+    use crate::unbounded_with_len;
 
     /// Peer task.
     pub(super) async fn run<T: Pload, K: Kex, E: Enc, P: Entrypoint<K, E>>(
@@ -126,7 +130,7 @@ mod run {
             } = peer;
             peer_id = new_peer_id;
 
-            let (post_sender, mut post_receiver) = mpsc::channel(1);
+            let (post_sender, mut post_receiver) = unbounded_with_len::unbounded_channel();
             let (peer_message_sender, peer_message_receiver) = oneshot::channel();
             let ready_peer_handle = handles::PeerHandle { post_sender };
             if connected_sender
@@ -163,6 +167,10 @@ mod run {
                             iroha_logger::debug!("Peer handle dropped.");
                             break;
                         };
+                        let post_receiver_len = post_receiver.len();
+                        if post_receiver_len > 100 {
+                            iroha_logger::warn!(size=post_receiver_len, peer=%peer_id, "Peer post messages are pilling up");
+                        }
                         if let Err(error) = message_sender.send_message(msg).await {
                             iroha_logger::error!(%error, peer=%peer_id, "Failed to send message to peer.");
                             break;
```

### p2p/tests/integration/p2p.rs
```diff
@@ -72,12 +72,10 @@ async fn network_create() {
     tokio::time::sleep(delay).await;
 
     info!("Posting message...");
-    network
-        .post(Post {
-            data: TestMessage("Some data to send to peer".to_owned()),
-            peer_id: peer1,
-        })
-        .await;
+    network.post(Post {
+        data: TestMessage("Some data to send to peer".to_owned()),
+        peer_id: peer1,
+    });
 
     tokio::time::sleep(delay).await;
 }
@@ -155,12 +153,10 @@ async fn two_networks() {
     tokio::time::sleep(delay).await;
 
     info!("Posting message...");
-    network1
-        .post(Post {
-            data: TestMessage("Some data to send to peer".to_owned()),
-            peer_id: peer2.clone(),
-        })
-        .await;
+    network1.post(Post {
+        data: TestMessage("Some data to send to peer".to_owned()),
+        peer_id: peer2.clone(),
+    });
 
     tokio::time::sleep(delay).await;
     assert_eq!(messages2.load(Ordering::SeqCst), 1);
@@ -235,7 +231,7 @@ async fn multiple_networks() {
                 data: TestMessage(String::from("Some data to send to peer")),
                 peer_id: id.clone(),
             };
-            network.post(post).await;
+            network.post(post);
         }
     }
     info!("Posts sent");
```
