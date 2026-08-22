### Title
Unauthenticated `StartCapture` relay trigger allows front-running of the self-serve biometric-capture start — (File: `src/plans/mod.rs`)

### Summary
In self-serve signup mode, the Orb gates the start of biometric capture on receiving a `StartCapture` message over the `orb-relay` channel that is keyed only by the `orb_relay_app_id` value extracted from the user's QR code. Any party that can read that same `orb_relay_app_id` (e.g. by viewing/photographing the QR code displayed on the user's phone, exactly as a mempool-watcher observes an unmined transaction) can connect to the same relay channel and send `StartCapture` ahead of the legitimate app, "front-running" the trigger that is supposed to represent explicit user consent/readiness — the same missing-authorization pattern as the reported `AlgebraPool.initialize()` front-running bug, where any party could observe and race a critical, unauthenticated state-setting call.

### Finding Description
`do_signup` binds the orb-relay session to `orb_relay_app_id`, taken from the scanned user QR-code data, and calls `orb_relay_announce_orb_id` to connect and register the Orb on that channel: [1](#0-0) 

The relay client is instantiated using only the `ORB_ID` and the `orb_relay_app_id` string as the channel identity, with no further per-message authentication of the sender: [2](#0-1) 

Once connected, `proceed_with_biometric_capture` simply waits for *any* `StartCapture` message on that channel to begin the capture, with no signature or session-ownership check on the message itself: [3](#0-2) 

The `orb_relay_app_id` itself originates from backend-verified `orb_qr_link::UserData`, but that data (and hence the `orb_relay_app_id`) is transmitted to the Orb by displaying it as a QR code on the user's phone screen, which is inherently visible to anyone with a camera pointed at it, comparable to a public mempool: [4](#0-3) 

Because the relay's message-acceptance logic checks only that the message arrived on the (orb_id, orb_relay_app_id) channel — not that it came specifically from the legitimate app instance that owns that session — any client that captures/relays the same `orb_relay_app_id` before the legitimate app does can send `StartCapture` first and win the race, exactly as the frontrunner in the original report races `initialize()` by observing calldata in the mempool before it is mined.

### Impact Explanation
A racing/eavesdropping unprivileged party can force premature start of biometric capture, bypassing the intended "wait for user to explicitly trigger" consent gate ( `self_serve_app_capture_trigger_timeout` ) and the readiness cues (`CaptureStarted`/`CaptureTriggerTimeout`). This does not by itself let an attacker read biometric data or forge a signup, but it undermines the intended UX/consent-timing guarantee and could be used to disrupt or desynchronize a legitimate self-serve signup (denial-of-service on the real user's flow), which is the same class of impact ("Medium" — not fund/identity loss, but a violated invariant/timing assumption) that the judge assigned to the original `initialize()` finding.

### Likelihood Explanation
Likelihood is Medium-Low: it requires the attacker to be physically proximate enough to see/photograph the user's QR code and race the network round-trip to the relay server before the legitimate app connects and sends `StartCapture`. It does not require any credential compromise or backend flaw — only that possession of the `orb_relay_app_id` is treated as sufficient authorization to control the capture trigger, mirroring the "unprotected against frontrunning" root cause in the original report.

### Recommendation
- Bind acceptance of `StartCapture` (and other privileged self-serve app→orb messages) to a per-session secret/nonce that is not derivable from anything displayed on-screen, or require the relay server to authenticate the app leg cryptographically rather than by channel-id alone.
- Alternatively, require the Orb to echo/challenge a value back to the app and only accept `StartCapture` messages that reference that specific challenge, closing the race window analogous to the "divide initialization into parts" mitigation recommended in the original report.

### Proof of Concept
1. Operator/user initiates a self-serve signup; the app displays a QR code encoding user data that includes `orb_relay_app_id`.
2. Before or as the Orb scans this code, a bystander with a camera captures the same QR code and extracts `orb_relay_app_id`.
3. The bystander's device connects to the relay backend as an "app" using the same `orb_relay_app_id` (same mechanism as `Client::new_as_app` in `orb-relay-client/src/bin/manual-test.rs`, lines shown at `orb-relay-client/src/bin/manual-test.rs:588-601`).
4. The bystander sends `self_serve::app::v1::StartCapture {}` immediately, before the legitimate app does.
5. The Orb's `proceed_with_biometric_capture` (`src/plans/mod.rs:2068-2106`) accepts this first-arriving message and begins biometric capture, having been "front-run" by the bystander rather than triggered by the legitimate user's explicit action.

### Citations

**File:** src/plans/mod.rs (L527-548)
```rust
        if self_serve && qr_codes.user_data.orb_relay_app_id.is_none() {
            tracing::error!("Self-serve: orb_relay_app_id is missing in the user data");
            debug_report.signup_app_incompatible_failure();
            return Ok(result);
        }
        if let Some(orb_relay_app_id) = &qr_codes.user_data.orb_relay_app_id {
            if let Err(e) = orb_relay_announce_orb_id(
                orb,
                orb_relay_app_id.clone(),
                self_serve,
                orb_relay_announce_orb_id_retries,
                orb_relay_announce_orb_id_timeout,
                orb_relay_shutdown_wait_for_pending_messages,
                orb_relay_shutdown_wait_for_shutdown,
            )
            .await
            {
                tracing::error!("{e}");
                debug_report.signup_orb_relay_failure();
                return Ok(result);
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

**File:** src/backend/user_status.rs (L203-244)
```rust
        let orb_qr_link::UserData {
            identity_commitment,
            self_custody_public_key: user_public_key,
            #[cfg(feature = "internal-data-acquisition")]
            data_policy,
            pcp_version,
            user_centric_signup,
            orb_relay_app_id,
            ..
        } = user_data;
        let backend_iris_public_key = decode_public_key(&backend_iris_public_key)
            .wrap_err("decoding backend_iris_public_key")?;
        let backend_normalized_iris_public_key =
            decode_public_key(&backend_normalized_iris_public_key)
                .wrap_err("decoding backend_normalized_iris_public_key")?;
        let backend_face_public_key = decode_public_key(&backend_face_public_key)
            .wrap_err("decoding backend_face_public_key")?;
        let backend_tier2_public_key = backend_tier2_public_key
            .map(decode_public_key)
            .transpose()
            .wrap_err("decoding backend_tier2_public_key")?;
        let user_public_key =
            decode_public_key(&user_public_key).wrap_err("decoding user_public_key")?;
        Ok(Some(UserData {
            backend_iris_public_key: Some(backend_iris_public_key),
            backend_iris_encrypted_private_key: Some(backend_iris_encrypted_private_key),
            backend_normalized_iris_public_key: Some(backend_normalized_iris_public_key),
            backend_normalized_iris_encrypted_private_key: Some(
                backend_normalized_iris_encrypted_private_key,
            ),
            backend_face_public_key: Some(backend_face_public_key),
            backend_face_encrypted_private_key: Some(backend_face_encrypted_private_key),
            backend_tier2_public_key,
            backend_tier2_encrypted_private_key,
            self_custody_user_public_key: Some(user_public_key),
            id_commitment: Some(identity_commitment),
            #[cfg(feature = "internal-data-acquisition")]
            data_policy,
            pcp_version,
            user_centric_signup,
            orb_relay_app_id,
        }))
```
