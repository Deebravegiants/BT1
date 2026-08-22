## Analysis

I investigated the reachable message-handling code in `orb-relay-client`, the crate `orb-core` uses for orb⇄app communication during self-serve signups, and found a concrete analog: an access-control check that is present for the general message path but is explicitly skipped for one specific message type, allowing state to be returned without the identity check that guards every other inbound message.

### Title
Missing sender authorization check on `RequestState` handling allows unauthorized disclosure of the orb's last signup-state message - (File: `orb-relay-client/src/client.rs`)

### Summary
In `PollerAgent::main_loop` (`orb-relay-client/src/client.rs`), every inbound relay payload is supposed to be validated against the expected communication peer before being processed (`src.id != self.config.dst_id`). However, the `RequestState` message type bypasses this check entirely: as soon as a payload matches `self_serve::app::v1::RequestState`, the orb immediately replies with its `last_message` to whoever sent it, without checking `src.id` at all.

### Finding Description
The core message dispatch loop is: [1](#0-0) 

```
message = response_stream.next() => {
    match message {
        Some(Ok(RelayConnectResponse { msg: Some(relay_connect_response::Msg::Payload(RelayPayload { src: Some(src), dst, seq, payload: Some(payload) })) })) => {
            if self_serve::app::v1::RequestState::matches(&payload).is_some() {
                sender_tx.send(self.last_message.clone()).await...
            } else if src.id != self.config.dst_id {
                tracing::error!("Skipping received message from unexpected source...");
            } else {
                self.handle_message(...).await?;
            }
        }
        ...
    }
}
```

For every other payload type, the client enforces `src.id != self.config.dst_id` before accepting the message, i.e. it only trusts messages whose claimed source matches the configured peer for that signup session (`Config::dst_id`, set in `Client::new_as_orb`/`new_as_app`) [2](#0-1) . This check exists precisely because the relay transport itself does not appear to strongly bind message delivery to `src` identity at the client's trust boundary — otherwise the check would be redundant.

The `RequestState` branch is evaluated first and unconditionally responds with `self.last_message` — the most recently sent output (e.g. `CaptureStarted`, `CaptureEnded`, `AgeVerificationRequiredFromOperator`, or `SignupEnded{success, failure_feedback}`) — to the sender, regardless of whether `src.id` matches the paired peer for that session [3](#0-2) .

### Impact Explanation
Any entity able to route a `RequestState` payload to an orb's relay session (i.e. anyone who can address `dst` = the orb's session identifier, which is exchanged as part of the self-serve QR/app flow) can pull the current signup-state snapshot (capture started/ended, age-verification-required, signup ended with success/failure feedback) without passing the same-peer check applied to all other messages. This is a cross-signup state disclosure: an unauthorized party can observe the live progress/outcome of another user's in-flight signup on that orb, which is sensitive operational/biometric-flow state that should only be visible to the paired self-serve app.

### Likelihood Explanation
The check bypass is unconditional and requires no privileged credentials beyond being able to address a `RequestState` payload with the target session's `dst_id` — something an app/relay client typically already knows via the self-serve QR flow, and is exactly the kind of "unprivileged, valid-protocol-flow abuse" this bug class covers. It requires no MITM, no server compromise — only a reachable relay connection.

### Recommendation
Move the `src.id != self.config.dst_id` check ahead of (or apply it to) the `RequestState` branch so that only the verified paired peer can trigger a resend of `last_message`. Do not special-case any message type to skip the sender-authorization check.

### Proof of Concept
1. Attacker connects an `orb-relay` client (or crafts a payload with) `RequestState` addressed to a target orb's active session `dst_id`.
2. Orb's `main_loop` matches `RequestState` first, sending `self.last_message` back to the attacker's send channel, without ever evaluating `src.id != self.config.dst_id`.
3. Attacker receives the orb's last self-serve state message (e.g. `SignupEnded{success, failure_feedback}`) for a session they are not the legitimate paired app for. [4](#0-3)

### Citations

**File:** orb-relay-client/src/client.rs (L144-154)
```rust
    /// Create a new client that sends messages from an Orb to an App
    #[must_use]
    pub fn new_as_orb(url: String, token: String, orb_id: String, session_id: String) -> Self {
        Self::new(url, Auth::Token(TokenAuth { token }), orb_id, session_id, Mode::Orb)
    }

    /// Create a new client that sends messages from an App to an Orb
    #[must_use]
    pub fn new_as_app(url: String, token: String, session_id: String, orb_id: String) -> Self {
        Self::new(url, Auth::Token(TokenAuth { token }), session_id, orb_id, Mode::App)
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

**File:** orb-relay-client/src/lib.rs (L32-43)
```rust
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
```
