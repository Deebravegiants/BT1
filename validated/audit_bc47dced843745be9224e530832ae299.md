### Title
`RequestState` message handling bypasses source-entity validation in the orb-relay client, allowing cross-session state disclosure - (File: `orb-relay-client/src/client.rs`)

### Summary
The orb-relay client's main receive loop special-cases `self_serve::app::v1::RequestState` messages by replying with the last message sent in the current session (`self.last_message`) *before* checking whether the message actually came from the paired session peer (`src.id == self.config.dst_id`). Every other message type is rejected unless it originates from the expected `dst_id`, but `RequestState` skips that check entirely, so any entity able to reach the relay stream for a given orb/app pairing can query and receive the last payload exchanged in that session.

### Finding Description
In `PollerAgent::main_loop`, incoming payloads are matched against `RequestState` first, and if matched, the response is sent unconditionally: [1](#0-0) 

```
if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: ...");
} else {
    self.handle_message(...).await?;
}
```

For all normal payloads the code enforces `src.id != self.config.dst_id` to drop messages from an unexpected sender [2](#0-1) , mirroring a state-machine "who is allowed to trigger this transition" check — analogous to the missing state guard in the `XChainController::sendFundsToVault` report, where a caller-identity/state check that should gate a transition is missing on one code path while present elsewhere. Here, the `RequestState` branch is the path where the guard is skipped: it returns `self.last_message`, which is populated whenever *any* outgoing message is sent by this client [3](#0-2) , i.e. it holds the most recent `self_serve` protocol message for that orb/session, such as `SignupEnded`, `CaptureTriggerTimeout`, `CaptureStarted`, or `AnnounceOrbId` [4](#0-3) .

Because the check that normally binds a session's messages to its expected peer (`dst_id`) is bypassed for `RequestState`, an unprivileged relay client — one that is not the paired app/orb for a given `session_id`/`orb_id` pair but is otherwise able to send a message that decodes as `RequestState` on that stream — can repeatedly query the orb (or app) for state belonging to a different session, in the same spirit as repeatedly invoking a state-transition entry point that omits the state/identity check present on the "normal" path.

### Impact Explanation
An attacker who can address a `RequestState` message to another party's relay stream (e.g. by guessing/observing a `session_id`/`orb_id`, which are used as the relay routing entity IDs rather than cryptographic secrets) can pull the last protocol message of a signup session cross-session, without being the legitimately paired app. Depending on the current signup, this can disclose whether a signup succeeded/failed, capture-trigger timing, or the orb ID being announced for the session — a cross-signup state bleed rather than a strict biometric-data leak, but it violates the intended session-pairing trust boundary between the orb and its paired self-serve app.

### Likelihood Explanation
Exploitation requires only sending a well-formed `RequestState` protobuf message over the relay to the targeted `src_id`/`dst_id` pair; no proof of pairing, secure-element attestation, or biometric material is needed, and the bypass is unconditional in code (not decision- or timing-dependent), making this straightforward to trigger for anyone who can reach the relay with a valid relay auth token and can address messages to another orb/app's routing IDs.

### Recommendation
Apply the same `src.id == self.config.dst_id` validation to `RequestState` messages before responding with `self.last_message`, so state queries are only answered for the legitimately paired peer of the current session, consistent with how all other message types are already gated.

### Proof of Concept
1. Orb connects as `Mode::Orb` with `src_id = orb_id`, `dst_id = session_id_A`, and sends/receives some self-serve protocol messages for session A (`self.last_message` gets set, e.g. to `SignupEnded`).
2. A second, unrelated relay client (not paired to session A) sends a `self_serve::app::v1::RequestState {}` payload addressed to the orb's stream, using an arbitrary/observed `src` entity.
3. Per `orb-relay-client/src/client.rs:436-440`, the orb-side `PollerAgent` responds with `self.last_message.clone()` regardless of `src.id`, leaking session A's last protocol message to the unrelated client — bypassing the `src.id != self.config.dst_id` check that guards every other message type. [5](#0-4)

### Citations

**File:** orb-relay-client/src/client.rs (L381-386)
```rust
struct PollerAgent<'a> {
    config: &'a Config,
    pending_messages: BTreeMap<u64, (RelayConnectRequest, Option<oneshot::Sender<()>>)>,
    last_message: RelayConnectRequest,
    seq: u64,
}
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

**File:** orb-relay-client/src/lib.rs (L19-54)
```rust
impl PayloadMatcher for self_serve::app::v1::StartCapture {
    type Output = self_serve::app::v1::StartCapture;

    fn matches(payload: &Any) -> Option<Self::Output> {
        if let Some(self_serve::app::v1::w::W::StartCapture(p)) =
            unpack_any::<self_serve::app::v1::W>(payload)?.w
        {
            return Some(p);
        }
        unpack_any::<Self>(payload)
    }
}

impl PayloadMatcher for self_serve::app::v1::RequestState {
    type Output = self_serve::app::v1::RequestState;

    fn matches(payload: &Any) -> Option<Self::Output> {
        if let Some(self_serve::app::v1::w::W::RequestState(p)) =
            unpack_any::<self_serve::app::v1::W>(payload)?.w
        {
            return Some(p);
        }
        unpack_any::<Self>(payload)
    }
}

impl PayloadMatcher for common::v1::AnnounceOrbId {
    type Output = common::v1::AnnounceOrbId;

    fn matches(payload: &Any) -> Option<Self::Output> {
        if let Some(common::v1::w::W::AnnounceOrbId(p)) = unpack_any::<common::v1::W>(payload)?.w {
            return Some(p);
        }
        unpack_any::<Self>(payload)
    }
}
```
