## Finding: `RequestState` messages bypass source-authentication check in orb-relay-client

The reported withdrawal bug is a case where a message-like object (`Transfer`) is *blindly accepted and acted upon* without validating its `source`/`target`, letting an unauthenticated caller trigger a privileged action. The same root-cause pattern exists in the `orb-relay-client` code that orb-core uses to synchronize self-serve signup state between an Orb and a paired App.

### Root cause
In `PollerAgent::main_loop`, every incoming `RelayPayload` is supposed to be validated against the expected peer before being processed: [1](#0-0) 

Concretely, for any payload *other* than `self_serve::app::v1::RequestState`, the code checks `src.id != self.config.dst_id` and drops the message if it doesn't match the expected session peer: [2](#0-1) 

But when the payload matches `self_serve::app::v1::RequestState`, the source check is skipped entirely — the branch immediately replies by re-sending `self.last_message` to whoever sent it, with no verification that `src` corresponds to the bound `dst_id` for this session: [3](#0-2) 

This is structurally identical to the withdrawal-precompile bug: a specific message type is processed without checking the identity fields (`src`/`dst`) that gate every other message, so a payload that should be scoped to one authenticated session/dst-id instead gets accepted from any source and triggers a privileged side effect (replaying the last session state).

The code's own author flags the underlying architectural weakness that makes this reachable — multiplexed connections carrying messages "from different sources" on the same stream, which is exactly what the `src` check exists to filter: [4](#0-3) 

`self.last_message` is not a static value — it is updated every time the Orb sends a self-serve protocol message (`CaptureStarted`, `CaptureTriggerTimeout`, `SignupEnded`, etc.) during a live signup: [5](#0-4) 

These are exactly the messages produced during the self-serve signup flow in `orb-core`, e.g. `CaptureStarted`/`CaptureTriggerTimeout` when gating biometric capture on an app trigger, and `SignupEnded` at the end of a signup: [6](#0-5) [7](#0-6) 

### Impact
Because `RequestState` handling skips the `src.id != dst_id` check, any relay peer able to reach the same relay-multiplexed stream can send a `RequestState` payload and receive the Orb's `last_message` — i.e., the current signup-session state (capture trigger status, capture start/end, signup success/failure) — without being the legitimate App bound to that `dst_id`/session. This allows cross-signup state disclosure/bleed: an unauthorized party can learn or interfere with another user's in-progress self-serve signup state, which the strict `src` check elsewhere in the same function is explicitly designed to prevent.

### Likelihood
The vulnerable branch is on the hot path of every message received while connected (`main_loop`), requires no special privileges beyond being able to send a `RequestState` payload over the relay, and the surrounding code's own `TODO` acknowledges the multiplexing risk this check is meant to close — but the fix wasn't applied uniformly to the `RequestState` fast-path.

### Recommendation
Apply the same `src.id == self.config.dst_id` validation to the `RequestState` branch before replying with `last_message`, rather than special-casing it ahead of the source check.

### Proof of Concept
1. Establish a relay connection as an Orb bound to `dst_id = session_A`.
2. From a different, unauthenticated/unrelated session (`src.id != session_A`), send a payload matching `self_serve::app::v1::RequestState`.
3. Observe that the Orb, per [3](#0-2) , replies with `self.last_message` (the last self-serve state, e.g. `CaptureStarted`/`SignupEnded`) to the unauthenticated sender, even though the `else if src.id != self.config.dst_id` guard at [2](#0-1)  would have rejected any other payload type from that same unauthorized source.

### Citations

**File:** orb-relay-client/src/client.rs (L388-392)
```rust
impl<'a> PollerAgent<'a> {
    // TODO: We need to split auth and subscription. Maybe ideally we issue 1 connect and then a subscribe that will notify
    // the server that we care about messages from a certain queue only. That will avoid multiplexing messages from
    // different sources.
    async fn main_loop(
```

**File:** orb-relay-client/src/client.rs (L425-452)
```rust
                message = response_stream.next() => {
                    match message {
                        Some(Ok(RelayConnectResponse {
                            msg:
                                Some(relay_connect_response::Msg::Payload(RelayPayload {
                                    src: Some(src),
                                    dst,
                                    seq,
                                    payload: Some(payload),
                                })),
                        })) => {
                            if self_serve::app::v1::RequestState::matches(&payload).is_some() {
                                sender_tx
                                    .send(self.last_message.clone())
                                    .await
                                    .wrap_err("Failed to send outgoing message")?;
                            } else if src.id != self.config.dst_id {
                                tracing::error!(
                                    "Skipping received message from unexpected source: {:?}: {payload:?}",
                                    src.id
                                );
                            } else {
                                self.handle_message(
                                    RelayPayload { src: Some(src), dst, seq, payload: Some(payload) },
                                    message_buffer,
                                )
                                .await?;
                            }
```

**File:** orb-relay-client/src/client.rs (L478-500)
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
```

**File:** src/plans/mod.rs (L1485-1495)
```rust
        if orb.config.lock().await.self_serve {
            if let Some(relay) = orb.orb_relay.as_mut() {
                relay
                    .send(self_serve::orb::v1::SignupEnded {
                        success: signup_result.success,
                        failure_feedback,
                    })
                    .await
                    .inspect_err(|e| tracing::error!("Relay: Failed to SignupEnded: {e}"))?;
            }
        }
```

**File:** src/plans/mod.rs (L2096-2103)
```rust
    tracing::info!("Self-serve biometric-capture start triggered");
    orb.ui.signup_start();

    tracing::info!("Self-serve: Informing orb-relay that biometric_capture has started");
    orb_relay
        .send(self_serve::orb::v1::CaptureStarted {})
        .await
        .inspect_err(|e| tracing::error!("Relay: Failed to CaptureStarted: {e}"))?;
```
