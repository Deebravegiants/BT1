### Title
Orb-Relay Client Skips Source-Identity Verification for `RequestState` Messages, Allowing Unauthenticated Replay of Signup State on the Multiplexed IPC Channel - ([File: orb-relay-client/src/client.rs])

### Summary
The `PollerAgent::main_loop` function in `orb-relay-client/src/client.rs` verifies that incoming relay messages originate from the expected paired peer (`src.id == self.config.dst_id`) before processing them — except for one specific message type. When a payload matches `self_serve::app::v1::RequestState`, the client immediately resends its last outbound signup-state message without any check on the sender's identity, bypassing the very authorization boundary enforced for every other message type on this shared, multiplexed IPC channel.

### Finding Description
In the connection loop, incoming payloads are dispatched with the following logic: [1](#0-0) 

If the payload matches `RequestState`, the code unconditionally re-sends `self.last_message` — the orb's most recent signup-state payload — with **no verification that the message came from the paired app/orb (`src.id != self.config.dst_id`)**. Every other payload is required to pass that identity check first. The maintainers' own comment above `main_loop` explicitly acknowledges the underlying trust problem: [2](#0-1) 

This confirms that the relay connection is a shared/multiplexed queue carrying messages from multiple distinct sources, and that source-based authorization is required precisely because the transport does not otherwise segregate senders. The `RequestState` branch is a special-cased exception to that authorization model, so any entity able to place a `RequestState`-typed payload onto the queue — without being the legitimate paired counterpart — can force the orb (or app) client to retransmit whatever signup-state message it last sent (e.g. `CaptureStarted`, `CaptureEnded`, `SignupEnded`, etc., used throughout the self-serve signup flow in `src/plans/mod.rs`, such as `proceed_with_biometric_capture` and `after_biometric_capture`).

### Impact Explanation
This breaks the identity-binding guarantee of the self-serve signup relay channel: an unpaired/unauthorized party on the multiplexed queue can trigger retransmission of privileged signup-state transitions without ever having been authenticated as the actual paired app or orb for that session. Depending on what the "last message" was at the time, this can cause duplicate or stale signup-state notifications (e.g. re-announcing `SignupEnded`/`CaptureEnded`) to be delivered to the legitimate counterpart, creating state confusion in the signup state machine that is otherwise strictly gated by the `src.id == dst_id` check everywhere else in the same function. This is the same class of flaw as the CSXTrade issue: a state-transition/finalization path lacks the authorization check that is present on the "normal" path, letting an unprivileged actor manipulate a async trust boundary tied to a session it does not own.

### Likelihood Explanation
Exploitability depends on whether an attacker can place a `RequestState` payload onto the same multiplexed relay stream targeting a specific orb/app pair (i.e., whether the relay server segregates messages strictly per-connection or per-session, or whether — as the code comment implies — messages from multiple sources can currently reach the same client queue). Given the explicit TODO acknowledging multiplexing of different sources on this channel, and that this is the only payload type exempted from the identity check, this is a realistic and directly reachable trust-boundary gap for any unprivileged relay participant.

### Recommendation
Remove the special case for `RequestState` in `PollerAgent::main_loop`, and require the same `src.id == self.config.dst_id` verification for it as for all other payload types before triggering a resend of `self.last_message`. If a legitimate use case requires resending state to a reconnecting peer, the resend should be authorized based on verified peer identity/session token, not purely on payload type.

### Proof of Concept
1. An orb and its paired app establish a relay session via `Client::new_as_orb`/`new_as_app`, exchanging signup-state messages (e.g. `CaptureStarted`).
2. A third party capable of injecting a message onto the same multiplexed relay queue (without being the paired app, i.e. `src.id != dst_id`) sends a payload that unpacks to `self_serve::app::v1::RequestState`.
3. In `PollerAgent::main_loop`, the check `self_serve::app::v1::RequestState::matches(&payload).is_some()` succeeds first, short-circuiting the `src.id != self.config.dst_id` rejection branch that would otherwise apply.
4. The orb/app immediately resends `self.last_message` — a previously-sent signup-state payload — regardless of who actually requested it, demonstrating that the source-identity authorization enforced elsewhere in the same function is bypassed for this message type.

### Citations

**File:** orb-relay-client/src/client.rs (L388-392)
```rust
impl<'a> PollerAgent<'a> {
    // TODO: We need to split auth and subscription. Maybe ideally we issue 1 connect and then a subscribe that will notify
    // the server that we care about messages from a certain queue only. That will avoid multiplexing messages from
    // different sources.
    async fn main_loop(
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
