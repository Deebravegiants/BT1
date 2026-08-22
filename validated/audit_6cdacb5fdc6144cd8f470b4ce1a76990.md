### Title
Orb-relay client replays last outgoing signup state to any sender claiming a `RequestState` payload, bypassing the `src.id`/`dst_id` binding check - ([File: orb-relay-client/src/client.rs])

### Summary
This is analogous to the Kamino `init_sy` bug: a piece of session/user-binding state (there, `obligation_farm`; here, the expected counterparty identity `dst_id`) is not consistently enforced before an action is taken on behalf of "the user," letting an entity other than the legitimate bound counterparty pull privileged state.

### Finding Description
`PollerAgent::main_loop` in `orb-relay-client/src/client.rs` processes every incoming `RelayPayload` from the relay stream. For all payload types except one, it verifies that the message's claimed `src.id` matches the `dst_id` the client was configured to talk to (`self.config.dst_id`) before accepting it: [1](#0-0) 

However, when the payload matches `self_serve::app::v1::RequestState`, that binding check is skipped entirely, and the client immediately replays `self.last_message` — the last state/payload it sent to its bound counterparty — to whoever sent the request, without checking that `src.id == self.config.dst_id`: [2](#0-1) 

`last_message` is updated on every outgoing send and holds the most recent signup-relevant payload sent to the app (e.g., `AnnounceOrbId`, `CaptureStarted`, `SignupEnded`, or other self-serve signup-state messages) as seen in the outgoing branch: [3](#0-2) 

This mirrors the reported bug class: a state-binding value (`obligation_farm` in Kamino; here, the verified counterparty `dst_id`/session binding) exists but is not enforced on this particular code path, so the "state" (last relayed signup message) can be handed to an unverified party instead of the one the session was established with — the `RequestState` handler in effect uses no "user_state" verification at all.

### Impact Explanation
If the relay server (or a malicious/compromised peer capable of injecting a payload with `src` unset/spoofed as matching the `RequestState` schema) can reach this client, the Orb (or App) client will disclose the last relayed signup-session payload to that requester regardless of identity verification. Depending on which message was last sent, this can leak state tied to a specific signup session (e.g., orb/session identifiers, capture/trigger state, `SignupEnded` status) to a party that was never bound to that session — a cross-signup/session state bleed condition, and a violation of the App/Orb entity-binding trust boundary that the `src.id != self.config.dst_id` check is designed to enforce everywhere else.

### Likelihood Explanation
The bypass is unconditional and reachable on every message received over the stream, with no auth/ownership check before replay — the only barrier is whatever authentication/session-routing the relay backend enforces between two ends of a channel. Because the check is intentionally special-cased and skips the general `src.id` validation used for every other message type, this is a straightforward logic bug rather than a hard-to-reach edge case: any correctly-formatted `RequestState` payload delivered to this client triggers the unauthenticated replay.

### Recommendation
Apply the same `src.id == self.config.dst_id` (or equivalent authenticated-binding) check to the `RequestState` branch before replaying `self.last_message`, so that only the verified, session-bound counterparty can request/receive the last relayed state — consistent with how every other payload type is already gated in this function.

### Proof of Concept
1. Establish a relay channel where the client is configured with `dst_id = "app-session-A"` (e.g., an Orb client from `Client::new_as_orb`), and have it send some signup-relevant payload (e.g., `AnnounceOrbId`) so `self.last_message` is populated.
2. From a different identity (`src.id` ≠ `"app-session-A"`) that is nonetheless able to deliver a `RelayPayload` whose `payload` matches `self_serve::app::v1::RequestState` to this client's stream (e.g., via a relay bug, misrouted message, or a peer sharing the transport), observe that `client.rs`'s `main_loop` immediately sends back `self.last_message` to that unverified sender — bypassing the `src.id != self.config.dst_id` check that governs every other message type at [1](#0-0) .

### Citations

**File:** orb-relay-client/src/client.rs (L436-452)
```rust
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
