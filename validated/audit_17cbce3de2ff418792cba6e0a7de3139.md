No vulnerability found for this question.

`OutgoingMessage` in `orb-relay-client/src/client.rs` is simply an internal enum used to route text/protobuf payloads through the relay message channel — it has two variants, `Normal(Any)` for fire-and-forget messages and `Blocking(Any, oneshot::Sender<()>)` for messages awaiting an ack [1](#0-0) . It is consumed inside `PollerAgent::main_loop`, where it is simply serialized into a `RelayPayload` and sent over the gRPC stream to the relay server [2](#0-1) .

There is no camera, video, or biometric-capture logic anywhere in this file or type — no consent flag, no stream-start/stop condition, no reference to capture/fraud/signup state. The `Client`/`PollerAgent` here is a generic bidirectional relay-messaging transport (used e.g. for App↔Orb signaling), not a video/frame streaming pipeline [3](#0-2) . Session teardown is handled through `shutdown`/`graceful_shutdown` and `CancellationToken`, which only affect this relay connection, not any camera capture stream [4](#0-3) .

Since the target file/type does not implement or gate any camera/live-stream functionality, there is no exploitable path here matching the described vulnerability (no per-session consent gate to bypass, because none is expected to exist in this component, and no capture/fraud enforcement logic resides in this file).

### Citations

**File:** orb-relay-client/src/client.rs (L89-92)
```rust
enum OutgoingMessage {
    Normal(Any),
    Blocking(Any, oneshot::Sender<()>),
}
```

**File:** orb-relay-client/src/client.rs (L94-102)
```rust
/// Client state
pub struct Client {
    message_buffer: Arc<Mutex<VecDeque<RelayPayload>>>,
    outgoing_tx: Option<mpsc::Sender<OutgoingMessage>>,
    command_tx: Option<mpsc::Sender<Command>>,
    shutdown_token: Option<CancellationToken>,
    shutdown_completed: Option<oneshot::Receiver<()>>,
    config: Config,
}
```

**File:** orb-relay-client/src/client.rs (L335-373)
```rust
    pub async fn graceful_shutdown(
        &mut self,
        wait_for_pending_messages: Duration,
        wait_for_shutdown: Duration,
    ) {
        // Let's wait for all acks to be received
        if self.has_pending_messages().await.map_or(false, |n| n > 0) {
            tracing::info!(
                "Giving {}ms for pending messages to be acked",
                wait_for_pending_messages.as_millis()
            );
            tokio::time::sleep(wait_for_pending_messages).await;
        }
        // If there are still pending messages, we retry to send them
        if self.has_pending_messages().await.map_or(false, |n| n > 0) {
            tracing::info!("There are still pending messages, replaying...");
            if let Ok(()) = self.replay_pending_messages().await {
                tokio::time::sleep(wait_for_pending_messages).await;
            }
        }

        // Eventually, there not much more we can do, so we shutdown the client
        self.shutdown();

        if let Some(shutdown_completed) = self.shutdown_completed.take() {
            match tokio::time::timeout(wait_for_shutdown, shutdown_completed).await {
                Ok(_) => tracing::info!("Shutdown completed successfully."),
                Err(_) => tracing::warn!("Timed out waiting for shutdown to complete."),
            }
        }
    }

    /// Shutdown the client
    pub fn shutdown(&mut self) {
        if let Some(token) = self.shutdown_token.take() {
            token.cancel();
        }
    }
}
```

**File:** orb-relay-client/src/client.rs (L478-501)
```rust
                Some(outgoing_message) = outgoing_rx.recv() => {
                    self.seq = self.seq.wrapping_add(1);
                    let (payload, maybe_ack_tx) = match outgoing_message {
                        OutgoingMessage::Normal(payload) => (payload, None),
                        OutgoingMessage::Blocking(payload, ack_tx) => (payload, Some(ack_tx)),
                    };
                    let (src_t, dst_t) = match self.config.mode {
                        Mode::Orb => (EntityType::Orb as i32, EntityType::App as i32),
                        Mode::App => (EntityType::App as i32, EntityType::Orb as i32),
                    };
                    let relay_message = RelayPayload {
                        src: Some(Entity { id: self.config.src_id.clone(), entity_type: src_t }),
                        dst: Some(Entity { id: self.config.dst_id.clone(), entity_type: dst_t }),
                        seq: self.seq,
                        payload:  Some(payload),
                    };

                    tracing::debug!("Sending message: from: {:?}, to: {:?}, seq: {:?}, payload: {:?}",
                        relay_message.src, relay_message.dst, relay_message.seq, debug_any(&relay_message.payload));

                    self.pending_messages.insert(self.seq, (relay_message.clone().into(), maybe_ack_tx));
                    self.last_message = relay_message.clone().into();
                    sender_tx.send(relay_message.into()).await.wrap_err("Failed to send outgoing message")?;
                }
```
