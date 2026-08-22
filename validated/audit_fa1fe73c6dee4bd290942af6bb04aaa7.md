### Title
Unprivileged-trigger local success determination bypasses backend signup verification when `user_centric_signup` is set - (File: src/plans/mod.rs)

### Summary
In `MasterPlan::do_signup()`, when the backend-supplied `user_data.user_centric_signup` flag is `true` (and `ignore_user_centric_signups` is not set in config), the orb skips the call to `enroll_user()` — the only path that actually contacts the backend (`signup_post`/`signup_poll`) to persist the signup and perform server-side duplicate/fraud detection — and instead derives `success` purely from local `signup_reason`, which itself is only ever `Fraud` if `detect_fraud()` returns true. `detect_fraud()` in this build unconditionally returns `Ok(false)` ("FOSS: WE HAVE DELETED ALL FRAUD CHECKS"). This mirrors the `_dontMint` bug class: a caller-controlled flag causes the code to take an early/alternate branch that skips the authoritative state-mutating step (crediting funds in the original; backend enrollment/duplicate-check in this codebase), while the surrounding code still marks the operation as completed/successful.

### Finding Description
`do_signup()` computes `signup_reason` from `fraud_detected`, which is produced by `detect_fraud()`: [1](#0-0) 

`detect_fraud()` always returns `false` in this build, so `fraud_detected` is always `false`, and `signup_reason` becomes `SignupReason::Normal` whenever the biometric pipeline produced a result.

Then, in the `user_centric_signup` branch, the code never calls `enroll_user()` (the function that performs the real backend round-trip via `signup_post::request`/`signup_poll::request`, which performs backend-side duplicate-signup and fraud checks, per the comments in `enroll_user.rs`): [2](#0-1) 

Instead, `success` is set directly to `signup_reason == SignupReason::Normal`, i.e., success is granted purely from the locally computed (and always-false) fraud signal, without any backend confirmation that the signup is unique, valid, or was actually persisted server-side.

The `user_centric_signup` boolean itself originates from `authenticated_app_data.user_centric_signup` returned by the `/status` endpoint and is only weakly bound to the physical QR code via a hash check (or not checked at all under `skip-user-qr-validation`): [3](#0-2) [4](#0-3) 

The `enroll_user::Plan::run()` docstring/comments explicitly enumerate what the skipped backend step is responsible for detecting — duplicates, legacy/replayed requests, in-flight matches, and backend-detected fraud: [5](#0-4) 

By skipping this call, the orb marks the local `debug_report`/`SignupResult.success` and UI state as `Success` (see `report_signup_reason` and `after_signup`) without the backend ever confirming or recording the corresponding enrollment. [6](#0-5) 

### Impact Explanation
This is a direct analog of the original bug class: a single boolean flag causes the code to bypass the mechanism that is supposed to authoritatively validate/record the operation (backend enrollment with duplicate/fraud detection), while the local code still reports the operation as completed successfully. The consequences are:
- Cross-signup state bleed / misattributed signup: the orb can locally conclude a signup is `Success` and proceed with the rest of the post-signup flow (UI success state, `SignupEnded` relay message with `success: true`, PCP tier-0/1/2 upload already happened earlier in the flow) without the backend's own uniqueness/duplicate/fraud gate ever running for that signup.
- Because `detect_fraud()` is compiled out entirely (`Ok(false)` unconditionally) in this build, the only remaining fraud/duplicate gate for `user_centric_signup` sessions was the backend round trip in `enroll_user()`, and that is exactly the step being skipped for this class of signup.

### Likelihood Explanation
`user_centric_signup` is a boolean returned from the backend's user-status response and is not itself under an attacker's control in the general case, but the branch executes for every signup where the backend sets this (increasingly the default for app-based flows), and the code path is unconditionally reachable by any user going through the ordinary QR-scan → capture → pipeline flow — no privileged/hardware access, malicious peer, or test-only feature is required to reach the branch itself. The concrete severity depends on how strictly the backend enforces this flag and whether it independently re-validates signups initiated this way, which is outside the visibility of this repo.

### Recommendation
Do not let a client/session-supplied flag (`user_centric_signup`) allow the orb to skip the authoritative backend enrollment call. At minimum, still invoke `enroll_user()` (or an equivalent backend confirmation call) before setting `success = true`, so backend-side duplicate and fraud detection is always performed regardless of `user_centric_signup`, consistent with how `ignore_user_centric_signups` already forces the safe path.

### Proof of Concept
Not independently executable from the indexed code alone (requires a live backend session where `/api/v1/user/{id}/status` or `/api/v2/session/{id}/status` returns `authenticated_app_data.user_centric_signup = true`). Structurally reachable via the standard flow:
1. Scan operator + user QR codes such that `backend::user_status::request()` returns `UserData { user_centric_signup: true, .. }` (see `src/backend/user_status.rs:203-244`, or trivially via the `skip-user-qr-validation` test feature at `src/backend/user_status.rs:100-109` where `user_centric_signup: true` is hardcoded).
2. Complete biometric capture and pipeline normally.
3. Because `detect_fraud()` unconditionally returns `false` (`src/plans/mod.rs:1399-1405`), `signup_reason` becomes `SignupReason::Normal`.
4. `do_signup()` takes the `user_centric_signup` branch (`src/plans/mod.rs:639-645`), setting `success = true` without ever calling `enroll_user()`/hitting the backend enrollment endpoint that performs duplicate/fraud checks (`src/plans/enroll_user.rs:157-176`).
5. `report_signup_reason` and `after_signup` treat the signup as fully successful and relay `SignupEnded { success: true }` to the app, even though the backend never confirmed or recorded the enrollment via `signup_post`/`signup_poll`.

### Citations

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

**File:** src/plans/mod.rs (L1392-1406)
```rust
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
