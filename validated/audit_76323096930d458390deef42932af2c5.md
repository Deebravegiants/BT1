### Title
Signup success is reported without backend duplicate/fraud verification when `user_centric_signup` is set - (File: src/plans/mod.rs)

### Summary
When a QR-code-derived `user_centric_signup` flag is `true`, `do_signup` bypasses the call to `enroll_user`, which is the only step that performs the backend's server-side uniqueness check (duplicate detection, in-flight match detection, backend fraud detection) via the `signup_post`/`signup_poll` request cycle. Success is instead derived solely from local `signup_reason`, and local fraud detection is a no-op stub in this build.

### Finding Description
In `do_signup`, after biometric capture and pipeline processing, `fraud_detected` is computed via `detect_fraud`, and `signup_reason` is set accordingly: [1](#0-0) 

`detect_fraud` itself is a stub that unconditionally returns `Ok(false)`: [2](#0-1) 

Then, when `user_centric_signup` is true (and the orb config's `ignore_user_centric_signups` override is not set), the enrollment success is determined entirely locally, and the call to `enroll_user` — which submits the signup to the backend and polls for the real verification result — is skipped entirely: [3](#0-2) 

By contrast, the `enroll_user` path that *is* skipped is the only path that checks against real backend-side invariants, explicitly enumerated in its own comments as covering duplicates and in-flight matches: [4](#0-3) 

The `user_centric_signup` flag itself originates from `orb_qr_link::UserData`, parsed from the backend's authenticated app data tied to the user's own QR code: [5](#0-4) 

This mirrors the reported bug class: a state-committing action (signup success / position open) proceeds to be marked valid without checking, at commit time, an invariant that is required to prevent an unsafe/invalid outcome (duplicate signup / liquidatable position).

### Impact Explanation
For any signup flagged as `user_centric_signup`, the device never confirms with the backend whether the identity commitment is a duplicate, is an in-flight match, or is otherwise rejected server-side. Combined with `detect_fraud` being a no-op, `signup_reason` will always be `Normal` for a successful capture/pipeline, so `success` is unconditionally `true`. This can result in unauthorized or misattributed signups — the same person or a spoofed identity could be enrolled multiple times without the backend’s de-duplication logic ever being consulted for this signup path.

### Likelihood Explanation
The path is reachable by any unprivileged user carrying a QR code that sets `user_centric_signup: true` (a field within the app-supplied/self-custody user data), completing a normal biometric capture. No operator or hardware-privileged access is required, and no additional check gates this beyond `ignore_user_centric_signups` being unset in orb config.

### Recommendation
Do not allow local-only fraud/pipeline status to fully determine signup success for `user_centric_signup` requests. The backend uniqueness/duplicate check performed inside `enroll_user` (`signup_post`/`signup_poll`) should still be invoked (or an equivalent backend-side verification call made) before the signup is marked `Success`, regardless of the `user_centric_signup` flag.

### Proof of Concept
1. Craft/obtain a user QR code whose backend-authenticated data sets `user_centric_signup: true` (see `src/backend/user_status.rs:203-212`).
2. Complete a normal biometric capture/pipeline on the orb; ensure `detect_fraud` returns `false` (it always does in this build, per `src/plans/mod.rs:1390-1406`).
3. Observe in `do_signup` (`src/plans/mod.rs:639-656`) that `enroll_user` (and thus the backend duplicate/in-flight-match check in `src/plans/enroll_user.rs:157-176`) is never invoked, and `success` is set to `true` purely from the local `signup_reason == SignupReason::Normal` check.
4. Repeat with the same underlying identity/QR data (or a different QR presenting the same biometric) — signup is reported successful again since server-side duplicate detection was never queried for this flow.

### Citations

**File:** src/plans/mod.rs (L562-571)
```rust
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

**File:** src/plans/enroll_user.rs (L157-176)
```rust
                            Ok(signup_poll::Response {
                                success: false,
                                error: None,
                                status: signup_poll::Status::Completed,
                            }) => {
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

**File:** src/backend/user_status.rs (L203-212)
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
```
