Based on my analysis, there is a valid analog to this bug class in the orb-core signup flow.

### Title
Re-reading mutable `ignore_user_centric_signups` config after signup start can bypass backend enrollment/uniqueness verification - (File: `src/plans/mod.rs`)

### Summary
The `MasterPlan::do_signup` function in `src/plans/mod.rs` snapshots several `Config` fields (`self_serve`, `pcp_v3`, relay retry/timeout settings, `operator_qr_expiration_time`) at the very start of the signup [1](#0-0) . However, the `ignore_user_centric_signups` flag used to decide whether to skip the full backend enrollment call is instead re-read from the shared, mutable `orb.config` mutex much later, after the (potentially lengthy) biometric capture and biometric pipeline stages have completed [2](#0-1) . This is the same root-cause pattern as the `Flip.sol` finding: a value that can be mutated externally between "game/process start" and "completion" is recalculated/re-read at completion time instead of being fixed at the start, producing an inconsistent decision.

### Finding Description
`orb.config` is a `Arc<Mutex<Config>>` that is periodically refreshed from the backend independently of any in-flight signup (see the periodic `plan.config_update(self)` call in the broker loop) [3](#0-2) . In `do_signup`, the branch that decides whether to trust the locally-derived `signup_reason` (and skip contacting the backend's `enroll_user` verification/uniqueness endpoint) is:

```rust
let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups {
    ...
    signup_reason == SignupReason::Normal
} else {
    Box::pin(self.enroll_user(...)).await.is_success()
};
``` [2](#0-1) 

`user_centric_signup` comes from the user's QR/app data captured near the beginning of the signup, while `ignore_user_centric_signups` is fetched fresh from the config mutex at this late point, well after `biometric_capture` and `biometric_pipeline` have executed [4](#0-3) , both of which can take a non-trivial amount of time. If the backend updates this config field mid-signup, the branch taken here can differ from what it would have been had the value been captured consistently with the other config fields at the top of the function.

Critically, when the "user-centric" branch is taken, `signup_reason` is trusted directly without any call to `enroll_user::Plan::run`, which is the only code path that contacts the backend's `signup_post`/`signup_poll` endpoints to check for "Backend duplicates", "Backend inflight matches", or "Backend detected fraud" [5](#0-4) . In this build, the local fraud-detection path is also a no-op (`detect_fraud` unconditionally returns `Ok(false)`, as fraud checks were stripped) [6](#0-5) , meaning `signup_reason` will be `SignupReason::Normal` for any signup that completed the pipeline, regardless of duplicate/uniqueness status.

### Impact Explanation
If the orb-level config toggles `ignore_user_centric_signups` during an in-flight signup (a normal, periodic occurrence via config refresh), a signup can be finalized as successful purely on stale, locally-derived state without ever calling the backend enrollment/uniqueness check that guards against duplicate or fraudulent signups. This constitutes a misattributed/duplicate-signup risk class: a signup could be recorded as `Success` without the backend ever validating iris uniqueness for that attempt, directly analogous to the `Flip.sol` payout mismatch caused by re-reading a mutable fee value after game start.

### Likelihood Explanation
Likelihood is low: it requires the backend-pushed config value `ignore_user_centric_signups` to change during the multi-second window between the start of `do_signup` and the enrollment decision (capture + pipeline processing), and it depends on the user/app having requested `user_centric_signup`. This mirrors the "Low likelihood" rating of the original finding, since it depends on a config change happening to land within a specific in-flight window rather than being directly and repeatably triggerable by an unprivileged actor.

### Recommendation
Capture `ignore_user_centric_signups` together with the other config fields at the top of `do_signup` (in the same destructure at line 497), and use that captured value consistently for the enrollment decision at line 639, instead of re-reading `orb.config` a second time after the lengthy capture/pipeline stages.

### Proof of Concept
1. Start a signup where the user's app requests `user_centric_signup = true`, while `ignore_user_centric_signups` is `false` in the orb's currently loaded config.
2. During biometric capture/pipeline processing (which can take seconds), the backend config poll updates and `ignore_user_centric_signups` flips (or a stale/racy read simply diverges from the value implicitly assumed at signup start).
3. At line 639, `orb.config.lock().await.ignore_user_centric_signups` is re-read; if it is still `false`, the "trust local `signup_reason`" branch is taken and `enroll_user::Plan::run` (the backend duplicate/uniqueness/fraud check) is never invoked [2](#0-1) .
4. Because `detect_fraud` always returns `false`, `signup_reason` is `SignupReason::Normal`, so `success` becomes `true` without any backend-side duplicate/fraud verification ever occurring [7](#0-6) .

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

**File:** src/plans/mod.rs (L553-573)
```rust
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
        let fraud_detected = !self.skip_fraud_checks()
            && self.detect_fraud(orb, debug_report, pipeline.as_ref()).await?;
        let signup_reason = if pipeline.is_none() {
            SignupReason::Failure
        } else if fraud_detected {
            SignupReason::Fraud
        } else {
            SignupReason::Normal
        };
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

**File:** src/plans/mod.rs (L1390-1406)
```rust
    /// Performs the fraud checks.
    #[allow(clippy::too_many_lines)]
    async fn detect_fraud(
        &mut self,
        orb: &mut Orb,
        _debug_report: &mut debug_report::Builder,
        pipeline: Option<&biometric_pipeline::Pipeline>,
    ) -> Result<bool> {
        orb.set_phase("Fraud detection").await;
        let Some(_pipeline) = pipeline else {
            return Ok(false);
        };

        // FOSS: WE HAVE DELETED ALL FRAUD CHECKS

        Ok(false)
    }
```

**File:** src/brokers/observer.rs (L475-478)
```rust
        if self.network_unblocked {
            while self.config_update_interval.next().poll_unpin(cx).is_ready() {
                plan.config_update(self)?;
            }
```

**File:** src/plans/enroll_user.rs (L162-176)
```rust
                                // This includes the following cases:
                                //   1. Backend duplicates
                                //   2. Backend legacy signup requests
                                //   3. Backend inflight matches
                                //   4. Backend detected fraud
                                //   5. Orb agent, internal, capture or pipeline failures
                                //   6. Orb detected fraud
                                tracing::info!("SIGNUP FAIL");
                                dd_incr!("main.count.http.user_enrollment.success.failed");
                                dd_incr!(
                                    "main.count.signup.result.failure.user_enrollment",
                                    "type:failure"
                                );
                                return Status::SignupVerificationNotSuccessful;
                            }
```
