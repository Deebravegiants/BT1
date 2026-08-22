### Title
Attacker-controlled `user_centric_signup` flag lets a signup bypass the backend's signup verification (dedup/fraud/liveness) step entirely - (File: `src/plans/mod.rs`)

### Summary
`do_signup()` decides whether to submit a completed signup to the backend for verification (`enroll_user`, which performs the real duplicate/fraud/liveness check) or to short-circuit and accept the signup as successful using only a local decision. This branch is gated by `user_centric_signup`, a boolean that originates from data supplied through the user's own signup-app QR flow. When this flag is `true`, the orb never calls the backend's `signup_post`/`signup_poll` endpoints and instead trusts local fraud detection alone — which in this build is a stub that always returns "no fraud." This mirrors the reported `buyLoan()` pattern: an invariant enforced on the primary path (backend signup verification) can be skipped entirely via an alternate, user-reachable path, letting the invariant (uniqueness/fraud/liveness enforcement) be bypassed.

### Finding Description
In `MasterPlan::do_signup`, after biometric capture and pipeline processing, the orb computes `signup_reason` from local `detect_fraud()` and then branches: [1](#0-0) 

If `user_centric_signup` is `true` (and `ignore_user_centric_signups` is not set), the code never calls `self.enroll_user(...)`. Instead it locally sets `enrollment_status` to `Success` whenever `signup_reason == SignupReason::Normal`, and treats that as the final `success` value: [2](#0-1) 

The path that is skipped, `enroll_user::Plan::run`, is the only place that talks to the signup backend to actually verify a signup: [3](#0-2) 

The backend's `signup_poll` response is explicitly documented to be the authority for detecting duplicate signups, in-flight matches, and backend-side fraud: [4](#0-3) 

Compounding this, the local `detect_fraud()` that gates the bypass branch is a stub in this build that unconditionally returns "no fraud detected": [5](#0-4) 

The `user_centric_signup` flag itself is sourced from data associated with the *user's own* QR code / signup-app flow (`orb_qr_link::UserData.user_centric_signup`), forwarded by the backend as `authenticated_app_data` and decoded into the orb's `UserData`: [6](#0-5) [7](#0-6) 

This is exactly the reported bug class: a validation/invariant (`maxLoanRatio` in the analog, backend duplicate/fraud/liveness verification here) that is enforced on one path (`borrow`/`enroll_user`) is silently skippable via a different, reachable code path (`buyLoan`/the `user_centric_signup` branch), letting an unprivileged actor (a borrower / a signup-app user) reach an end state that the enforced path was designed to prevent.

### Impact Explanation
An unprivileged signup-app user who can influence the `user_centric_signup` value returned in their own session's `authenticated_app_data` causes the orb to skip the backend's signup submission/poll (`signup_post`/`signup_poll`), which is the sole mechanism that detects backend duplicates, in-flight matches, and backend-side fraud. Combined with the stubbed `detect_fraud()` (always `false`), the orb will locally mark the signup `Success` without any server-side verification. This can lead to unauthorized or duplicate/misattributed enrollment — i.e., a signup being accepted (and a `debug_report.signup_successful()` / `enrollment_status(Success)` recorded, and the PCP uploaded) even though the backend never confirmed uniqueness or absence of fraud — a direct cross-signup/identity-binding integrity break.

### Likelihood Explanation
Reachability requires only a normal, unprivileged signup flow: the attacker acts as the signee via their own app/QR session and needs the backend to relay `user_centric_signup: true` for their session (this flag is documented as controlling "whether the orb should perform app-centric signups," i.e., is meant to be legitimately settable per user/app version). Whether the *backend* independently authenticates/authorizes the `user_centric_signup` value beyond the `user_data_hash` check in `verify_user_qr_code`/`user_data.verify()` could not be fully confirmed from the orb-core code alone (that check happens against backend-supplied data, and the backend's own authorization logic for this field is out of scope of this repo). Given the field is explicitly designed to route around backend enrollment, and `detect_fraud()` is a no-op in this build, the bypass is highly likely to be exploitable whenever this code path is reachable.

### Recommendation
- Do not allow `user_centric_signup` to fully bypass backend signup verification; at minimum, still call `enroll_user` (or backend `signup_post`/`signup_poll`) to check for duplicates/in-flight matches/fraud before marking `success`, even for app-centric flows.
- Restore/implement real local fraud detection in `detect_fraud()` rather than an unconditional `Ok(false)`, or explicitly document/gate this stub behind a feature flag that cannot be reached in production builds.
- Ensure `user_centric_signup` cannot be set by the user/app without cryptographic authorization from the backend that is scoped specifically to permit skipping enrollment.

### Proof of Concept
1. Complete a normal signup flow up to biometric capture as an unprivileged signup-app user.
2. Ensure the backend returns `authenticated_app_data.user_centric_signup = true` for the session (this is the field documented to enable "app-centric signups"), verified via `qr_code.user_data_hash` per `backend::user_status::request`.
3. In `do_signup`, since `detect_fraud()` (`src/plans/mod.rs:1390-1406`) always returns `Ok(false)`, `signup_reason` becomes `SignupReason::Normal` after any successful pipeline run.
4. Because `user_centric_signup == true` and `ignore_user_centric_signups` is not set, execution takes the branch at `src/plans/mod.rs:639-645`, sets `enrollment_status(Success)`, and returns `success = true` — without ever invoking `enroll_user`/`signup_post`/`signup_poll`, i.e., without the backend ever performing duplicate/fraud detection for this signup.

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

**File:** src/plans/enroll_user.rs (L90-102)
```rust
        let signup_id = self.signup_id.to_string();
        for i in 0..RETRIES_COUNT {
            let response = signup_post::request(
                signature.as_ref(),
                &signup_id,
                &self.operator_qr_code,
                &self.user_qr_code,
                &self.s3_region_str,
                self.capture,
                self.pipeline,
                self.signup_reason,
            )
            .await;
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

**File:** src/backend/user_status.rs (L42-49)
```rust
    pub data_policy: DataPolicy,
    /// Personal Custody Package version.
    pub pcp_version: u16,
    /// Whether the orb should perform app-centric signups.
    pub user_centric_signup: bool,
    /// The Orb Relay id which we will use to send information. New apps should always report this.
    pub orb_relay_app_id: Option<String>,
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
