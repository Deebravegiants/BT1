### Title
Missing source-identity check on `RequestState` messages allows any relay peer to trigger resend of the last cached signup-state message - (File: `orb-relay-client/src/client.rs`)

### Summary
The Orb-Relay client's connection loop verifies that incoming payloads originate from the expected peer (`src.id == self.config.dst_id`) before processing them, except for one message type — `self_serve::app::v1::RequestState` — which is handled *before* that check and unconditionally triggers a resend of the client's last outgoing message to whoever is on the stream.

### Finding Description
In `PollerAgent::main_loop`, every incoming `RelayPayload` is supposed to be validated against the expected counterpart identity before being surfaced to application logic: `else if src.id != self.config.dst_id { ... skip ... } else { self.handle_message(...) }`. However, the `RequestState` branch is evaluated first and unconditionally, with no reference to `src` at all: [1](#0-0) 

```
if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: ...");
} else {
    self.handle_message(...).await?;
}
```

This is structurally identical to the reported bug class: a handler that processes attacker-influenced input (here, a `RequestState` payload arriving on the stream) without first checking that the caller/source is the authorized counterpart, while every sibling code path in the same function does perform that check. The code's own TODO comment even acknowledges the underlying trust-boundary weakness: "we need to split auth and subscription... that will avoid multiplexing messages from different sources" [2](#0-1) .

`self.last_message` is the most recent state the Orb or App sent over the relay — during self-serve signup this includes messages such as `AnnounceOrbId`, `CaptureStarted`, `CaptureTriggerTimeout`, and `SignupEnded` [3](#0-2) , which drive the app-side signup/capture UI state machine consumed in `proceed_with_biometric_capture` and other self-serve signup flows [4](#0-3) .

### Impact Explanation
Because the `RequestState` handler runs before the source-identity check, an unauthorized/unattributed peer able to have a `RequestState` payload delivered on the relay stream can force replay of the cached last-message (signup/capture state) without being validated as the legitimate session counterpart. In a self-serve signup flow this can cause cross-signup state bleed (an unintended party receiving another session's cached signup-state message) or be leveraged to repeatedly force resends as a low-effort denial-of-service against the signup state machine, mirroring the report's scenario where a caller not verified against the expected hooked/authorized entity can force processing of state-affecting calls.

### Likelihood Explanation
Exploitability depends on whether the relay transport can deliver payloads for a given stream/session with a `src` different from the expected `dst_id` (the comment in the code suggests message multiplexing across sources is an acknowledged possibility). Given the check is explicitly present for every other payload type but deliberately absent for `RequestState`, the omission looks unintentional rather than a deliberate broadcast primitive, and is reachable purely from the self-serve app-side signup flow without any special privilege.

### Recommendation
Apply the same `src.id == self.config.dst_id` verification to the `RequestState` branch as is applied to all other message branches before resending `last_message`, so that only the authenticated/expected counterpart can trigger a state resend.

### Proof of Concept
1. Establish a relay connection as the Orb (`Client::new_as_orb`) for a given `orb_id`/`session_id`, and have it hold a `last_message` such as `SignupEnded { success: true, ... }` after finishing a signup.
2. Have a second peer (not matching `self.config.dst_id`) — e.g., a stale/malicious session or manual test client resembling `orb_to_app_with_state_request` in `orb-relay-client/src/bin/manual-test.rs` [5](#0-4)  — send a `self_serve::app::v1::RequestState {}` payload that reaches the Orb's stream with `src` not equal to the expected `dst_id`.
3. Observe that `main_loop` still matches `RequestState::matches(&payload).is_some()` and immediately resends `self.last_message` via `sender_tx`, bypassing the `src.id != self.config.dst_id` guard that would otherwise reject it.

### Citations

**File:** orb-relay-client/src/client.rs (L389-391)
```rust
    // TODO: We need to split auth and subscription. Maybe ideally we issue 1 connect and then a subscribe that will notify
    // the server that we care about messages from a certain queue only. That will avoid multiplexing messages from
    // different sources.
```

**File:** orb-relay-client/src/client.rs (L425-453)
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
                        }
```

**File:** orb-relay-client/src/lib.rs (L100-116)
```rust
impl IntoPayload for self_serve::orb::v1::CaptureTriggerTimeout {
    fn into_payload(self) -> Any {
        Any::from_msg(&self_serve::orb::v1::W {
            w: Some(self_serve::orb::v1::w::W::CaptureTriggerTimeout(self)),
        })
        .unwrap()
    }
}

impl IntoPayload for self_serve::orb::v1::SignupEnded {
    fn into_payload(self) -> Any {
        Any::from_msg(&self_serve::orb::v1::W {
            w: Some(self_serve::orb::v1::w::W::SignupEnded(self)),
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

**File:** orb-relay-client/src/bin/manual-test.rs (L268-310)
```rust
async fn orb_to_app_with_state_request() -> Result<()> {
    tracing::info!("== Running Orb to App with state request ==");
    let (orb_id, session_id) = get_ids();

    let mut app_client = Client::new_as_app(
        BACKEND_URL.to_string(),
        APP_KEY.to_string(),
        session_id.to_string(),
        orb_id.to_string(),
    );
    let now = Instant::now();
    app_client.connect().await?;
    tracing::info!("Time took to app_connect: {}ms", now.elapsed().as_millis());

    let mut orb_client = Client::new_as_orb(
        BACKEND_URL.to_string(),
        ORB_KEY.to_string(),
        orb_id.to_string(),
        session_id.to_string(),
    );
    let now = Instant::now();
    orb_client.connect().await?;
    tracing::info!("Time took to orb_connect: {}ms", now.elapsed().as_millis());

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
