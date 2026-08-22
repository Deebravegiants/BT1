### Title
Missing sender authentication when handling `RequestState` messages in the Orb-Relay client causes unauthenticated message-triggered resend (griefing) - ([File: orb-relay-client/src/client.rs])

### Summary
The relay client's `PollerAgent::main_loop` enforces a same-source check (`src.id != self.config.dst_id`) before processing any inbound relay message — except for one message type, `self_serve::app::v1::RequestState`, which is unconditionally honored regardless of the sender's identity. This mirrors the reported bug class: a state-mutating/state-emitting action that is meant to be restricted to a specific trusted counterpart but has no enforced access control, letting an unprivileged party trigger it.

### Finding Description
In `PollerAgent::main_loop`, incoming relay payloads are matched in this order: [1](#0-0) 

```
if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: ...");
} else {
    self.handle_message(...)
}
```

Every other inbound payload is validated against `src.id == self.config.dst_id` — the identity established at connect time for the counterparty (orb or app) in this signup session — before being accepted [2](#0-1) . The `RequestState` branch, however, bypasses this check entirely and immediately re-sends `self.last_message` to the queue, with no verification of `src`.

The code's own comment acknowledges the underlying trust-boundary weakness that makes this reachable by a non-counterpart sender: "We need to split auth and subscription... That will avoid multiplexing messages from different sources," indicating messages from sources other than the expected dst can currently reach this same stream [3](#0-2) . `RequestState` is a real, unauthenticated-by-content message defined and sent by the app side of the self-serve signup flow [4](#0-3) , and is used during the biometric-capture trigger window of a live signup [5](#0-4) .

### Impact Explanation
Because the `RequestState` handler skips the identity check that every other message type is subject to, any entity able to inject a payload onto this multiplexed relay stream (not just the legitimate paired app/orb for the session) can force the Orb-side (or App-side) client to resend its last transmitted message on demand — repeatedly and at will. In the context of an active self-serve signup, the "last message" can be signup-lifecycle state such as `CaptureStarted`, `CaptureTriggerTimeout`, or `SignupEnded`. An unauthorized party forcing repeated re-emission of these messages can desynchronize or grief the legitimate app/orb pairing's signup state machine — a direct analog of the reported griefing pattern where an unprivileged caller repeatedly invokes a state-mutating/state-emitting action meant to be restricted, denying the legitimate party a clean signup flow.

### Likelihood Explanation
The check bypass is unconditional and requires no special permission beyond being able to place a message on the multiplexed stream — which the code's own TODO states is possible today ("multiplexing messages from different sources" on the same connection). This makes the missing check reachable without any hardware, operator, or malicious-peer assumptions; it only requires network-level message injection capability against the relay session, which fits within the self-serve app's trust boundary that regular (non-operator, non-hardware) users interact with.

### Recommendation
Apply the same `src.id == self.config.dst_id` authentication check to the `RequestState` branch before resending `self.last_message`, so that only the verified counterparty for the session can trigger a state resend:
```rust
if src.id != self.config.dst_id {
    tracing::error!("Skipping RequestState from unexpected source: {:?}", src.id);
} else if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else {
    self.handle_message(...)
}
```
Additionally, address the underlying multiplexing weakness noted in the code comment by binding each relay stream/subscription to a single verified source, rather than relying on a per-message-type opt-out of the identity check.

### Proof of Concept
1. Establish (or otherwise gain the ability to inject frames into) a relay stream corresponding to an active self-serve signup session between an App client and an Orb client.
2. Send a `self_serve::app::v1::RequestState {}` payload with an arbitrary/spoofed `src` (not equal to the orb's registered `dst_id`).
3. Observe that `PollerAgent::main_loop`'s first branch matches on payload type alone and immediately re-sends `self.last_message` — bypassing the `src.id != self.config.dst_id` filter that would reject this same message if it carried a different payload type.
4. Repeat the injection during a live signup to force repeated re-emission of session-lifecycle messages (e.g., `CaptureStarted`), disrupting the legitimate app/orb state synchronization for that signup.

### Citations

**File:** orb-relay-client/src/client.rs (L388-392)
```rust
impl<'a> PollerAgent<'a> {
    // TODO: We need to split auth and subscription. Maybe ideally we issue 1 connect and then a subscribe that will notify
    // the server that we care about messages from a certain queue only. That will avoid multiplexing messages from
    // different sources.
    async fn main_loop(
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

**File:** orb-relay-client/src/lib.rs (L118-125)
```rust
impl IntoPayload for self_serve::app::v1::RequestState {
    fn into_payload(self) -> Any {
        Any::from_msg(&self_serve::app::v1::W {
            w: Some(self_serve::app::v1::w::W::RequestState(self)),
        })
        .unwrap()
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
