Based on my research, I found a valid analog in `src/plans/mod.rs`'s `do_signup` function. This mirrors the reported bug class precisely: an on-chain (here, backend) verification step is bypassed and a locally-computed decision is trusted for a critical, security-relevant outcome, exactly as `transferBribes` trusted admin-supplied `amount`/`token` without validating them against the actual on-chain `rewardIdentifier` state.

### Title
Signup success is determined locally without backend enrollment verification for user-centric signups - (File: `src/plans/mod.rs`)

### Summary
When `qr_codes.user_data.user_centric_signup` is `true` and `ignore_user_centric_signups` is not set, `do_signup` never calls `enroll_user` (which performs the authoritative `signup_post`/`signup_poll` round-trip to the backend). Instead it locally sets `enroll_user::Status::Success` purely based on the orb-computed `signup_reason`, which in turn depends on the on-orb `detect_fraud` result.

### Finding Description
In the normal enrollment path, `Plan::enroll_user` ( [1](#0-0) ) submits the signup to the backend via `signup_post::request` and then polls `signup_poll::request` until the backend reports `Completed`/`success`, which is the authoritative confirmation of signup validity (deduplication, backend fraud checks, inflight-match checks, etc.), as documented in `enroll_user::Plan::run` ( [2](#0-1) ).

However, in `do_signup`, when `user_centric_signup` is true, this entire backend verification is skipped: [3](#0-2) 

The `success` boolean (and hence `enroll_user::Status::Success`) is derived solely from `signup_reason == SignupReason::Normal`, where `signup_reason` is computed on-device from `detect_fraud` ( [4](#0-3) ). In this FOSS build, `detect_fraud` unconditionally returns `Ok(false)` (all fraud checks deleted, `N_FRAUD_CHECKS = 0`), so `signup_reason` is `Normal` for essentially any successful capture/pipeline run.

This is structurally identical to the `transferBribes` bug: a privileged/authoritative validation step (backend's duplicate/fraud/inflight checks, analogous to verifying the proposal deadline and reconciling `amount`/`token`) is bypassed, and a party's self-reported state (the orb's local `signup_reason`, analogous to the admin-supplied `amounts`/`token` arguments) is trusted directly to produce a security-relevant outcome (marking a signup as `Success`, analogous to transferring funds).

### Impact Explanation
If reached with `user_centric_signup=true`, the orb never gives the backend a chance to reject the signup as a duplicate/inflight/fraudulent match. Combined with `detect_fraud` being a no-op in this build, `enrollment_status` and `signup_successful()` get set locally without cross-checking against the backend's global state, which is exactly the class of "trust in one actor's local determination instead of on-chain/authoritative enforcement" flagged in the report. This can misattribute a signup as successful (`SignupStatus::Success`) without backend-side deduplication/fraud confirmation, which is a state-integrity issue in the signup outcome rather than a hardware/peer trust issue.

### Likelihood Explanation
Reachability depends on the `user_centric_signup` flag returned by the backend's user-status endpoint (`orb_qr_link::UserData.user_centric_signup`, see `src/backend/user_status.rs` lines 203-244) and on `ignore_user_centric_signups` being `false` (the default, per `src/config.rs` line 436: `ignore_user_centric_signups: false`). Since this flag is server/app-controlled per user QR and defaults to honoring it, this path is reachable in normal operation whenever an app signals `user_centric_signup`.

### Recommendation
Do not treat local, orb-computed `signup_reason` as sufficient for marking a signup `Success` when skipping `enroll_user`. Either always perform the backend `signup_post`/`signup_poll` round trip regardless of `user_centric_signup`, or, if that flow is intentionally different for user-centric (app-driven) signups, ensure that the backend still performs its authoritative deduplication/fraud checks (e.g., via `personal_custody_package` upload confirmation) before `debug_report.enrollment_status(enroll_user::Status::Success)` and `signup_successful()` are recorded.

### Proof of Concept
1. Backend returns `user_centric_signup: true` for a scanned user QR-code (`src/backend/user_status.rs:209`, `242`).
2. `ignore_user_centric_signups` remains at its default `false` (`src/config.rs:436`).
3. A signup proceeds through capture and pipeline; `detect_fraud` returns `false` (FOSS build always does, `src/plans/mod.rs:1390-1406`).
4. In `do_signup`, the `user_centric_signup` branch runs (`src/plans/mod.rs:639-656`), setting `enroll_user::Status::Success` and `success = true` purely from `signup_reason == SignupReason::Normal`, without ever calling `enroll_user`/`signup_post`/`signup_poll` to let the backend confirm/reject duplicates, inflight matches, or backend-side fraud.
5. `report_signup_reason` then marks the debug report `signup_successful()` (`src/plans/mod.rs:658`, `676-678`), and `result.success` is derived from this locally-set enrollment status (`src/plans/mod.rs:660-661`), without backend confirmation.

### Citations

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

**File:** src/plans/mod.rs (L1408-1435)
```rust
    async fn enroll_user(
        &mut self,
        orb: &mut Orb,
        debug_report: &mut debug_report::Builder,
        capture: &biometric_capture::Capture,
        pipeline: Option<&biometric_pipeline::Pipeline>,
        signup_reason: SignupReason,
    ) -> enroll_user::Status {
        orb.set_phase("User enrollment").await;
        let t = Instant::now();
        let status = Box::pin(
            enroll_user::Plan {
                signup_id: debug_report.signup_id.clone(),
                operator_qr_code: debug_report.operator_qr_code.clone(),
                user_qr_code: debug_report.user_qr_code.clone(),
                s3_region_str: self.s3_region_str.clone(),
                capture,
                pipeline,
                signup_reason,
            }
            .run(orb),
        )
        .await;
        dd_timing!("main.time.signup.user_enrollment", t);

        debug_report.enrollment_status(status.clone());
        status
    }
```

**File:** src/plans/enroll_user.rs (L146-176)
```rust
                        match response {
                            Ok(signup_poll::Response {
                                success: true,
                                error: None,
                                status: signup_poll::Status::Completed,
                            }) => {
                                tracing::info!("SIGNUP SUCCESS");
                                dd_incr!("main.count.http.user_enrollment.success.success_unique");
                                dd_incr!("main.count.http.user_enrollment.success.success");
                                return Status::Success;
                            }
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
