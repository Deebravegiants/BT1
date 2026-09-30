# [?] fix(p2p): prevent deadlock on simultaneous sending large message (#4948)

## Summary
Severity: Unknown
Chain: Hyperledger Iroha
Component: hyperledger-iroha/iroha
Published: 2024-08-07
Source: https://github.com/hyperledger-iroha/iroha/commit/00892429cb300f1323b574ad3eee79b0defa5084
Type: security-commit

## Details
fix(p2p): prevent deadlock on simultaneous sending large message (#4948)

Signed-off-by: Shanin Roman <shanin1000@yandex.ru>

## Patch
### p2p/src/network.rs
```diff
@@ -299,10 +299,11 @@ impl<T: Pload, K: Kex, E: Enc> NetworkBase<T, K, E> {
         let self_public_key_hash = blake2b_hash(self.key_pair.public_key().encode());
         let topology = topology
             .into_iter()
+            .filter(|peer_id| peer_id.public_key() != self.key_pair.public_key())
             .map(|peer_id| {
                 // Determine who is responsible for connecting
                 let peer_public_key_hash = blake2b_hash(peer_id.public_key().encode());
-                let is_active = self_public_key_hash > peer_public_key_hash;
+                let is_active = self_public_key_hash >= peer_public_key_hash;
                 (peer_id, is_active)
             })
             .collect();
```

### p2p/src/peer.rs
```diff
@@ -196,8 +196,8 @@ mod run {
                             ping_period=?ping_interval.period(),
                             "The connection has been idle, pinging to check if it's alive"
                         );
-                        if let Err(error) = message_sender.send_message(Message::<T>::Ping).await {
-                            iroha_logger::error!(%error, "Failed to send ping to peer.");
+                        if let Err(error) = message_sender.prepare_message(Message::<T>::Ping) {
+                            iroha_logger::error!(%error, "Failed to encrypt message.");
                             break;
                         }
                     }
@@ -218,8 +218,8 @@ mod run {
                         if post_receiver_len > 100 {
                             iroha_logger::warn!(size=post_receiver_len, "Peer post messages are pilling up");
                         }
-                        if let Err(error) = message_sender.send_message(Message::Data(msg)).await {
-                            iroha_logger::error!(%error, "Failed to send message to peer.");
+                        if let Err(error) = message_sender.prepare_message(Message::Data(msg)) {
+                            iroha_logger::error!(%error, "Failed to encrypt message.");
                             break;
                         }
                     }
@@ -240,8 +240,8 @@ mod run {
                         match msg {
                             Message::Ping => {
                                 iroha_logger::trace!("Received peer ping");
-                                if let Err(error) = message_sender.send_message(Message::<T>::Pong).await {
-                                    iroha_logger::error!(%error, "Failed to send message to peer.");
+                                if let Err(error) = message_sender.prepare_message(Message::<T>::Pong) {
+                                    iroha_logger::error!(%error, "Failed to encrypt message.");
                                     break;
                                 }
                             },
@@ -261,6 +261,12 @@ mod run {
                         idle_interval.reset();
                         ping_interval.reset();
                     }
+                    result = message_sender.send() => {
+                        if let Err(error) = result {
+                            iroha_logger::error!(%error, "Failed to send message to peer.");
+                            break;
+                        }
+                    }
                     else => break,
                 }
                 tokio::task::yield_now().await;
@@ -368,7 +374,10 @@ mod run {
     struct MessageSender<E: Enc> {
         write: OwnedWriteHalf,
         cryptographer: Cryptographer<E>,
-        buffer: BytesMut,
+        /// Reusable buffer to encode messages
+        buffer: Vec<u8>,
+        /// Queue of encrypted messages waiting to be sent
+        queue: BytesMut,
     }
 
     impl<E: Enc> MessageSender<E> {
@@ -379,38 +388,43 @@ mod run {
                 write,
                 cryptographer,
                 // TODO: eyeball decision of default buffer size of 1 KB, should be benchmarked and optimized
-                buffer: BytesMut::with_capacity(1024),
+                buffer: Vec::with_capacity(1024),
+                queue: BytesMut::with_capacity(1024),
             }
         }
 
-        /// Send byte-encoded message to the peer
+        /// Prepare message for the delivery and put it into the queue to be sent later
         ///
         /// # Errors
         /// - If encryption fail.
-        /// - If write to `stream` fail.
-        async fn send_message<T: Pload>(&mut self, msg: T) -> Result<(), Error> {
+        fn prepare_message<T: Pload>(&mut self, msg: T) -> Result<(), Error> {
             // Start with fresh buffer
             self.buffer.clear();
-            let mut writer = (&mut self.buffer).writer();
-            msg.encode_to(&mut writer);
-            let encoded_size = self.buffer.remaining();
-            let encrypted = self.cryptographer.encrypt(&self.buffer[..encoded_size])?;
-            self.buffer.advance(encoded_size);
-            assert!(
-                !self.buffer.has_remaining(),
-                "Buffer must be empty at this point"
-            );
-            let encrypted_size = encrypted.len();
+            msg.encode_to(&mut self.buffer);
+            let encrypted = self.cryptographer.encrypt(&self.buffer)?;
+
+            let size = encrypted.len();
+            self.queue.reserve(size + Self::U32_SIZE);
             #[allow(clippy::cast_possible_truncation)]
-            self.buffer.put_u32(encrypted_size as u32);
-            self.buffer.put_slice(encrypted.as_slice());
-            self.write.write_all(&self.buffer[..]).await?;
-            self.write.flush().await?;
-            self.buffer.advance(encrypted_size + Self::U32_SIZE);
-            assert!(
-                !self.buffer.has_remaining(),
-                "Buffer must be empty at this point"
-            );
+            self.queue.put_u32(size as u32);
+            self.queue.put_slice(encrypted.as_slice());
+            Ok(())
+        }
+
+        /// Send bytes of byte-encoded messages piled up in the message queue so far.
+        /// On the other side peer will collect bytes and recreate original messages from them.
+        ///
+        /// Sends only as much data as the underlying writer will accept in one `.write` call,
+        /// so must be called in a loop to ensure everything will get sent.
+        ///
+        /// # Errors
+        /// - If write to `stream` fail.
+        async fn send(&mut self) -> Result<(), Error> {
+            let chunk = self.queue.chunk();
+            if !chunk.is_empty() {
+                let n = self.write.write(chunk).await?;
+                self.queue.advance(n);
+            }
             Ok(())
         }
     }
```
