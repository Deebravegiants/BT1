### Title
`RequestState` handler bypasses source-identity filter, allowing replay of `last_message` to unverified sender - (File: `orb-relay-client/src/client.rs`)

### Summary
In `PollerAgent::main_loop`, the `RequestState` branch is checked before the `src.id != self.config.dst_id` guard, so it fires and replays `self.last_message` regardless of who sent the message. Every other payload type is subject to the `dst_id` source check, but `RequestState` short-circuits it entirely.

### Finding Description
In the `response_stream.next()` arm, the received message is dispatched as follows: [1](#0-0) 

The `self_serve::app::v1::RequestState::matches(&payload).is_some()` check is evaluated first and, if it matches, immediately replays `self.last_message` over `sender_tx` — with no check on `src`, `src.id`, or `self.config.dst_id` at all. Only the `else if` branch (for any non-`RequestState` payload) enforces `src.id != self.config.dst_id` as an identity filter. This means the one guard designed to prevent cross-session message injection is structurally skipped for `RequestState`.

`self.last_message` is not per-requester state; it is simply the most recent `RelayConnectRequest` this agent sent (set on every outgoing message at line `self.last_message = relay_message.clone().into();`), which can be `AnnounceOrbId`, `SignupEnded`, `CaptureStarted`, or any other payload tied to the current signup/session: [2](#0-1) 

The code itself acknowledges that the relay stream can carry multiplexed traffic from multiple sources, which is exactly why the `src.id != self.config.dst_id` filter exists: [3](#0-2) 

Because the `RequestState` branch executes unconditionally on the decoded payload type alone, any message on the stream that decodes as `self_serve::app::v1::RequestState` — irrespective of its declared `src` — triggers a resend of the last state-bearing message, defeating the very isolation the subsequent `else if` is meant to enforce.

### Impact Explanation
This allows replay/disclosure of session state (e.g., `AnnounceOrbId`, `SignupEnded`, `CaptureStarted`) tied to a specific orb/session pairing to a requester whose identity was never validated against `self.config.dst_id`. This corresponds to a cross-signup state bleed / unauthorized disclosure of signup-session data, matching a "session isolation break / information disclosure" class of impact rather than full account takeover, since the replayed payloads observed in this codebase (`AnnounceOrbId`, `SignupEnded`) do not themselves contain biometric templates, but do leak orb/session/signup outcome metadata to an unverified party.

### Likelihood Explanation
Exploitability depends on whether the relay server multiplexes messages from unrelated sessions onto the same client-facing stream so that an attacker-controlled `RequestState` message reaches this specific `PollerAgent` instance's `response_stream`. The client code's own TODO comment acknowledges this multiplexing is a known, current characteristic of the connect/subscribe model (`"That will avoid multiplexing messages from different sources"` implies it currently does multiplex). Given that, the bypass is trivially reachable by any entity able to place a `RequestState`-typed payload onto that stream, with no further preconditions (no auth token forgery, no MCU access) — it only requires reaching the relay as an ordinarily-authenticated entity and crafting the message type before/without matching identity.

### Recommendation
Move the `RequestState` check inside (or after) the `src.id == self.config.dst_id` validation so replay is only granted to the verified counterpart:
```rust
if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: {:?}: {payload:?}", src.id);
} else if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await.wrap_err("Failed to send outgoing message")?;
} else {
    self.handle_message(...).await?;
}
```
This preserves identical `RequestState` functionality for legitimate `dst_id`-matching peers while closing the identity bypass.

### Proof of Concept
Unit test on `PollerAgent::main_loop` (or a focused test exercising the same match logic extracted into a helper):
1. Configure `PollerAgent` with `config.dst_id = "expected-peer"` and set `self.last_message` to a `RelayConnectRequest` wrapping a `SignupEnded { success: true, .. }` payload (simulating prior session state).
2. Feed the stream a `RelayConnectResponse` containing a `RelayPayload` with `src.id = "attacker-id"` (≠ `dst_id`) and `payload = RequestState{}`.
3. Assert that `sender_tx` receives `self.last_message` (current behavior — this is the bug) instead of being dropped/logged as "unexpected source" (expected/fixed behavior).
4. After applying the fix, assert the same crafted message from `"attacker-id"` is rejected (logged, not replayed), and only a `RequestState` from `src.id == "expected-peer"` triggers the replay.

### Citations

**File:** orb-relay-client/src/client.rs (L389-391)
```rust
    // TODO: We need to split auth and subscription. Maybe ideally we issue 1 connect and then a subscribe that will notify
    // the server that we care about messages from a certain queue only. That will avoid multiplexing messages from
    // different sources.
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

**File:** orb-relay-client/src/client.rs (L488-500)
```rust
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
