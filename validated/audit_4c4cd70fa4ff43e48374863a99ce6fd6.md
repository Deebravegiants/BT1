## Title
Local-only signup success determination bypasses backend duplicate/fraud verification for user-centric signups - (File: `src/plans/mod.rs`)

### Summary
In `do_signup`, when a signup is flagged `user_centric_signup` (and the orb config does not force `ignore_user_centric_signups`), the enrollment success/failure is derived **entirely from local state** (`signup_reason`) instead of actually invoking the backend enrollment flow (`enroll_user::Plan::run`) that performs server-side duplicate/uniqueness detection and persists the enrollment record. This mirrors the MasterChef pattern of recording a completed state (reward accrual / enrollment success) without ever performing the underlying verified action (token transfer / backend signup persistence and duplicate check).

### Finding Description
`do_signup` computes `signup_reason` purely from the local biometric pipeline result and a stubbed-out `detect_fraud` function that unconditionally returns `false`: [1](#0-0) 

When `user_centric_signup` is `true` for the current user QR/session, `do_signup` skips the actual backend enrollment call and instead marks `enrollment_status` as `Success`/`Error` directly from `signup_reason`, without ever posting to `signup_post`/polling `signup_poll`: [2](#0-1) 

By contrast, the non-user-centric path calls `enroll_user`, which posts the signup to the backend and polls for completion — a flow whose own comments explicitly describe it as the mechanism that filters out "Backend duplicates," "Backend legacy signup requests," "Backend inflight matches," and "Backend detected fraud": [3](#0-2) 

The `user_centric_signup` boolean itself originates from `backend::user_status`, deserialized from `authenticated_app_data` supplied via the user QR-linked backend response: [4](#0-3) 

Just as MasterChef's `updatePool()` computed and recorded reward-share state without ever verifying/transferring the underlying `depositToken`, `do_signup`'s user-centric branch records `enrollment_status(Success)` and drives `debug_report.signup_successful()` / UI success without ever verifying with the backend that this specific biometric signup is unique or has actually been durably persisted server-side (no duplicate/fraud check equivalent to the `signup_post`/`signup_poll` round-trip is performed on the orb-core side).

### Impact Explanation
Because `detect_fraud` is a stub that always returns `false` (all fraud checks removed) and the user-centric path never performs the backend `signup_post`/`signup_poll` round trip that would otherwise reject duplicate/inflight/fraudulent signups, an orb running with `user_centric_signup=true` will locally report/persist (`enrollment_status`, `debug_report.signup_successful()`, `dd_incr!("main.count.signup.result.success.successful_signup")`, `orb.ui.signup_success()`) a **successful enrollment** for any biometric capture whose local pipeline produced a result, with no cross-check against backend-side duplicate detection. This can lead to misattributed/duplicate signups being counted and surfaced as successful by the orb itself, and to loss of the uniqueness guarantee that the backend-verification path (`enroll_user`) is designed to enforce.

### Likelihood Explanation
This path is reachable whenever the backend-supplied user data sets `user_centric_signup = true` and the orb's `ignore_user_centric_signups` config is `false` (its default posture is to respect the flag) — this is a production code path, not test-only or feature-gated behind a dev-only flag: [5](#0-4) 
It requires no privileged orb access; only a completed biometric capture and a user QR/session carrying `user_centric_signup=true`.

### Recommendation
For `user_centric_signup` sessions, still require some equivalent backend confirmation (or app-relayed confirmation with server-verifiable proof) before marking `enrollment_status` as `Success` locally, so duplicate/fraud detection is not entirely bypassed on the orb side; alternatively, ensure the app-side backend confirmation (via orb-relay `SignupEnded`) is treated as authoritative and orb-core does not independently claim success without it.

### Proof of Concept
1. Configure/observe an orb session where the backend's `authenticated_app_data` for the scanned user QR sets `user_centric_signup: true` (see `src/backend/user_status.rs:203-212`) and orb config `ignore_user_centric_signups=false` (default).
2. Complete a biometric capture such that the local pipeline succeeds (`pipeline.is_some()`), which is sufficient because `detect_fraud` always returns `false` (`src/plans/mod.rs:1390-1406`).
3. `do_signup` reaches the branch at `src/plans/mod.rs:639-645`, sets `enroll_user::Status::Success` purely from `signup_reason == SignupReason::Normal`, without any call to `signup_post::request`/`signup_poll::request`.
4. `result.success` becomes `true` and `report_signup_reason` marks `debug_report.signup_successful()`, incrementing the success metric and driving `orb.ui.signup_success()` — all without the backend duplicate/fraud verification round-trip that the non-user-centric `enroll_user` path performs.

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

**File:** src/config.rs (L120-121)
```rust
    /// Ignore app centric signup flag from the app and always perform an enrollment request.
    pub ignore_user_centric_signups: bool,
```
