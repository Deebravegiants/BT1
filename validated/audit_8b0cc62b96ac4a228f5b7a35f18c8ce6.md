### Title
`do_signup` re-reads `ignore_user_centric_signups` from the live config at the end of a signup instead of the value snapshotted at signup start, allowing a mid-signup config change to retroactively bypass backend enrollment/verification - (File: `src/plans/mod.rs`)

### Summary
`MasterPlan::do_signup` snapshots several config fields (`self_serve`, `pcp_v3`, relay timeouts, etc.) into local variables at the very start of the signup via a single destructure of `orb.config.lock().await` [1](#0-0) . However, the decision of whether to trust a "user-centric" signup result without calling the backend `enroll_user` verification path is made at the very end of the (potentially long) signup flow by re-reading `orb.config.lock().await.ignore_user_centric_signups` fresh, instead of using a value captured consistently with the rest of the signup state [2](#0-1) . Because the global `Config` is periodically overwritten in the background by the observer's `config_update` task independent of any in-flight signup [3](#0-2) , the effective decision for a given signup can be based on a configuration value that did not exist when the signup, its QR data, and its `user_centric_signup` flag were established.

### Finding Description
The relevant branch is:
```rust
let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups {
    // treat local pipeline/fraud result as final — enroll_user (backend dedup/verification) is skipped
    signup_reason == SignupReason::Normal
} else {
    // full backend enrollment/verification path
    self.enroll_user(...).await.is_success()
};
``` [2](#0-1) 

`user_centric_signup` is derived from QR data captured near the beginning of `do_signup` [4](#0-3) , well before the sound delay, biometric capture, and full biometric pipeline execution — all of which can take a substantial amount of wall-clock time [5](#0-4) . In contrast, `ignore_user_centric_signups` is fetched from the shared, mutable `Config` object at the very end of that same flow.

That shared `Config` is not stable for the duration of a signup: the `Observer` broker runs a background task on a fixed interval (`CONFIG_UPDATE_INTERVAL`) that downloads a fresh configuration from the backend and unconditionally replaces the entire `Config` object in place — `*config.lock().await = new_config;` — with no coordination with any signup currently in progress [3](#0-2) . This is structurally identical to the reported bug class: a computation that spans an interval of time (`_calculateGlobalInterest` accruing state since `lastExchangeRateUpdate`, analogous here to a signup accruing state since `start_signup`) reads a control parameter (`reserveFactorX32`, analogous here to `ignore_user_centric_signups`) *after* it may have changed, and applies the new parameter value retroactively to the entire already-elapsed interval instead of using the value that was in effect when the interval began.

The other config fields captured in the initial destructure (`self_serve`, `pcp_v3`, `orb_relay_*`) show that the code is aware config should be pinned for a signup's duration; `ignore_user_centric_signups` was simply excluded from that snapshot and is instead read fresh, creating the inconsistency.

### Impact Explanation
`ignore_user_centric_signups` is the safety switch that forces every signup through the backend `enroll_user` verification/enrollment path (dedup, signature calculation, server-side status) rather than accepting the orb-local pipeline/fraud-check outcome as final. If the backend flips this flag from `true` to `false` while a `user_centric_signup` is already in flight, the signup that began under the "always verify with backend" policy will complete under the "trust local result" policy without ever calling `enroll_user`. The signup will be marked `Success`/`Normal` purely based on `signup_reason == SignupReason::Normal` (i.e., whether the on-orb pipeline/fraud stage reported success), bypassing:
- backend-side deduplication/verification of the identity commitment,
- the biometric signature calculation and server acknowledgment normally performed by `enroll_user`.

This is a legitimate misattributed/unauthorized-signup-acceptance path: a signup can be finalized as successful while skipping the authoritative backend check that the flag was specifically designed to enforce for that class of signup, purely as a side effect of the timing of a routine background config refresh relative to the signup's lifetime.

### Likelihood Explanation
The trigger condition (a backend-pushed config change altering `ignore_user_centric_signups` while a `user_centric_signup` is already mid-flight) does not require an attacker to compromise anything on the device; it is a natural race between the periodic config-refresh task and the multi-stage `do_signup` flow (QR scan, sound delay, capture, biometric pipeline), all of which can span enough time for at least one `config_update` tick to occur. No malicious operator/peer/hardware access is required — this is purely a same-process, unprivileged-timing race inherent to normal orb operation whenever `user_centric_signup` is used together with backend-driven config changes to `ignore_user_centric_signups`.

### Recommendation
Capture `ignore_user_centric_signups` in the same up-front config snapshot used for `self_serve`, `pcp_v3`, and the other fields at the start of `do_signup`, and use that pinned value for the final enrollment-path decision instead of re-reading the live config:

```rust
let Config {
    self_serve,
    pcp_v3,
    ignore_user_centric_signups,
    orb_relay_announce_orb_id_retries,
    orb_relay_announce_orb_id_timeout,
    orb_relay_shutdown_wait_for_pending_messages,
    orb_relay_shutdown_wait_for_shutdown,
    operator_qr_expiration_time,
    ..
} = *orb.config.lock().await;
...
let success = if user_centric_signup && !ignore_user_centric_signups {
    ...
};
```
This ensures the policy in effect at signup start governs the entire signup, matching the treatment already given to the other snapshotted fields, and prevents a mid-flight config change from retroactively altering whether backend enrollment/verification is required.

### Proof of Concept
1. Backend sets `ignore_user_centric_signups = true` (forcing full backend enrollment for all signups) and the orb polls this into its local `Config`.
2. A user starts a signup where `qr_codes.user_data.user_centric_signup == true`; `do_signup` proceeds — since `ignore_user_centric_signups` is `true`, the `!orb.config.lock().await.ignore_user_centric_signups` check would currently evaluate `false`, so the code intends to route through `enroll_user`.
3. While the signup is mid-flight (during biometric capture/pipeline, which can take on the order of tens of seconds — long enough to span a `CONFIG_UPDATE_INTERVAL` tick handled in `DefaultPlan::config_update` [3](#0-2) ), the backend flips `ignore_user_centric_signups` to `false` and the observer's background task overwrites the shared `Config`.
4. When `do_signup` reaches the final decision at line 639, it re-reads the now-changed `orb.config.lock().await.ignore_user_centric_signups` (now `false`), so `user_centric_signup && !ignore_user_centric_signups` evaluates `true`.
5. The signup completes via the local-only branch (`signup_reason == SignupReason::Normal`), skipping `enroll_user`/backend verification entirely — even though the safety flag was `true` (verification required) for the entire duration the signup was actually running.

### Citations

**File:** src/plans/mod.rs (L497-506)
```rust
        let Config {
            self_serve,
            pcp_v3,
            orb_relay_announce_orb_id_retries,
            orb_relay_announce_orb_id_timeout,
            orb_relay_shutdown_wait_for_pending_messages,
            orb_relay_shutdown_wait_for_shutdown,
            operator_qr_expiration_time,
            ..
        } = *orb.config.lock().await;
```

**File:** src/plans/mod.rs (L550-562)
```rust
        // wait for the sound to finish and user to get ready before starting the capture
        sleep(Duration::from_millis(3000)).await;

        let capture = self.biometric_capture(orb, debug_report).await?;
        self.after_biometric_capture(orb, debug_report, capture.is_some(), self_serve).await?;
        let Some(capture) = capture else {
            return Ok(result);
        };
        if self.skip_pipeline() || debug_report.signup_extension_config.is_some() {
            result.success = true;
            return Ok(result);
        }
        let pipeline = Box::pin(self.biometric_pipeline(orb, debug_report, &capture)).await?;
```

**File:** src/plans/mod.rs (L572-573)
```rust
        let user_id = qr_codes.user_qr_code.user_id.clone();
        let user_centric_signup = qr_codes.user_data.user_centric_signup;
```

**File:** src/plans/mod.rs (L639-656)
```rust
        let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups
        {
            debug_report.enrollment_status(match signup_reason {
                SignupReason::Normal => enroll_user::Status::Success,
                _ => enroll_user::Status::Error,
            });
            signup_reason == SignupReason::Normal
        } else {
            Box::pin(self.enroll_user(
                orb,
                debug_report,
                &capture,
                pipeline.as_ref(),
                signup_reason,
            ))
            .await
            .is_success()
        };
```

**File:** src/brokers/observer.rs (L187-205)
```rust
    fn config_update(&mut self, observer: &mut Observer) -> Result<()> {
        if self.before_config_update()? {
            match observer.config_update.as_mut().map(future::FutureExt::now_or_never) {
                Some(None) => return Ok(()),
                Some(Some(result)) => result??,
                None => {}
            }
            let config = Arc::clone(&observer.config);
            let ui = observer.ui.clone();
            observer.config_update = Some(tokio::spawn(async move {
                if let Ok(new_config) = Config::download().await {
                    *config.lock().await = new_config;
                    config.lock().await.propagate_to_ui(ui.as_ref());
                }
                Ok(())
            }));
        }
        Ok(())
    }
```
