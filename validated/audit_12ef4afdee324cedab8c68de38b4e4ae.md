### Title
Missing sender authorization allows any relay peer to trigger orb state replay - (File: orb-relay-client/src/client.rs)

### Summary
In `orb-relay-client`, incoming relay messages are supposed to be validated against the expected paired counterparty (`self.config.dst_id`) before being processed. However, when the incoming payload matches `self_serve::app::v1::RequestState`, the client responds by re-sending its `last_message` **before** the `src.id != self.config.dst_id` check is applied, so the sender-identity check is bypassed entirely for this message type.

### Finding Description
In the connection main loop, incoming `RelayPayload`s are matched and handled as follows: [1](#0-0) 

The `RequestState` branch is evaluated first and unconditionally triggers a resend of `self.last_message` to the relay, with no check that `src.id == self.config.dst_id`. Only the `else if` branch (for all other message types) performs that identity check: [2](#0-1) 

This mirrors the pattern in the external report: a state-affecting/state-disclosing action (`withdrawInterest(_id, _lender)` in Sublime, `RequestState` handling here) is performed on behalf of/in reply to an unauthenticated or unverified caller, because the access-control check (`msg.sender == _lender` / `src.id == self.config.dst_id`) is either missing or skipped for that specific code path. The `Client` struct is used both in `Mode::Orb` (server side, i.e., what orb-core actually runs) and `Mode::App`, and `last_message` holds the most recently sent state/signup payload — data intended only for the paired app/orb for a given `session_id`/`dst_id`.

### Impact Explanation
Because the `RequestState` handling path skips the `src.id != self.config.dst_id` check, any relay entity capable of sending a `RequestState` payload to the connected client can force it to replay its last outgoing state message — regardless of whether that requester is the legitimately paired counterparty for the session. This is a cross-signup/cross-session state disclosure: state information intended for one paired app/session (e.g., signup progress/state events forwarded over dbus/relay) can be obtained by an unauthorized peer, violating the identity-binding invariant that ties orb/app communication to a specific `session_id`.

### Likelihood Explanation
Exploitability depends on the relay server's own message-routing guarantees (whether it independently enforces src/dst pairing before delivering a `RelayConnectResponse`). If the relay server allows any authenticated relay client to address a `RequestState` message to another orb/app pair (or if `dst`/session-id checks on the server side are not airtight), the client-side check bypass in this code path becomes directly exploitable, since it is the *only* application-level defense guarding this operation. This is a plausible, low-complexity trust-boundary gap in the agent/app-to-orb IPC layer, similar in class (missing access-control check on a state-disclosing operation) to the referenced Sublime finding, though its real-world reachability depends on server-side routing behavior that is outside orb-core.

### Recommendation
Move (or duplicate) the `src.id != self.config.dst_id` check so it is enforced before handling `RequestState`, e.g.:

```rust
if src.id != self.config.dst_id {
    tracing::error!(
        "Skipping received message from unexpected source: {:?}",
        src.id
    );
} else if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await.wrap_err("Failed to send outgoing message")?;
} else {
    self.handle_message(
        RelayPayload { src: Some(src), dst, seq, payload: Some(payload) },
        message_buffer,
    ).await?;
}
```

This ensures the identity check in `orb-relay-client/src/client.rs` is applied uniformly to all inbound message types, closing the bypass for `RequestState`.

### Proof of Concept
1. A malicious or misbehaving relay peer connects to the relay server with a different `src_id`/session than the one paired with a target orb/app `Client`.
2. It sends a payload matching `self_serve::app::v1::RequestState` addressed such that it reaches the target `Client`'s `response_stream`.
3. In `main_loop` (`orb-relay-client/src/client.rs`, lines ~425-452), the `RequestState::matches` branch fires first and calls `sender_tx.send(self.last_message.clone())`, replaying the last state payload — without ever reaching the `src.id != self.config.dst_id` check that would have rejected an unpaired sender.
4. The attacker thereby learns/obtains state information (e.g. last signup/session state) intended only for the legitimate paired counterpart.

Note: full verification of server-side relay routing/authorization for `dst`/session binding could not be completed within this analysis (that logic lives outside `orb-core`'s indexed files), so the exploitability assessment above assumes the relay server does not independently block cross-session `RequestState` delivery.

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
