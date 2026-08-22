Based on my investigation, I found a legitimate analog in orb-core to the Notional H-4 bug class: **"trust the caller/other side did the check, without re-verifying" leading to a state transition (success/completion) that skips a required verification step**.

In `src/plans/mod.rs`, the `do_signup` function determines final signup `success` via a branch on `user_centric_signup`: [1](#0-0) 

When `user_centric_signup` is `true` and `ignore_user_centric_signups` is `false`, the orb **skips the entire `enroll_user` flow** (which normally submits the signup to the backend via `signup_post::request` and polls `signup_poll::request` for backend-side confirmation, including duplicate/uniqueness detection) and instead sets `success` purely from the locally computed `signup_reason`: [2](#0-1) 

Compare this to the normal path in `enroll_user::Plan::run`, where the comment explicitly states that a `Completed`+`success:false` backend response can mean "Backend duplicates," "Backend inflight matches," or "Backend detected fraud" — i.e., the backend is the authority that clears/validates the signup for uniqueness: [3](#0-2) 

This mirrors the Notional pattern precisely: Notional's `VaultAccountAction` trusts that the vault side "already handled" secondary debt repayment and only checks primary debt before clearing state (`maturity = 0`). Here, orb-core trusts that the app/backend side ("user-centric" signup, presumably meaning the phone app already got backend confirmation) has already performed the authoritative uniqueness/fraud check, and marks local success/failure based solely on the orb's own `fraud_detected` computation — without the orb itself ever confirming with the backend via `enroll_user` that the signup was actually accepted and unique.

### Title
Signup completion trusts client-supplied `user_centric_signup` flag and bypasses backend uniqueness verification - (File: `src/plans/mod.rs`)

### Summary
`MasterPlan::do_signup` determines final enrollment success differently depending on the `user_centric_signup` flag pulled from user QR-code data. When that flag is set (and the orb config does not override it via `ignore_user_centric_signups`), the code never calls `enroll_user` (which submits to and polls the Notional-style backend for global duplicate/fraud verification) and instead derives `success` solely from the orb-local `signup_reason`, which itself only reflects local pipeline/fraud-check results.

### Finding Description
`do_signup` computes `signup_reason` from local pipeline output and local fraud detection [4](#0-3)  then branches: [1](#0-0) 

For the `user_centric_signup` branch, `debug_report.enrollment_status` is set directly from `signup_reason` and `success` becomes `signup_reason == SignupReason::Normal` — no call to the backend's `signup_post`/`signup_poll` verification (`enroll_user::Plan::run`) is made at all. That backend flow is the only place that performs server-side duplicate/uniqueness/fraud checks, as documented in the response-handling comment [3](#0-2) . `user_centric_signup` itself originates from `orb_qr_link::UserData`, delivered through `backend::user_status::request`, and is nominally verified via `user_data.verify(user_data_hash)` [5](#0-4) , but once that gate is passed, the orb permanently defers the actual signup acceptance decision to a locally-computed flag rather than any subsequent authoritative backend check for this signup attempt.

### Impact Explanation
If the local fraud/pipeline pass in this mode is bypassed or influenced (e.g., through the same kind of biometric fraud-check weaknesses that are already stubbed out in this build, `N_FRAUD_CHECKS: usize = 0` in `src/plans/fraud_check.rs`), a signup can be marked `Success`/`SignupStatus::Success` and complete the PCP upload flow without ever confirming with the backend that the identity is unique or that the signup should be accepted — i.e., a misattributed/unauthorized signup could be finalized purely on local determination, analogous to the Notional vault completing a full exit while trusting unverified secondary-debt state.

### Likelihood Explanation
This requires `user_centric_signup: true` in the signed/verified `UserData`, which is attacker-influenceable only insofar as the app/backend sets that field for a session; it's not purely an "unprivileged user" bypass without other conditions, but it does represent a designed trust boundary where the orb defers signup finalization to local-only logic in a codebase where fraud checks are currently no-ops.

### Recommendation
Even in the `user_centric_signup` path, require an explicit backend confirmation call (equivalent to `enroll_user`'s poll) before setting `enrollment_status` to `Success`, rather than deriving success purely from local `signup_reason`.

### Proof of Concept
Not directly exploitable without additional access to set `user_centric_signup=true` and control `signup_reason`; concrete PoC would require simulating a QR/session where `user_data.verify` passes with `user_centric_signup: true` and forcing `fraud_detected == false`, then observing `result.success = true` set without any `signup_post`/`signup_poll` request being issued [1](#0-0) .

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

**File:** src/backend/user_status.rs (L163-179)
```rust
    if let (Some(backend_keys), Some(user_data)) = (backend_keys, authenticated_app_data) {
        tracing::info!("User QR-data: {user_data:?}");

        #[cfg(not(feature = "skip-user-qr-validation"))]
        {
            let Some(user_data_hash) = &qr_code.user_data_hash else {
                tracing::error!(
                    "image_self_custody is provided by backend, but got no user_data_hash from \
                     QR-code"
                );
                return Ok(None);
            };
            if !user_data.verify(user_data_hash) {
                tracing::error!("user_data verification failure");
                return Ok(None);
            }
        }
```
