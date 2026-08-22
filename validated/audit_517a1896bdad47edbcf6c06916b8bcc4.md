## Title
Orb-Relay client bypasses source-identity check for `RequestState` messages, allowing any relay-connected peer to trigger last-message replay - (File: `orb-relay-client/src/client.rs`)

### Summary
The reported bug pattern is an authorization check that validates the wrong party (a receiver instead of the actual caller), letting an unauthorized third party trigger a state-affecting action intended to be gated by identity. In `orb-relay-client`, the `PollerAgent::main_loop` function performs an analogous mistake: it special-cases one payload type (`self_serve::app::v1::RequestState`) and acts on it **before** checking whether the message actually originated from the expected peer (`src.id == self.config.dst_id`), so the source-identity check is bypassed entirely for that message type.

### Finding Description
In `main_loop`, incoming relay messages are matched as follows: [1](#0-0) 

```
message = response_stream.next() => {
    match message {
        Some(Ok(RelayConnectResponse {
            msg: Some(relay_connect_response::Msg::Payload(RelayPayload {
                src: Some(src), dst, seq, payload: Some(payload),
            })),
        })) => {
            if self_serve::app::v1::RequestState::matches(&payload).is_some() {
                sender_tx.send(self.last_message.clone()).await...
            } else if src.id != self.config.dst_id {
                tracing::error!("Skipping received message from unexpected source: ...");
            } else {
                self.handle_message(...).await?;
            }
        }
``` [2](#0-1) 

The `src.id != self.config.dst_id` check — the only mechanism verifying the message actually came from the paired peer (the specific Orb or App session the client is bound to) — is only evaluated in the `else if` branch. Any payload that matches `RequestState` skips that check unconditionally and causes the client to resend `self.last_message` (the last outgoing state payload) to the relay, regardless of who sent the `RequestState` request. This mirrors the C4 finding's root cause: an authorization/identity gate exists in the code but is checked against (or applied to) the wrong condition, so the intended party-binding is not enforced for a specific action path.

### Impact Explanation
`self.last_message` holds session state previously sent over the relay channel (e.g., Orb-side signup/session state broadcast to the paired app, per `no_state()`/`last_message` usage). Because the relay-side `src` identity is not verified before honoring a `RequestState` request, any entity able to inject a `RequestState`-typed payload into the connection's message stream for a given `dst_id`/session can force the client to re-broadcast its last state to that channel without being the legitimate paired peer. This is a state re-disclosure/replay primitive within the same trust boundary problem class as the C4 report (a receiver/caller identity check that is not actually enforced), even though the concrete blast radius here (session/state replay) is narrower than an asset-drain.

### Likelihood Explanation
Exploitability depends entirely on whether the relay server enforces `src` correctly upstream, and whether an unprivileged client is able to have a `RequestState` payload routed to a specific `dst_id` (channel/session) it does not own. This is a `no-impact` / `hard-to-verify` scenario without deeper access to `orb-relay-server` (not present in this repo) and the relay's own auth/routing model, so the actual reachability of this code path by an unprivileged, non-paired peer cannot be confirmed from `orb-core--002` alone.

### Recommendation
Move the `src.id == self.config.dst_id` check to apply uniformly to all payload types, including `RequestState`, before taking any state-replaying action:
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
Not independently verifiable from this repository: reachability requires knowledge of the `orb-relay-server`'s routing/auth semantics (not present in `orb-core--002`), specifically whether it allows a non-paired client to have a `RequestState` payload delivered against an arbitrary `dst_id`. The client-side logic itself is confirmed as shown above: for any incoming `RelayPayload` whose `payload` matches `self_serve::app::v1::RequestState`, `main_loop` sends `self.last_message` back without evaluating `src.id != self.config.dst_id` at all [3](#0-2) .

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
