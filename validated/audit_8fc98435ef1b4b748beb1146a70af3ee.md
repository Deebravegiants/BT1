### Title
Missing sender-authorization check on `RequestState` handling allows unauthenticated replay of the last orb-relay signup message - (File: `orb-relay-client/src/client.rs`)

### Summary
`PollerAgent::main_loop` in `orb-relay-client/src/client.rs` validates the sender of every incoming relay message by comparing `src.id` against the expected peer (`self.config.dst_id`), except for messages matching `self_serve::app::v1::RequestState`. For that message type, the last outgoing signup message is unconditionally replayed to whoever sent the request, with no identity check performed at all. This mirrors the root cause of the referenced report: an authorization check that is supposed to bind a privileged action to a specific verified counterparty is bypassed for one specific code path, letting an attacker-controlled "sender" identity go completely unchecked.

### Finding Description
In the message-receive branch of `main_loop`: [1](#0-0) 

every other payload type is gated by `else if src.id != self.config.dst_id { ...skip... }`, enforcing that only the paired peer (the counterpart Orb/App identified by the session's `dst_id`) can push data into the local buffer or otherwise be treated as trusted. However, the special case:

```rust
if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
}
```

is evaluated *before* the `src.id != self.config.dst_id` check, and it never checks `src.id` at all. Any entity that is able to place a `RequestState` payload on this session's relay stream — regardless of its `src` identity — will cause the orb-relay client to resend `self.last_message` (the last message the Orb/App actually sent to its counterpart) to that requester.

This is architecturally analogous to the `CompoundToNotionalV2.notionalCallback` bug: the code path meant to be reachable only by the verified/paired counterparty (`sender == address(this)` in the original; `src.id == self.config.dst_id` here) has a bypass condition that lets an attacker skip the authorization check by hitting a specific parameter/message shape. Here, sending a `RequestState`-typed payload sidesteps the src-identity check that every other message type is subjected to.

### Impact Explanation
`last_message` holds the most recent signup/session-lifecycle payload sent over this orb↔app relay channel (e.g. `AnnounceOrbId`, `CaptureEnded`, `SignupEnded`, and other `self_serve::orb::v1`/`self_serve::app::v1` state messages used throughout the signup flow orchestrated in `src/plans/mod.rs`). If the underlying relay transport or session model ever permits more than one identity to inject payloads onto a given session id (e.g., a second entity claiming the correct session/orb id but a different `src.id`, a replayed/hijacked stream, or a backend routing bug), this bypass discloses/duplicates the last signup-state message to an unverified party instead of only the intended paired peer — a cross-signup/cross-session state disclosure that undermines the identity binding the `src.id != dst_id` check is meant to enforce everywhere else in this function.

### Likelihood Explanation
Exploitability is conditional on whether the relay server (out of scope, backend-side) can be made to deliver a `RelayConnectResponse` with an `src` that isn't the legitimate paired peer, or whether multiple concurrent connections can share the same session/dst_id routing. This cannot be fully confirmed from the orb-core codebase alone since the trust boundary partially depends on the backend relay's connection/session enforcement, which is not visible in this repository. Within orb-core itself, the code demonstrates a genuine inconsistency: the `RequestState` branch is the only one that omits the exact identity check that is otherwise applied uniformly, which is a concrete, reachable code defect regardless of the backend's session guarantees.

### Recommendation
Move the `src.id == self.config.dst_id` check ahead of the `RequestState` handling so it applies uniformly to all payload types, e.g.:

```rust
if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: {:?}", src.id);
} else if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else {
    self.handle_message(...).await?;
}
```
This ensures the replay-last-message behavior is only ever granted to the verified counterparty, closing the parameter/branch-based authorization bypass.

### Proof of Concept
1. An Orb and App establish a relay session identified by `orb_id`/`session_id`, with the Orb's `Config.dst_id` set to the app's session id (see `Client::new_as_orb`/`new_as_app` in `orb-relay-client/src/client.rs`, lines 146-154).
2. The Orb sends a normal signup-lifecycle message (e.g. `SignupEnded`), which is cached as `self.last_message` (client.rs, line 499).
3. A second entity — one that is able to get a `RelayConnectResponse::Payload` delivered on this stream with an `src` different from the legitimate app's id (e.g., through relay-side session/routing weaknesses, which are outside orb-core) — sends a payload matching `self_serve::app::v1::RequestState`.
4. Because the code checks `RequestState::matches(&payload)` before verifying `src.id == self.config.dst_id` (client.rs, lines 436-440), the Orb immediately replays `self.last_message` to this unverified sender, without ever hitting the `else if src.id != self.config.dst_id` rejection branch that governs every other message type. [2](#0-1)

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
