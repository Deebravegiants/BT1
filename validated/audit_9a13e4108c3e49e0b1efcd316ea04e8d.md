## Title
Locally-declared signup success bypasses backend dedup/fraud confirmation for user-centric signups - (File: `src/plans/mod.rs`)

### Summary
The external report describes a bug where a critical state transition (the collateral state hash reflecting a completed lien buyout) is never persisted to the authoritative record after the operation's side effects (payment transfer) have already occurred, letting the seller retain ownership despite being paid. The reachable analog in `orb-core` is in the signup completion logic in `MasterPlan::do_signup`, where for "user-centric" signups the Orb marks a signup as successfully enrolled (`enrollment_status`/`result.success`) purely from its own local, unauthenticated computation, without ever invoking the backend call that performs the authoritative duplicate/fraud verification that all other signups go through.

### Finding Description
In `MasterPlan::do_signup`, after biometric capture and pipeline processing, the code branches on `user_centric_signup`: [1](#0-0) 

If `user_centric_signup` is true (and `ignore_user_centric_signups` is not set), `enrollment_status` is set to `Success`/`Error` purely from the locally-computed `signup_reason` (`Normal`/`Fraud`/`Failure`), and `success` becomes `signup_reason == SignupReason::Normal`. Crucially, this path never calls `self.enroll_user(...)`, which is the function that in the "else" branch drives `enroll_user::Plan::run`.

That skipped function is the only place the Orb contacts the backend `signups` endpoint (`signup_post::request`) and polls for completion (`signup_poll::request`): [2](#0-1) [3](#0-2) 

The comment in the fail-path explicitly documents that this backend round-trip is what performs authoritative uniqueness/fraud checks: "Backend duplicates", "Backend legacy signup requests", "Backend inflight matches", "Backend detected fraud". By skipping `enroll_user`, the user-centric branch never asks the backend whether this iris/user has already been enrolled, whether it's a duplicate, or whether the backend's own fraud system rejects it — the Orb's local record of "signup success" is set unilaterally, just as the Lien's ownership record was left unsynced with the actual payment state.

`user_centric_signup` itself is populated straight from the backend `user_status` response tied to the user's QR code, not from any operator-privileged input: [4](#0-3) 

### Impact Explanation
Because the local `enrollment_status`/`success` state is set to `Success` without ever confirming with the backend's authoritative signup/dedup service, a user-centric signup can be recorded and propagated (UI "signup success", `dbus::Signup::signup_finished(true)`, `self_serve::orb::v1::SignupEnded { success: true, .. }`, and PCP tier upload keyed by `user_id`) even though the backend never validated it is not a duplicate enrollment or otherwise fraudulent. This is a state-bleed between the device's declared outcome and the backend's ground truth, i.e., a misattributed/unauthorized signup can be finalized and reported as legitimate without backend confirmation — mirroring the original bug's core defect: the authoritative record is left stale relative to the operation that already took real-world effect.

### Likelihood Explanation
This path is reachable by any ordinary end user going through the self-serve/user-centric signup flow — `user_centric_signup` is a normal backend-provided flag for supported app versions, not an operator or hardware-privileged setting. Additionally, in this build, `detect_fraud` is a stub that always returns `false` ("FOSS: WE HAVE DELETED ALL FRAUD CHECKS"), so `signup_reason` will be `Normal` whenever the biometric pipeline itself completes without an internal agent failure — making the "declare success without backend confirmation" branch commonly and easily reached. [5](#0-4) 

### Recommendation
For user-centric signups, the Orb should still invoke the backend's authoritative signup verification (equivalent to `signup_post`/`signup_poll`, or a dedicated user-centric confirmation endpoint) before setting `enrollment_status`/`result.success` to `Success`, so that the device's local success state is only set once the backend record has actually been created/confirmed — analogous to updating `collateralStateHash` only after the state-changing operation is verified.

### Proof of Concept
1. Perform a signup as a regular user with a QR code whose backend `user_status` response sets `user_centric_signup = true` and `ignore_user_centric_signups` disabled in Orb config.
2. Complete biometric capture such that the pipeline succeeds (`pipeline.is_some()`), and since fraud checks are stubbed to always return `false`, `signup_reason` resolves to `Normal`.
3. Observe in `src/plans/mod.rs` lines 639-645 that `debug_report.enrollment_status(enroll_user::Status::Success)` is set and `result.success` becomes `true` without any call to `signup_post`/`signup_poll` (the backend dedup/fraud verification implemented in `src/plans/enroll_user.rs`).
4. The signup is reported to the UI and via `SignupEnded { success: true }` as successful, and PCP tiers are uploaded — all without the backend ever confirming this signup is not a duplicate or otherwise fraudulent, unlike the standard (non-user-centric) path.

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

**File:** src/backend/user_status.rs (L44-49)
```rust
    pub pcp_version: u16,
    /// Whether the orb should perform app-centric signups.
    pub user_centric_signup: bool,
    /// The Orb Relay id which we will use to send information. New apps should always report this.
    pub orb_relay_app_id: Option<String>,
}
```
