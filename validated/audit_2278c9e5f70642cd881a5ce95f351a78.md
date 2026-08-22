### Title
Orb locally marks user-centric signups as successful without backend confirmation of uniqueness/fraud - ([File: src/plans/mod.rs])

### Summary
In `do_signup`, when a signup is `user_centric_signup` (i.e. the mobile app, not the Orb, is responsible for submitting the signup to the backend and polling for the fraud/uniqueness verdict), the Orb skips calling `enroll_user` — the code path that actually posts to the backend (`signup_post::request`) and polls for the definitive result (`signup_poll::request`) — and instead derives success purely from **local** state (`signup_reason`, computed from the Orb's own pipeline result and local fraud-detection heuristics).

### Finding Description
`do_signup` computes `signup_reason` from local biometric-pipeline output and local fraud checks: [1](#0-0) 

When the signup is user-centric and `ignore_user_centric_signups` is false, the Orb never calls the backend-verifying `enroll_user` plan (which performs `signup_post`/`signup_poll` — the actual source of truth for whether the person is unique/not fraudulent/not a duplicate). Instead it locally decides success and records `enrollment_status`/`signup_successful` directly from `signup_reason`: [2](#0-1) 

This is only bypassed for the non-user-centric path, which does hit the backend and iterates on `signup_poll::Status` (`Success`/`Fail`/`Fraud`/`Duplicate`, etc.) as the authoritative check: [3](#0-2) 

The comment in `enroll_user.rs` even enumerates why the backend/poll result is the actual source of truth (duplicates, in-flight matches, backend-detected fraud), none of which the local `signup_reason`-only judgment in the user-centric branch can detect: [4](#0-3) 

This mirrors the report's core structural bug class: an operation is validated/approved using conditions known at one point in time/place (the Orb's local pipeline+fraud pass/fail), while the actual source of truth for validity (the backend, which performs uniqueness/duplicate/fraud checks) is consulted separately (by the app) or not consulted at all by the Orb in this code path. Any state that later diverges between the Orb's local judgement and the backend's authoritative verdict (e.g., the app fails to submit, the backend detects a duplicate/fraud match that the Orb's local heuristics missed, or the app's submission never completes) leaves the Orb reporting/recording a signup outcome (`signup_successful`, `enrollment_status = Success`, operator/UI feedback) that does not reflect what the backend — the actual source of truth — ultimately determines.

### Impact Explanation
This can lead to a misattributed signup state: the Orb marks and reports (`debug_report.signup_successful()`, UI "signup complete", metrics `main.count.signup.result.success.successful_signup`) a signup as fully valid/enrolled based solely on local pipeline health, while the backend — which is the sole authority for cross-signup uniqueness and fraud verdicts — may never confirm, or may reject, that same signup (duplicate, fraud, in-flight match). Conversely a local `signup_reason::Fraud`/`Failure` judgment marks the debug report as failed even when the app might still complete a valid backend enrollment. Either direction is a divergence between the recorded/reported signup outcome and the backend source of truth, i.e. exactly the "off-chain validation vs. on-chain source of truth" mismatch flagged in the source report, applied to signup attribution/fraud state instead of token minting.

### Likelihood Explanation
Medium: this executes on every user-centric signup (`self_serve` config combined with `orb_relay_app_id` present) that isn't overridden by `ignore_user_centric_signups`, and requires no attacker action — it is a structural gap that triggers whenever the app's own backend submission outcome differs from the Orb's local pipeline/fraud determination (e.g., transient app-side failure, backend-side duplicate/fraud detection not mirrored by Orb-local fraud checks, or timing skew between local pipeline judgment and app-side submission).

### Recommendation
Do not treat local `signup_reason` as sufficient to record signup success/failure for user-centric signups. Either have the Orb also poll a backend-confirmed status for user-centric signups before finalizing `enrollment_status`, or make `debug_report.enrollment_status`/`signup_successful` conditional on an explicit backend acknowledgment (via `orb_relay`/`self_serve::orb::v1::SignupEnded` correlated with actual backend confirmation) rather than solely on the Orb's local pipeline/fraud verdict.

### Proof of Concept
1. Configure the Orb for `self_serve` with a `user_centric_signup` QR/user-data payload (`orb_relay_app_id` present) and `ignore_user_centric_signups = false`. [5](#0-4) 
2. Run a signup where the biometric pipeline succeeds and the Orb's own local fraud checks pass (`signup_reason == SignupReason::Normal`), but the app's actual backend submission/poll (which is the only path that consults backend-side uniqueness/fraud/duplicate detection) is never completed or is rejected by the backend for reasons the Orb's local heuristics cannot see.
3. Observe that `do_signup` still sets `enrollment_status = enroll_user::Status::Success` and increments `main.count.signup.result.success.successful_signup`/calls `debug_report.signup_successful()`, purely because `signup_reason == SignupReason::Normal`, without any backend confirmation: [2](#0-1) 
4. Compare to the non-user-centric path in `enroll_user::Plan::run`, which requires an explicit backend `signup_poll::Status::Completed`/`success: true` response before declaring `Status::Success`, and treats duplicates/fraud/in-flight matches as failure: [3](#0-2)

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

**File:** src/plans/mod.rs (L639-663)
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

        Self::report_signup_reason(success, signup_reason, debug_report);

        result.success =
            debug_report.enrollment_status.as_ref().map_or(false, enroll_user::Status::is_success);
        Ok(result)
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
