## Finding

The reported bug class is: a state-changing method executes without an explicit precondition/authorization check that other, similar code paths do enforce. The clearest analog in `orb-core` is in the Orb-Relay client's message-handling loop, where the source-authentication check that gates all other inbound relay messages is skipped for `RequestState` messages.

### Title
Missing source-identity check before replaying last relay message on `RequestState` - (File: `orb-relay-client/src/client.rs`)

### Summary
In `PollerAgent::main_loop`, incoming relay messages are normally accepted only if `src.id == self.config.dst_id`, i.e. only from the expected counter-party (the orb or the app bound to the current session) [1](#0-0) . However, when the payload matches `self_serve::app::v1::RequestState`, the client immediately replies with `self.last_message` *before* that source check is ever evaluated [2](#0-1) .

### Finding Description
The relevant branch is:
```rust
if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: ...");
} else {
    self.handle_message(...).await?;
}
``` [3](#0-2) 

Every other inbound message type is required to originate from `self.config.dst_id` (the specific app/orb entity paired for this signup session) before it is buffered/handled. The `RequestState` branch is evaluated first and unconditionally triggers a resend of `self.last_message`, which is the last payload the orb sent to the app (e.g. `AnnounceOrbId`, `SignupEnded`, `CaptureTriggerTimeout`, `CaptureStarted`) [4](#0-3) . This mirrors the reported bug class exactly: an operation that should be gated by an explicit status/identity check can be invoked before that check is performed, because the check is only applied to the "else" branches and not to the privileged action itself.

This client is used for the self-serve signup flow, where the Orb and an untrusted end-user's phone app communicate over the relay using session identifiers derived from the QR-code flow, e.g. `orb_relay_app_id` from `backend::user_status::UserData` [5](#0-4) , and the flow explicitly relies on `wait_for_msg`/state-request semantics to synchronize the capture start [6](#0-5) .

### Impact Explanation
Because the identity check is bypassed for `RequestState`, any party able to reach the relay stream for a given session (not necessarily the legitimate bound app) can trigger a resend of the last orb→app message without being validated as the expected destination entity. Depending on relay-server-side routing guarantees, this can lead to state disclosure/replay across an unauthorized party and cross-signup state bleed if session binding is not otherwise perfectly enforced by the server, which is inconsistent with the trust model implied by the `src.id != dst_id` check applied everywhere else in the same function.

### Likelihood Explanation
This code path is reachable by any client capable of establishing a relay connection and sending a `RequestState`-shaped payload; it does not require any special privilege beyond being able to open the gRPC relay stream, which is the same low-privilege access level as a normal self-serve app user.

### Recommendation
Move the `src.id == self.config.dst_id` check ahead of the `RequestState` handling so that only the expected, bound counter-party can trigger a resend of `self.last_message`, consistent with how every other inbound message type is treated in the same loop.

### Proof of Concept
1. Establish a relay connection with an `src.id` different from the expected `dst_id` for an active session (e.g., use a manual test client such as `orb-relay-client/src/bin/manual-test.rs`'s `orb_to_app_with_state_request` pattern [7](#0-6)  but supply a mismatched entity id).
2. Send a payload matching `self_serve::app::v1::RequestState`.
3. Observe that the orb replies with `self.last_message` despite the source not matching `self.config.dst_id`, whereas any other message type from the same mismatched source is dropped and logged as "Skipping received message from unexpected source" [8](#0-7) .

### Citations

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

**File:** src/backend/user_status.rs (L47-48)
```rust
    /// The Orb Relay id which we will use to send information. New apps should always report this.
    pub orb_relay_app_id: Option<String>,
```

**File:** src/plans/mod.rs (L2068-2094)
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
