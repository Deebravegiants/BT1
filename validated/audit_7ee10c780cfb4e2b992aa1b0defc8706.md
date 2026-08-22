### Title
Missing sender/initiator verification for `RequestState` replay allows unauthorized disclosure of last signup message - (File: `orb-relay-client/src/client.rs`)

### Summary
In `PollerAgent::main_loop`, every incoming relay payload is supposed to be checked against the expected session peer (`src.id == self.config.dst_id`) before being processed, mirroring the intended trust boundary between an Orb and its paired App in a self-serve signup session. However, the `RequestState` message type is special-cased and handled *before* this source check, so any entity able to deliver a payload to this client's stream can trigger a reply containing `self.last_message` without ever being validated as the authorized session peer.

### Finding Description
The message dispatch loop is:
```rust
if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: ...");
} else {
    self.handle_message(...).await?;
}
``` [1](#0-0) 

Every other message type is gated by `src.id != self.config.dst_id`, which enforces that only the intended paired counterpart (the App for an Orb-mode client, or the Orb for an App-mode client, bound to a specific `session_id`/`orb_id` pair) can drive the client's state machine. `RequestState` bypasses this check entirely: as soon as the payload matches `RequestState`, the client unconditionally replays `self.last_message` — the most recently sent `RelayConnectRequest` (e.g. `AnnounceOrbId`, `SignupEnded`, `CaptureStarted`, etc., set in `send_internal`/`main_loop`) — to whatever sender delivered the payload. [2](#0-1) 

This is the same bug class as the Sherlock finding: the code assumes the "initiator" of a privileged callback path is always the trusted counterpart of the flow (there, `MarginTrading` itself; here, the paired session peer identified by `dst_id`), but the actual protocol allows any party able to reach the callback (there, any flash-loan `receiverAddress`; here, any relay message tagged as `RequestState`) to invoke it without an initiator check.

### Impact Explanation
`last_message` can carry signup-session state such as `AnnounceOrbId`, `SignupEnded`, or other self-serve status payloads sent over the relay channel [3](#0-2) . Because the `RequestState` handler skips the `src.id == dst_id` authorization check that every other inbound message is subject to, an entity that is not the verified counterpart for this specific signup session can obtain a replay of that state. This is a signup-session/identity-binding trust-boundary violation: it weakens the assumption (relied upon by callers such as `proceed_with_biometric_capture`, which waits on relay messages during self-serve capture [4](#0-3) ) that only the authenticated, bound session peer can interact with a given signup's relay state.

### Likelihood Explanation
Exploitability depends on whether the relay backend service (not present in this repo) enforces routing/authorization purely based on entity IDs known to the requester, or performs additional binding beyond what this client-side code assumes. Within `orb-core`'s own client code, the check is unconditionally skipped for `RequestState`, so the client itself provides no defense-in-depth against a misrouted or spoofed `RequestState` payload — it fully trusts that "if the payload matches `RequestState`, respond," with no initiator verification, unlike all other message types in the same loop. This is a real code-level gap; whether it is remotely reachable by a fully unprivileged party depends on server-side routing guarantees outside this repository's index, which could not be fully verified.

### Recommendation
Move the `src.id != self.config.dst_id` check ahead of the `RequestState` special case so all inbound payloads — including `RequestState` — are validated against the expected session peer before any reply or state disclosure occurs:
```rust
if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: {:?}", src.id);
} else if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else {
    self.handle_message(...).await?;
}
```

### Proof of Concept
1. An unprivileged relay-connected client obtains or is delivered a `RelayPayload` whose `payload` matches `self_serve::app::v1::RequestState`, with any `src` value.
2. In `main_loop`'s `tokio::select!` branch handling `response_stream.next()`, the code checks `RequestState::matches(&payload).is_some()` first and, since it's true, immediately sends `self.last_message.clone()` over `sender_tx` — regardless of whether `src.id == self.config.dst_id` [5](#0-4) .
3. The `src.id != self.config.dst_id` authorization check, applied to every other message type, is never evaluated for this payload, so the state disclosure happens without verifying the requester is the bound session peer.

### Citations

**File:** orb-relay-client/src/client.rs (L104-117)
```rust
impl Client {
    fn no_state(&self) -> RelayConnectRequest {
        let (src_t, dst_t) = match self.config.mode {
            Mode::Orb => (EntityType::Orb as i32, EntityType::App as i32),
            Mode::App => (EntityType::App as i32, EntityType::Orb as i32),
        };
        RelayPayload {
            src: Some(Entity { id: self.config.src_id.clone(), entity_type: src_t }),
            dst: Some(Entity { id: self.config.dst_id.clone(), entity_type: dst_t }),
            payload: Some(common::v1::NoState::default().into_payload()),
            seq: 0,
        }
        .into()
    }
```

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

**File:** orb-relay-client/src/client.rs (L478-499)
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
```

**File:** src/plans/mod.rs (L2081-2094)
```rust
    let orb_relay = orb.orb_relay.as_mut().expect("orb_relay to exist");

    tracing::info!("Waiting for self-serve biometric-capture trigger...");
    if let Err(e) = orb_relay
        .wait_for_msg::<self_serve::app::v1::StartCapture>(self_serve_app_capture_trigger_timeout)
        .await
    {
        if let Err(e) = orb_relay.send(self_serve::orb::v1::CaptureTriggerTimeout {}).await {
            tracing::warn!("failed to send CaptureTriggerTimeout: {e}");
        };
        orb.ui.signup_fail(SignupFailReason::Timeout);
        tracing::warn!("Self-serve biometric-capture start was not triggered: {e}");
        return Ok(false);
    };
```
