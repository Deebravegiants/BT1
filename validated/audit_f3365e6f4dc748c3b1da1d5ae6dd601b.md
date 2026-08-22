## Title
Missing sender-identity check for `RequestState` messages in `orb-relay-client` bypasses the sender validation enforced for all other relay messages - (File: `orb-relay-client/src/client.rs`)

### Summary
The Sherlock report describes `ERC1155Voucher.onERC1155BatchReceived()` omitting the `isValidToken[msg.sender]` check that its sibling function `onERC1155Received()` enforces, letting an unregistered caller reach privileged logic through the unguarded twin entry point. The orb-relay client exhibits the same asymmetric-validation pattern: every inbound relay payload is required to originate from the configured session peer (`src.id == self.config.dst_id`) before being buffered and processed, except payloads matching `self_serve::app::v1::RequestState`, which are handled *before* that identity check and therefore bypass it entirely.

### Finding Description
In `PollerAgent::main_loop`, incoming payloads are dispatched like this: [1](#0-0) 

The `else if src.id != self.config.dst_id` branch is the sole guard that restricts message processing to the expected session peer, and the `else` branch (`self.handle_message`) is where all legitimate application messages (e.g. `AnnounceOrbId`, `SignupEnded`, `StartCapture`, `CaptureStarted`) are buffered for the plan logic to consume. However, the very first branch — triggered when the payload matches `self_serve::app::v1::RequestState` — runs unconditionally, `send`-ing `self.last_message.clone()` back onto the relay connection with **no check that `src.id` equals `self.config.dst_id`**. This mirrors exactly the ERC1155Voucher flaw: one code path (`handle_message`/`onERC1155Received`) enforces sender validation, while the sibling path (`RequestState` handling/`onERC1155BatchReceived`) does not.

The `dst_id`/`src_id` values used for this pairing are the orb ID and the app-supplied `orb_relay_app_id` obtained from the user QR-code data during signup, and are wired together in `orb_relay_announce_orb_id`: [2](#0-1) 

Because `RequestState` is exempted from the peer-identity check, **any relay entity** (not only the paired app for this signup session) that can reach the relay stream and knows/guesses the orb's relay identity can send a `RequestState` message and force the orb-side client to immediately re-transmit `self.last_message` — the most recent signup/session-state message the orb sent (e.g. `AnnounceOrbId`, `SignupEnded`, `CaptureTriggerTimeout`) — without having to satisfy the same sender-authentication requirement enforced everywhere else in the same function.

### Impact Explanation
This breaks the intended invariant that only the paired session peer (validated via `src.id == dst_id`) can interact with a given orb-relay session, exactly as the original report's "only valid registered token can vouch" invariant was broken. An unauthenticated/unpaired relay client can:
- Trigger repeated retransmission of session state messages (replay/state-bleed across signup sessions) without passing the identity check applied to every other message type.
- Potentially interfere with or confuse the self-serve signup flow's state machine (which relies on `wait_for_msg` calls such as `wait_for_msg::<self_serve::app::v1::StartCapture>` in `proceed_with_biometric_capture`) by forcing extraneous retransmissions outside of the validated peer relationship.

This qualifies as a cross-signup-session state-bleed exposure caused by an asymmetric/missing authorization check identical in shape to the reported ERC1155Voucher bug.

### Likelihood Explanation
Exploitation only requires connecting to the relay backend as any entity and sending a `RequestState` payload while knowing/guessing the target `dst_id` (orb ID or app session ID, values that are exchanged over the relay protocol and QR flow); no privileged credentials beyond a valid relay auth token are required, and the check is skipped unconditionally for this one message type in production code (not test-only).

### Recommendation
Move the `src.id != self.config.dst_id` validation ahead of the `RequestState` special-case, or explicitly validate `src.id == self.config.dst_id` inside that branch before resending `self.last_message`, so `RequestState` handling is subject to the same sender-identity check as `handle_message`:
```rust
if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: {:?}", src.id);
} else if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await.wrap_err("Failed to send outgoing message")?;
} else {
    self.handle_message(RelayPayload { src: Some(src), dst, seq, payload: Some(payload) }, message_buffer).await?;
}
```

### Proof of Concept
1. Establish an orb-side relay session with `dst_id = orb_relay_app_id` as done in `orb_relay_announce_orb_id`. [3](#0-2) 
2. As a third-party relay client authenticated with a valid (but unrelated) token, send a `self_serve::app::v1::RequestState` payload addressed to the orb's queue, using an `src.id` different from the orb's configured `dst_id`.
3. Observe that unlike any other message type, the `src.id != self.config.dst_id` guard at `orb-relay-client/src/client.rs:441` is never evaluated for this payload — the orb immediately re-sends `self.last_message` (the last state message, e.g. `SignupEnded`/`AnnounceOrbId`), demonstrating that the sender-identity enforcement present for all other message types is absent for `RequestState`.

### Citations

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

**File:** src/plans/mod.rs (L2108-2126)
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
```
