I have enough evidence to complete the analysis now.

### Title
Missing source-authorization check on `RequestState` allows any relay peer to obtain the Orb/App session state - (File: orb-relay-client/src/client.rs)

### Summary
In the `PollerAgent::main_loop` message-handling loop, every incoming `RelayPayload` is checked against the expected session peer (`src.id != self.config.dst_id`) before being processed — except for `self_serve::app::v1::RequestState` messages, which are answered unconditionally with `self.last_message.clone()` regardless of who sent them. This mirrors the reported bug class ("anyone can change/access account state because an authorization check that gates the rest of the code path is missing for one specific code path"), just applied to the Orb-relay IPC boundary between the Orb and its paired self-serve App instead of a smart-contract setter.

### Finding Description
`PollerAgent::main_loop` receives messages from the relay stream and, for normal payloads, drops any message whose `src.id` does not match the configured peer (`self.config.dst_id`): [1](#0-0) 

However, the very first branch intercepts `RequestState` messages *before* that source check is applied, replying with `self.last_message.clone()` to whatever `src` sent the request: [2](#0-1) 

`last_message` is simply the last `RelayConnectRequest` this client sent (mirrored every time `send`/`send_blocking` is called), which for an Orb client can be `AnnounceOrbId`, `CaptureStarted`, `CaptureEnded`, `SignupEnded`, or similar self-serve signup-flow state messages: [3](#0-2) 

Because the `src.id != self.config.dst_id` filter — the only defense-in-depth check this client performs against the identity of the sender — is skipped for `RequestState`, any entity able to inject a `RequestState` payload into the stream this client is subscribed to (e.g. a message routed by the backend relay under a spoofed/incorrect `src`, or a bug/compromise on the relay server that misroutes a peer's traffic into another session) gets an authoritative echo of the Orb's current signup/session state without needing to be authenticated as the actual paired peer for that session.

### Impact Explanation
The disclosed `last_message` can reveal self-serve signup-session lifecycle information (`CaptureStarted`, `SignupEnded` success/failure, `AnnounceOrbId` with `orb_id`) to a party that is not the legitimately paired app, which is a session/state disclosure across the Orb⇄App relay trust boundary — the client-side identity check that exists specifically to prevent one session's messages from leaking into another is bypassed for this message type. This is analogous to the reported "any unprivileged caller can access state that should be gated to the account/session owner" bug class, applied to signup-session state leakage rather than an OCT-token setter.

### Likelihood Explanation
Exploitation depends on the relay backend or another party being able to deliver a `RequestState`-typed payload with an arbitrary/incorrect `src` into a given client's response stream (e.g. multiplexing, backend misrouting, or a compromised/malicious relay). It does not require any local/hardware access to the Orb and is reachable purely through the orb-relay IPC protocol, which is a legitimate remote trust boundary for self-serve signups. Note this is likelihood-bounded by the trustworthiness of the relay backend itself, since orb-core relies on it for message routing; the code path itself, however, contains no client-side check at all for this message type, unlike every other message type handled in the same loop.

### Recommendation
Apply the same `src.id == self.config.dst_id` check to `RequestState` messages before responding with `last_message`, so the source-authorization logic is consistent across all payload types handled in `PollerAgent::main_loop`.

### Proof of Concept
1. An entity controlling delivery of relay messages (e.g., a misbehaving/compromised relay backend, or any code path able to inject a payload into the `response_stream` this `PollerAgent` consumes) sends a `RelayConnectResponse` containing a `RelayPayload` with `payload = self_serve::app::v1::RequestState{}` and an arbitrary/mismatched `src`.
2. In `PollerAgent::main_loop`, the check `if self_serve::app::v1::RequestState::matches(&payload).is_some() { ... }` matches first and unconditionally executes `sender_tx.send(self.last_message.clone())`, bypassing the `src.id != self.config.dst_id` guard that every other message type must pass.
3. The requester receives `self.last_message` — the Orb's last sent state (e.g. `SignupEnded`, `CaptureStarted`, `AnnounceOrbId`) — without having been validated as the actual paired session peer.

### Citations

**File:** orb-relay-client/src/client.rs (L425-453)
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
