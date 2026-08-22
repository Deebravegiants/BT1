### Title
`RequestState` Handling Bypasses Source-Identity Check in Orb-Relay Client — ([File: orb-relay-client/src/client.rs])

### Summary
`PollerAgent::main_loop` in the `orb-relay-client` crate processes incoming `RelayPayload` messages received over the Orb↔App relay channel used during self-serve signup sessions. For every payload type except `self_serve::app::v1::RequestState`, the code validates that the message's `src.id` matches the expected counterpart (`self.config.dst_id`) before further processing. For `RequestState`, this validation is skipped entirely: the branch unconditionally re-sends `self.last_message` back through `sender_tx` regardless of who actually sent the request.

### Finding Description
In `main_loop`, the message dispatch logic is: [1](#0-0) 

```
message = response_stream.next() => {
    match message {
        Some(Ok(RelayConnectResponse {
            msg: Some(relay_connect_response::Msg::Payload(RelayPayload {
                src: Some(src), dst, seq, payload: Some(payload),
            })),
        })) => {
            if self_serve::app::v1::RequestState::matches(&payload).is_some() {
                sender_tx.send(self.last_message.clone()).await
                    .wrap_err("Failed to send outgoing message")?;
            } else if src.id != self.config.dst_id {
                tracing::error!("Skipping received message from unexpected source: {:?}: {payload:?}", src.id);
            } else {
                self.handle_message(RelayPayload { src: Some(src), dst, seq, payload: Some(payload) }, message_buffer).await?;
            }
        }
        ...
```

The `src.id != self.config.dst_id` check is a defense-in-depth measure intended to ensure that only the paired counterpart of a given signup session (identified by `dst_id`, e.g., the specific App session id paired to this Orb, or vice versa) can influence this connection's behavior — every other message kind is dropped and logged as "unexpected source" if it fails this check. The `RequestState` branch is evaluated first and unconditionally triggers a reply (`self.last_message.clone()`) without ever checking `src.id`. This mirrors the bug class described in the report: a handler meant to process an inbound message instead unconditionally emits an outgoing "reply" without validating that the reply is being generated for the correct party/context, undermining the very authorization check applied to structurally identical code paths a few lines below.

`self.last_message` holds the most recently sent `RelayConnectRequest`, which during a self-serve signup can be signup-sensitive state such as `AnnounceOrbId` (containing `orb_id`) or `SignupEnded` outcome data, as seen in the same file's usage patterns: [2](#0-1) 

and in `src/plans/mod.rs`'s `orb_relay_announce_orb_id`, which uses this exact client to announce `AnnounceOrbId`/session state for self-serve signups: [3](#0-2) 

Because the `RequestState` fast-path in `main_loop` runs before the `src.id` equality check, any entity able to deliver a `RequestState`-shaped payload into this stream — including one whose `src` field does not match the expected paired counterpart for this session — will have the orb's/app's last relayed signup-session message replayed back to it, i.e., a state disclosure/reply that bypasses the identity check enforced for all other message types.

### Impact Explanation
This creates a path for cross-signup/session state bleed: the last message exchanged in one paired orb↔app relay session (which can include signup identifiers/state such as `AnnounceOrbId` or `SignupEnded` results) can be replayed to a sender that the code's own authorization check (`src.id != self.config.dst_id`) was designed to reject for every other message. This is a direct structural instance of the reported bug class — an inbound-message handler emitting an unconditional "reply" without the surrounding authorization guard — applied to the self-serve signup IPC channel between the Orb and the paired App.

### Likelihood Explanation
The `RequestState` check is evaluated unconditionally on every payload received on the stream before the source check runs, so it is reachable on every connected relay session without any special privileges — the same conditions under which a normal (unprivileged) App participant in a signup session can send messages are sufficient to reach this code path with an arbitrary `src`.

### Recommendation
Move the `RequestState` handling to occur only after the same `src.id == self.config.dst_id` validation applied to all other payload types, so that only the properly paired counterpart of the session can request/receive the replayed last-message state. This mirrors the report's recommendation of not emitting a reply/response in situations where the request is not from a validated party.

### Proof of Concept
1. Establish an Orb-Relay session for a given signup (`orb_id`/`session_id` pair) and have the Orb send a signup-related message (e.g., `AnnounceOrbId`) via `orb_relay_announce_orb_id`, which becomes `self.last_message`.
2. Deliver a `RelayPayload` on the same underlying stream whose `payload` matches `self_serve::app::v1::RequestState` but whose `src.id` does not equal `self.config.dst_id` (i.e., not the actual paired party).
3. Observe that `main_loop` matches the `RequestState` branch first and calls `sender_tx.send(self.last_message.clone())`, replaying the session's last message without ever evaluating the `src.id != self.config.dst_id` guard that would otherwise reject the message.

### Citations

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

**File:** orb-relay-client/src/client.rs (L484-500)
```rust
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

**File:** src/plans/mod.rs (L2108-2146)
```rust
async fn orb_relay_announce_orb_id(
    orb: &mut Orb,
    orb_relay_app_id: String,
    is_self_serve_enabled: bool,
    reties: u32,
    timeout: Duration,
    wait_for_pending_messages: Duration,
    wait_for_shutdown: Duration,
) -> Result<()> {
    let mut relay = Client::new_as_orb(
        RELAY_BACKEND_URL.to_string(),
        get_orb_token()?,
        ORB_ID.to_string(),
        orb_relay_app_id,
    );
    if let Err(e) = relay.connect().await {
        dd_incr!("main.count.orb_relay.failure.connect");
        return Err(eyre::eyre!("Relay: Failed to connect: {e}"));
    }
    for _ in 0..reties {
        let now = Instant::now();
        if let Ok(()) = relay
            .send_blocking(
                common::v1::AnnounceOrbId {
                    orb_id: ORB_ID.to_string(),
                    mode_type: if is_self_serve_enabled {
                        common::v1::announce_orb_id::ModeType::SelfServe.into()
                    } else {
                        common::v1::announce_orb_id::ModeType::Legacy.into()
                    },
                    hardware_type: if identification::HARDWARE_VERSION.contains("Diamond") {
                        common::v1::announce_orb_id::HardwareType::Diamond.into()
                    } else {
                        common::v1::announce_orb_id::HardwareType::Pearl.into()
                    },
                },
                timeout,
            )
            .await
```
