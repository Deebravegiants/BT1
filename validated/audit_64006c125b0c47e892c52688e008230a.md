### Title
Stale/superseded signup-state messages can be replayed to the app over Orb-Relay, causing cross-session state confusion - (File: `orb-relay-client/src/client.rs`)

### Summary
The `orb-relay` client used by `orb-core` to talk to a user's phone app during a self-serve signup keeps unacknowledged outgoing messages in a `pending_messages` map and unconditionally re-sends them on reconnect, and separately answers any `RequestState` request from the app by resending whatever `last_message` was last queued - with no validation that the replayed message still reflects the orb's current signup state. This mirrors the ECO Protocol bug class: a permissionless/unauthenticated-content message path with insufficient freshness checks lets an old, already-superseded state message be delivered later, desynchronizing the two sides' view of signup state.

### Finding Description
`PollerAgent` stores every outgoing message in `pending_messages: BTreeMap<u64, (RelayConnectRequest, Option<oneshot::Sender<()>>)>` when it is sent, and only removes an entry when an `Ack` for that specific `seq` arrives: [1](#0-0) [2](#0-1) 

On every reconnect (both automatic, in `main_loop`, and via the explicit `Command::Reconnect` /`Command::ReplayPendingMessages`), all entries still in `pending_messages` are resent verbatim, in insertion order, regardless of how much orb-side state has moved on since they were originally queued: [3](#0-2) [4](#0-3) 

Separately, whenever the app sends `RequestState`, the orb-side agent replies by resending `self.last_message.clone()` - the single most-recently-*sent* message - with no check that it corresponds to the app's current session, sequence, or actual live state: [5](#0-4) 

`self.last_message` is only ever updated when a new outgoing message is queued (`self.last_message = relay_message.clone().into();`), so any transient failure/reconnect cycle can leave `pending_messages` holding messages describing an earlier phase of the signup (e.g. `CaptureStarted`, `CaptureTriggerTimeout`, an earlier `AnnounceOrbId`) that have been functionally superseded by later events. During a real signup, the orb sends a strict sequence of self-serve state transitions over this channel - `AnnounceOrbId` → `CaptureStarted`/`CaptureTriggerTimeout` → `CaptureEnded` → `SignupEnded` - via `orb_relay_announce_orb_id`, `proceed_with_biometric_capture`, `after_biometric_capture`, and `after_signup`: [6](#0-5) [7](#0-6) [8](#0-7) [9](#0-8) 

None of these transitions carry a monotonic session/round identifier that the receiving app validates before accepting the payload; the app only matches on message *type* (`AnnounceOrbId::matches`, `SignupEnded::matches`, etc.), exactly as shown in the test harness: [10](#0-9) [11](#0-10) 

This is structurally the same root cause as the ECO H-2 bug: outgoing state-transition messages are queued with no anti-replay/staleness binding (there, an L1 block number; here, nothing at all tying a message to the still-current signup attempt), an unprivileged party can force reconnects/retries that keep old messages "pending" (`orb_relay_announce_orb_id`'s retry loop calls `relay.reconnect()` on any timeout, which re-triggers `replay_pending_messages`), and a later delivery of one of these stale messages is accepted by the receiver as authoritative current state.

### Impact Explanation
If a stale `SignupEnded { success: true }` (or a stale `CaptureStarted`/`CaptureEnded`) from an earlier, already-abandoned signup attempt is delivered to the app after the orb has moved to a different signup attempt or outcome, the app can show/act on a signup result that does not correspond to the actual current session - i.e. cross-session state bleed and a misattributed signup outcome (e.g., the app believes a signup succeeded when the live attempt actually failed, or vice versa, or restarts a UI flow expecting a `CaptureStarted` that already happened for a stale session). This falls squarely in the accepted "cross-signup state bleed / misattributed signup" impact category.

### Likelihood Explanation
The trigger conditions are entirely reachable by an unprivileged party sitting on the app side of the relay (a normal signup flow participant, not an operator/admin): repeated reconnects are already a designed retry path (`orb_relay_announce_orb_id`'s loop calls `relay.reconnect()` on failure/timeout), and `RequestState` can be sent by the app at any time with no rate limiting or freshness check visible in this code path. No cryptographic bypass or privileged access is required - only network/timing conditions (dropped acks, reconnects) that are realistic on a phone's cellular/WiFi connection during a signup session. Likelihood is moderate: it requires timing (an ack getting lost or a reconnect happening mid-sequence) rather than being trivially triggerable on every signup, but it is a normal operational condition, not a contrived edge case.

### Recommendation
Bind every self-serve relay message to a session/round identifier or monotonically increasing state version that both `last_message` and the retained `pending_messages` are validated against before being (re-)sent or accepted; discard/refuse delivery of any pending or "last" message whose version/session token does not match the orb's current signup attempt. On `RequestState`, respond with the actual current state (recomputed from live signup progress) rather than blindly replaying whatever was last queued, and expire/drop `pending_messages` entries once the corresponding phase of the signup has been superseded.

### Proof of Concept
Not independently verified end-to-end (no live relay backend available to reproduce timing-dependent reconnect/ack-loss conditions); the following is the reachable code path supporting the finding:
1. Orb starts self-serve signup, sends `AnnounceOrbId` via `orb_relay_announce_orb_id` (`send_blocking`); the message is stored in `pending_messages` keyed by `seq`.
2. Ack is delayed/lost (realistic over a mobile network); `orb_relay_announce_orb_id`'s loop calls `relay.reconnect()`, causing `main_loop` to restart and call `self.replay_pending_messages(&sender_tx)` at start-up [12](#0-11) , resending the old `AnnounceOrbId`/state message unconditionally.
3. Meanwhile, the orb has already progressed (e.g., signup failed and restarted, or `SignupEnded` sent) — but any earlier still-pending message (or `last_message` served in response to a subsequent `RequestState`) is delivered later, out of sync with the orb's true state, and the app has no way to detect this because matching is purely by message type [13](#0-12) .

### Citations

**File:** orb-relay-client/src/client.rs (L400-412)
```rust
        let (mut response_stream, sender_tx) = match self.connect().await {
            Ok(ok) => ok,
            Err(e) => {
                shutdown_token.cancel();
                return Err(e);
            }
        };

        if let Some(tx) = connection_established_tx {
            let _ = tx.send(());
        }

        self.replay_pending_messages(&sender_tx).await?;
```

**File:** orb-relay-client/src/client.rs (L436-440)
```rust
                            if self_serve::app::v1::RequestState::matches(&payload).is_some() {
                                sender_tx
                                    .send(self.last_message.clone())
                                    .await
                                    .wrap_err("Failed to send outgoing message")?;
```

**File:** orb-relay-client/src/client.rs (L454-464)
```rust
                        Some(Ok(RelayConnectResponse { msg: Some(relay_connect_response::Msg::Ack(ack)) })) => {
                            if let Some((_, Some(ack_tx))) = self.pending_messages.remove(&ack.seq) {
                                if ack_tx.send(()).is_err() {
                                    // The receiver has been dropped, possibly due to a timeout. That means we
                                    // need to increase the timeout at send_blocking().
                                    tracing::warn!(
                                        "Failed to send ack back to send_blocking(): receiver dropped"
                                    );
                                }
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

**File:** orb-relay-client/src/client.rs (L527-543)
```rust
    async fn replay_pending_messages(
        &mut self,
        sender_tx: &Sender<RelayConnectRequest>,
    ) -> Result<()> {
        if !self.pending_messages.is_empty() {
            tracing::warn!("Replaying pending messages: {:?}", self.pending_messages);
            for (_key, (msg, sender)) in self.pending_messages.iter_mut() {
                sender_tx.send(msg.clone()).await.wrap_err("Failed to send pending message")?;
                // If there's a sender, send a signal and set it to None. We are coming from a reconnect or a manual
                // retry, so we don't care about the acks.
                if let Some(tx) = sender.take() {
                    let _ = tx.send(());
                }
            }
        }
        Ok(())
    }
```

**File:** src/plans/mod.rs (L1117-1136)
```rust
    async fn after_biometric_capture(
        &self,
        orb: &mut Orb,
        debug_report: &mut debug_report::Builder,
        capture_succeeded: bool,
        self_serve: bool,
    ) -> Result<()> {
        if self_serve {
            tracing::info!("Self-serve: Informing backend that biometric_capture has ended");
            orb.orb_relay
                .as_mut()
                .expect("orb_relay to exist")
                .send(self_serve::orb::v1::CaptureEnded {
                    success: capture_succeeded,
                    failure_feedback: debug_report.failure_feedback_capture_proto(),
                })
                .await
                .inspect_err(|e| tracing::error!("Relay: Failed to CaptureEnded: {e}"))?;
        }
        Ok(())
```

**File:** src/plans/mod.rs (L1463-1497)
```rust
    async fn after_signup(&mut self, orb: &mut Orb, signup_result: SignupResult) -> Result<()> {
        let SignupResult { capture_start, debug_report, .. } = signup_result;
        if self.skip_pipeline() {
            // This is just to give the UI ring some time to reset.
            sleep(Duration::from_secs(5)).await;
            return Ok(());
        }
        let Some(debug_report) = debug_report else { return Ok(()) };

        tracing::info!("After-signup phase");
        dd_timing!("main.time.signup.full_signup", capture_start);

        let signup_status = debug_report.signup_status.clone();

        let enrollment_status = debug_report.enrollment_status.clone();
        let failure_feedback = debug_report.failure_feedback_after_capture_proto();
        Box::pin(self.upload_debug_report(orb, debug_report)).await?;

        if let Some(signup_status) = signup_status {
            Self::ui_complete_signup(orb, &signup_status, enrollment_status);
        }

        if orb.config.lock().await.self_serve {
            if let Some(relay) = orb.orb_relay.as_mut() {
                relay
                    .send(self_serve::orb::v1::SignupEnded {
                        success: signup_result.success,
                        failure_feedback,
                    })
                    .await
                    .inspect_err(|e| tracing::error!("Relay: Failed to SignupEnded: {e}"))?;
            }
        }

        Ok(())
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

**File:** src/plans/mod.rs (L2108-2166)
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
    for _ in 0..reties {
        let now = Instant::now();
        if let Ok(()) = relay
            .send_blocking(
                common::v1::AnnounceOrbId {
                    orb_id: ORB_ID.to_string(),
                    mode_type: if is_self_serve_enabled {
                        common::v1::announce_orb_id::ModeType::SelfServe.into()
                    } else {
                        common::v1::announce_orb_id::ModeType::Legacy.into()
                    },
                    hardware_type: if identification::HARDWARE_VERSION.contains("Diamond") {
                        common::v1::announce_orb_id::HardwareType::Diamond.into()
                    } else {
                        common::v1::announce_orb_id::HardwareType::Pearl.into()
                    },
                },
                timeout,
            )
            .await
        {
            // Happy path. We have successfully announced and acknowledged the OrbId.
            dd_timing!("main.time.orb_relay.announce_orb_id", now);
            orb.orb_relay = if is_self_serve_enabled {
                Some(relay)
            } else {
                relay.graceful_shutdown(wait_for_pending_messages, wait_for_shutdown).await;
                None
            };
            return Ok(());
        }
        dd_incr!("main.count.orb_relay.retry.send.announce_orb_id");
        tracing::error!("Relay: Failed to AnnounceOrbId. Retrying...");
        relay.reconnect().await?;
        if relay.has_pending_messages().await? > 0 {
            sleep(Duration::from_secs(1)).await;
        }
    }
    dd_incr!("main.count.orb_relay.failure.send.announce_orb_id");
    Err(eyre::eyre!("Relay: Failed to send AnnounceOrbId after a reconnect"))
```

**File:** orb-relay-client/src/bin/manual-test.rs (L223-230)
```rust
            if let Some(common::v1::AnnounceOrbId { orb_id, .. }) =
                common::v1::AnnounceOrbId::matches(msg.payload.as_ref().unwrap())
            {
                assert!(orb_id == time_now, "Received orb_id is not the same as sent orb_id");
                break 'ext;
            }
            unreachable!("Received unexpected message: {msg:?}");
        }
```

**File:** orb-relay-client/src/bin/manual-test.rs (L251-258)
```rust
            if let Some(self_serve::orb::v1::SignupEnded { success, .. }) =
                self_serve::orb::v1::SignupEnded::matches(msg.payload.as_ref().unwrap())
            {
                assert!(success, "Received: success is not true");
                break 'ext;
            }
            unreachable!("Received unexpected message: {msg:?}");
        }
```

**File:** orb-relay-client/src/lib.rs (L32-66)
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

impl PayloadMatcher for common::v1::AnnounceOrbId {
    type Output = common::v1::AnnounceOrbId;

    fn matches(payload: &Any) -> Option<Self::Output> {
        if let Some(common::v1::w::W::AnnounceOrbId(p)) = unpack_any::<common::v1::W>(payload)?.w {
            return Some(p);
        }
        unpack_any::<Self>(payload)
    }
}

impl PayloadMatcher for self_serve::orb::v1::SignupEnded {
    type Output = self_serve::orb::v1::SignupEnded;

    fn matches(payload: &Any) -> Option<Self::Output> {
        let w: self_serve::orb::v1::W = unpack_any(payload)?;
        match w.w {
            Some(self_serve::orb::v1::w::W::SignupEnded(p)) => Some(p),
            _ => None,
        }
    }
}
```
