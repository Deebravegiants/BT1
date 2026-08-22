### Title
Missing sender/source verification in `PollerAgent::main_loop`'s `RequestState` handling allows cross-session state disclosure - (File: `orb-relay-client/src/client.rs`)

### Summary
The external report describes an ERC-3156 flashloan callback (`onFlashLoan()`) that fails to verify the `initiator`/`token` before trusting the callback data, and an `exchange()` function missing the trust-boundary check applied elsewhere in the contract. The `orb-relay-client` crate has the same class of bug: the message-handling loop in `PollerAgent::main_loop` normally verifies that an incoming message's `src.id` matches the expected `dst_id` before trusting/acting on it, but this verification is explicitly skipped for `RequestState` messages, which instead immediately triggers a resend of the client's last (potentially sensitive) session/signup state.

### Finding Description
In `orb-relay-client/src/client.rs`, `PollerAgent::main_loop` processes incoming relay messages: [1](#0-0) 

Specifically:
```rust
if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    sender_tx.send(self.last_message.clone()).await...
} else if src.id != self.config.dst_id {
    tracing::error!("Skipping received message from unexpected source: ...");
} else {
    self.handle_message(...).await?;
}
```

The `else if src.id != self.config.dst_id` branch is the trust-boundary check for this component — it is the code's own defense against "unexpected source" messages, analogous to what `onFlashLoan()` should be doing for `initiator`/`token`. But the `RequestState` branch is evaluated *first* and unconditionally responds with `self.last_message.clone()` regardless of whether `src.id` equals the expected `dst_id`. This means any entity able to inject a `RequestState` payload into the bidirectional relay stream — without being the verified counterparty (`dst_id`) — can trigger the client to resend its last transmitted message.

`self.last_message` is set on every outgoing send: [2](#0-1) 

and can contain signup/session-related payloads such as `AnnounceOrbId` (orb id, session id, mode/hardware type) or `SignupEnded` (success/failure feedback), as exercised in the crate's own test harness: [3](#0-2) [4](#0-3) 

The relay protocol's own `PayloadMatcher`/message model treats `src`/`dst`/`Entity` as authoritative identity fields that the rest of the code (the `else if` branch) is designed to check — but the `RequestState` fast-path was added without that same check, breaking the intended trust boundary between `Orb` and `App` entities on a session.

### Impact Explanation
This mirrors the reported flashloan bug class: a privileged/trust-sensitive code path (resending session state) is reachable via a message type whose sender identity is never validated, unlike the sibling code path that does validate it. Depending on how the relay backend scopes message delivery within a `session_id`, this allows disclosure of the last signup/session state (e.g., `AnnounceOrbId`, `SignupEnded`) to a party in the session that has not been authenticated as the expected `dst_id`, i.e., a cross-signup/session state bleed of orb-relay session data to an unverified party.

### Likelihood Explanation
The code path is unconditionally reachable on every established relay connection (both `Orb` and `App` modes) whenever a `RequestState` payload is received — no additional preconditions or race are required, since the check is structurally omitted for this branch rather than merely racy.

### Recommendation
Move the `RequestState` handling after (or apply) the same `src.id != self.config.dst_id` verification used for all other inbound relay payloads, so the state-resend fast-path is only honored for messages from the verified session counterparty.

### Proof of Concept
1. Establish a relay session as `Orb`/`App` per `orb-relay-client/src/bin/manual-test.rs` setup.
2. As a third entity capable of sending a `RelayPayload` into the same session/stream with an arbitrary `src` (i.e., anything other than the expected `dst_id`) and a `self_serve::app::v1::RequestState` payload.
3. Observe that `main_loop` matches the `RequestState` branch first (`orb-relay-client/src/client.rs:436-440`) and sends `self.last_message.clone()` back without ever reaching the `src.id != self.config.dst_id` check, disclosing the last signup/session-state message to the unverified sender.

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

**File:** orb-relay-client/src/bin/manual-test.rs (L200-238)
```rust
    let now = Instant::now();
    let time_now = time_now()?;
    tracing::info!("Sending time now: {}", time_now);
    orb_client
        .send(common::v1::AnnounceOrbId {
            orb_id: time_now.clone(),
            mode_type: common::v1::announce_orb_id::ModeType::SelfServe.into(),
            hardware_type: common::v1::announce_orb_id::HardwareType::Diamond.into(),
        })
        .await?;
    tracing::info!("Time took to send a message from the app: {}ms", now.elapsed().as_millis());

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
            if let Some(common::v1::AnnounceOrbId { orb_id, .. }) =
                common::v1::AnnounceOrbId::matches(msg.payload.as_ref().unwrap())
            {
                assert!(orb_id == time_now, "Received orb_id is not the same as sent orb_id");
                break 'ext;
            }
            unreachable!("Received unexpected message: {msg:?}");
        }
    }
    tracing::info!("Time took to receive a message: {}ms", now.elapsed().as_millis());

    let now = Instant::now();
    orb_client
        .send(self_serve::orb::v1::SignupEnded { success: true, failure_feedback: Vec::new() })
        .await?;
    tracing::info!("Time took to send a second message: {}ms", now.elapsed().as_millis());
```

**File:** orb-relay-client/src/bin/manual-test.rs (L268-322)
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

    let now = Instant::now();
    let time_now = time_now()?;
    tracing::info!("Sending time now: {}", time_now);
    orb_client
        .send(common::v1::AnnounceOrbId {
            orb_id: time_now,
            mode_type: common::v1::announce_orb_id::ModeType::SelfServe.into(),
            hardware_type: common::v1::announce_orb_id::HardwareType::Diamond.into(),
        })
        .await?;
    tracing::info!("Time took to send a message from the app: {}ms", now.elapsed().as_millis());
```
