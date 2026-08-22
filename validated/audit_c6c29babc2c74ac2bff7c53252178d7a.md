### Title
Unauthenticated `RequestState` message bypasses source-identity verification in Orb-Relay client, enabling cross-session state disclosure/griefing - (File: `orb-relay-client/src/client.rs`)

### Summary
The `orb-relay-client` `PollerAgent::main_loop` enforces a source-identity check (`src.id != self.config.dst_id`) before accepting any relayed message from the paired counterparty. However, this check is unconditionally skipped whenever the incoming payload matches `self_serve::app::v1::RequestState`: the agent immediately replays its cached `last_message` to whoever sent it, without verifying that the sender is actually the authenticated session peer. This mirrors the reported `TrancheVault` pattern, where an action (`deposit`) that should only be permitted between an authorized pair of accounts instead performs a sensitive, state-affecting operation (`addRedemptionRequest`'s lockout reset) on behalf of anyone who supplies the right shape of request, without checking that the caller is actually the intended counterparty.

### Finding Description
In the connection loop that mediates Orb⟷App communication for self-serve signups, every incoming message is expected to originate from the previously-paired peer (`self.config.dst_id`), enforced here: [1](#0-0) 

Note that the `RequestState` branch is evaluated first and unconditionally: if `self_serve::app::v1::RequestState::matches(&payload).is_some()`, the agent responds with `self.last_message.clone()` to the sender — completely bypassing the `else if src.id != self.config.dst_id` guard that protects the `handle_message` path used for every other payload type. The matcher itself performs no source validation, it only inspects the payload shape: [2](#0-1) 

`last_message` holds the most recently sent outbound payload for the session (e.g. `AnnounceOrbId`, `SignupEnded`, or pending signup-relay state) and is updated on every outgoing send: [3](#0-2) 

This client is instantiated by orb-core itself during self-serve signup to announce the Orb's identity to the paired app and to gate/notify biometric-capture triggers: [4](#0-3) [5](#0-4) 

Just as the `TrancheVault.deposit()` function checked only that both the depositor and the receiver were "approved" without verifying that the depositor was actually authorized to act on the receiver's redemption timing, this relay client checks only that the payload matches the `RequestState` shape, not that the sender is the legitimate session counterparty identified by `dst_id`. Any party able to route a message into this client's stream can therefore trigger the privileged "replay last state" action intended exclusively for the paired signup session, disclosing session state (which signup/round the state belongs to) to an unauthorized third party and interfering with the legitimate self-serve signup flow.

### Impact Explanation
An unauthorized party masquerading as the session peer can force disclosure of the Orb's/App's last relayed signup message (e.g. `AnnounceOrbId`, `SignupEnded`) outside of the intended pairing, and can repeatedly trigger this replay to interfere with a genuine self-serve signup in progress — a form of cross-signup state bleed / griefing analogous to the reported lending vault issue, where an unauthorized actor manipulates state belonging to another party's session without being that party.

### Likelihood Explanation
The bypass is unconditional and requires no additional privilege beyond being able to place a `RequestState`-shaped payload onto the stream that the vulnerable client is reading from; it does not depend on race conditions, timing windows, or misconfiguration — any message shaped as `RequestState` triggers the bypass regardless of `src.id`.

### Recommendation
Move the `src.id == self.config.dst_id` check ahead of the `RequestState` special case so that state-replay is only performed for messages verified to originate from the authenticated session counterparty, consistent with how all other payload types are already validated in the same loop.

### Proof of Concept
1. Establish (or hijack) a relay stream that can deliver a payload to the target client's `response_stream` (any `RelayPayload` with `src` distinct from `self.config.dst_id`).
2. Craft the payload as `self_serve::app::v1::RequestState {}` wrapped per `PayloadMatcher` (`orb-relay-client/src/lib.rs:32-43`).
3. Because the `RequestState::matches(&payload).is_some()` branch is checked first in `main_loop` (`orb-relay-client/src/client.rs:436-440`), the client immediately replies with `self.last_message.clone()` — the previous privileged payload (e.g., `AnnounceOrbId`/`SignupEnded`) — without ever reaching the `src.id != self.config.dst_id` rejection path that governs every other message type.

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

**File:** src/plans/mod.rs (L2068-2106)
```rust
async fn proceed_with_biometric_capture(orb: &mut Orb) -> Result<bool> {
    let Config {
        self_serve,
        self_serve_app_skip_capture_trigger,
        self_serve_app_capture_trigger_timeout,
        ..
    } = *orb.config.lock().await;
    if !self_serve || self_serve_app_skip_capture_trigger {
        // Biometric capture not gated by a user action. Continue.
        orb.ui.signup_start();
        return Ok(true);
    }

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

    tracing::info!("Self-serve biometric-capture start triggered");
    orb.ui.signup_start();

    tracing::info!("Self-serve: Informing orb-relay that biometric_capture has started");
    orb_relay
        .send(self_serve::orb::v1::CaptureStarted {})
        .await
        .inspect_err(|e| tracing::error!("Relay: Failed to CaptureStarted: {e}"))?;

    Ok(true)
}
```

**File:** src/plans/mod.rs (L2108-2122)
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
```
