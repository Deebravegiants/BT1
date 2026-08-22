## Analysis

The reported Llama bug class is: **a state-mutating/state-returning code path that should be gated to an authorized/paired caller instead skips that authorization check entirely for a specific input, letting an unauthorized party read or corrupt privileged session state.**

The strongest reachable analog in `orb-core` is in the `orb-relay-client` crate, which implements the agent-IPC channel orb-core uses to coordinate self-serve signups with the mobile app over the Worldcoin relay service.

### Title
Unauthorized relay peer can bypass source-identity check and retrieve the last cached session message via `RequestState` - (File: `orb-relay-client/src/client.rs`)

### Summary
`PollerAgent::main_loop` validates that every inbound relay message actually originates from the expected paired peer (`src.id == self.config.dst_id`) before processing it. However, this authorization check is placed in an `else if` branch that is only reached if the payload is *not* a `self_serve::app::v1::RequestState` message. For `RequestState` payloads, the client immediately replies with `self.last_message.clone()` — completely bypassing the `src.id` check.

### Finding Description [1](#0-0) 

The relevant branch:
```rust
if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: ...");
} else {
    self.handle_message(...).await?;
}
``` [2](#0-1) 

Every other inbound message type is subject to the `src.id != self.config.dst_id` guard, which exists specifically to reject relay traffic from an entity other than the one this session is paired with. The `RequestState` case is checked first and unconditionally re-sends `self.last_message` — the previously sent `RelayConnectRequest` (which, in the orb→app direction, can be an `AnnounceOrbId`, `SignupEnded`, `CaptureStarted`, or other self-serve session payload) — without ever consulting `src`. This mirrors the Llama pattern where a function meant to only be invoked by a trusted caller was left reachable by anyone, letting that caller mutate/read state meant to be tied to a specific action/session.

### Impact Explanation
Because the identity check is skipped for `RequestState`, any relay entity able to route a `RequestState` payload into this stream (e.g., another orb/app session mux'd on the same relay connection, or a peer whose token authenticates it to the relay server but who is not the `dst_id` this `Client` is paired with) can force replay of the last cached message meant for the legitimate paired peer. In the self-serve signup flow this is the mechanism transporting `AnnounceOrbId` (orb/session identifiers) and signup lifecycle events (`SignupEnded`, `CaptureStarted`, `CaptureTriggerTimeout`) between the orb and the user's phone app. Bypassing the source check here allows disclosure of session/signup state to an unauthorized relay party and creates a cross-session state-bleed path, since the same defensive check that would normally reject a mismatched `src.id` is defeated for this message type.

### Likelihood Explanation
The bypass requires no privilege beyond being able to deliver a `RequestState`-shaped payload over the relay stream this client is subscribed to — it is a pure logic/ordering bug (`if`/`else if` short-circuit), not something requiring compromise of the relay server's auth. Any party capable of reaching the client's `response_stream` with an appropriately crafted payload triggers it deterministically, with no reliance on race conditions or timing.

### Recommendation
Move the `src.id != self.config.dst_id` check ahead of the `RequestState` handling so the source-identity verification is enforced unconditionally for **all** inbound payload types, including `RequestState`:
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
1. Establish a relay connection as an unauthorized entity that is not `self.config.dst_id` for the target `Client` session (i.e., an entity other than the orb's or app's paired counterpart for that `session_id`/`orb_id`).
2. Send a `self_serve::app::v1::RequestState {}` payload targeting that session's stream (as demonstrated by the legitimate flow in `orb_to_app_with_state_request` in `orb-relay-client/src/bin/manual-test.rs`, lines 268-364, which shows the app invoking `RequestState` to pull the orb's last state). [3](#0-2) 
3. Observe that `PollerAgent::main_loop` replies with `self.last_message.clone()` regardless of the `src.id` mismatch, because the `RequestState::matches` branch is evaluated before the `src.id != self.config.dst_id` guard. [4](#0-3) 
4. The unauthorized entity thus receives the last message intended only for the properly paired peer of that signup session.

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

**File:** orb-relay-client/src/bin/manual-test.rs (L292-310)
```rust
    let now = Instant::now();
    app_client.send(self_serve::app::v1::RequestState {}).await?;
    tracing::info!("Time took to send RequestState from the app: {}ms", now.elapsed().as_millis());

    let now = Instant::now();
    'ext: loop {
        #[allow(clippy::never_loop)]
        for msg in app_client.get_buffered_messages().await {
            tracing::info!(
                "Received message: from: {:?}, to: {:?}, seq: {:?}, payload: {:?}",
                msg.src,
                msg.dst,
                msg.seq,
                debug_any(&msg.payload)
            );
            break 'ext;
        }
    }
    tracing::info!("Time took to receive a message: {}ms", now.elapsed().as_millis());
```
