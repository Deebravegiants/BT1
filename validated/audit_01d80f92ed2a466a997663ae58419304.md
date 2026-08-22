### Title
Missing Sender Validation on `RequestState` Relay Messages Allows Unauthenticated Replay of Orb Signup/Session State - (File: `orb-relay-client/src/client.rs`)

### Summary
The external report describes `AssetController.receiveMessage` accepting and processing a message without verifying that the caller (`msg.sender`) is an authorized party, letting an attacker manipulate transfer state directly. The analogous flaw in `orb-core` is in the Orb-Relay client's main receive loop, `orb-relay-client/src/client.rs::PollerAgent::main_loop`, which processes an incoming relay `RequestState` payload and immediately echoes back the last sent state **without performing the source-identity check** (`src.id != self.config.dst_id`) that is applied to every other message type on the same channel.

### Finding Description
In the message-processing branch of `main_loop`, every payload received over the Orb-Relay stream is expected to be validated against the configured peer (`self.config.dst_id`) before being handled: [1](#0-0) 

The `else if src.id != self.config.dst_id` check exists specifically to reject "message[s] from unexpected source" and drop them [2](#0-1) . However, the very first branch — triggered when the payload matches `self_serve::app::v1::RequestState` — bypasses this check entirely and unconditionally resends `self.last_message` on the channel: [3](#0-2) 

This is structurally the same root cause as the reported bug: a specific message-handling branch omits the sender/identity verification that the rest of the function otherwise enforces, based purely on the payload's declared type rather than on who actually sent it (`src.id`). Just as `receiveMessage`'s multi-bridge branch skipped the check present in the single-bridge branch, this relay client's `RequestState` branch skips the check present in the normal message branch.

`self.last_message` holds the most recently sent `RelayPayload`, which for an Orb acting during a self-serve signup can contain sensitive session/state transitions such as `CaptureStarted`, `SignupEnded`, or `AgeVerificationRequiredFromOperator` [4](#0-3) , populated via `orb_relay_announce_orb_id` and the self-serve signup flow in `src/plans/mod.rs::do_signup`/`proceed_with_biometric_capture` [5](#0-4) .

### Impact Explanation
Any relay peer capable of sending a `RequestState`-typed payload on the stream — regardless of whether its `src.id` matches the paired app's `dst_id` for that signup session — can force the Orb to re-transmit its last signup-state message. Because the identity check is skipped only for this message type, this creates a path for cross-session/cross-signup state disclosure or replay within the relay trust boundary, undermining the intended per-session isolation that the `src.id != self.config.dst_id` guard is meant to enforce elsewhere in the same function.

### Likelihood Explanation
Exploitation requires only the ability to send a `RequestState` payload over an established Orb-Relay stream; no forgery of relay-level auth tokens is needed since the check being bypassed is an application-level sender check, not the relay's connection-level authentication. Any client that can reach the Orb-Relay channel and craft this specific message type can trigger the unauthenticated replay path.

### Recommendation
Apply the same `src.id != self.config.dst_id` validation to the `RequestState` branch before honoring the replay request, so that only the legitimate paired peer can trigger `last_message` retransmission:
```rust
if self_serve::app::v1::RequestState::matches(&payload).is_some() {
    if src.id != self.config.dst_id {
        tracing::error!("Skipping RequestState from unexpected source: {:?}", src.id);
    } else {
        sender_tx.send(self.last_message.clone()).await.wrap_err("Failed to send outgoing message")?;
    }
} else if src.id != self.config.dst_id {
    ...
}
```

### Proof of Concept
1. Establish a relay connection as an Orb for `session_id`/`orb_relay_app_id` X (per `orb_relay_announce_orb_id`, `src/plans/mod.rs` L2108-2166) [6](#0-5) .
2. From a separate relay identity (`src.id` different from the configured `dst_id`), send a `self_serve::app::v1::RequestState {}` payload on the same relay channel, as demonstrated in the manual test tool [7](#0-6) .
3. Observe that `main_loop` matches the payload type and immediately replays `self.last_message` back to `sender_tx` without ever evaluating `src.id != self.config.dst_id`, unlike every other payload type handled in the same loop.

### Citations

**File:** orb-relay-client/src/client.rs (L380-386)
```rust

struct PollerAgent<'a> {
    config: &'a Config,
    pending_messages: BTreeMap<u64, (RelayConnectRequest, Option<oneshot::Sender<()>>)>,
    last_message: RelayConnectRequest,
    seq: u64,
}
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

**File:** src/plans/mod.rs (L2096-2103)
```rust
    tracing::info!("Self-serve biometric-capture start triggered");
    orb.ui.signup_start();

    tracing::info!("Self-serve: Informing orb-relay that biometric_capture has started");
    orb_relay
        .send(self_serve::orb::v1::CaptureStarted {})
        .await
        .inspect_err(|e| tracing::error!("Relay: Failed to CaptureStarted: {e}"))?;
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

**File:** orb-relay-client/src/bin/manual-test.rs (L292-294)
```rust
    let now = Instant::now();
    app_client.send(self_serve::app::v1::RequestState {}).await?;
    tracing::info!("Time took to send RequestState from the app: {}ms", now.elapsed().as_millis());
```
