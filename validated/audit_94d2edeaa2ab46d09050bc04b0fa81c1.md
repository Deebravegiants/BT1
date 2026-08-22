## Title
Local-only enrollment success determination bypasses authoritative backend fraud/duplicate detection - (File: src/plans/mod.rs)

### Summary
The `do_signup` state machine has two mutually-exclusive paths for deciding whether a signup is considered "successful": the authoritative path that calls `enroll_user`, which submits the signup to the backend and polls for confirmation of uniqueness/fraud checks, and a `user_centric_signup` path that computes `success` purely from a **locally derived** `signup_reason` value, entirely skipping the call into `enroll_user`. This mirrors the reported bug class: an operation whose accounting/validation state is normally updated only through one privileged function (`claimRewards`/`enroll_user`) can instead be reached and finalized through a second path that never performs the accompanying validation/accounting step (direct `claimDelayedWithdrawals`/local `signup_reason` shortcut).

### Finding Description
In `do_signup`, after biometric capture and pipeline execution, the code computes `signup_reason` locally from `pipeline`/`fraud_detected`: [1](#0-0) 

`fraud_detected` is derived from `detect_fraud`, which in this build unconditionally returns `Ok(false)` — no fraud checks are actually performed: [2](#0-1) 

The result is then branched: when the QR/session data marks the signup as `user_centric_signup`, the code **never calls `enroll_user`** — the function that actually contacts the backend (`signup_post::request` + `signup_poll::request` polling) and only reports success when the backend confirms uniqueness and absence of fraud: [3](#0-2) 

The authoritative check that is bypassed lives in `enroll_user::Plan::run`, whose poll loop is explicitly the place where the backend reports duplicates, inflight matches, or detected fraud: [4](#0-3) 

`user_centric_signup` itself comes from `UserData` returned when validating the user's QR code/session with the backend user-status endpoint: [5](#0-4) 

The only integrity check tying this field to something signed is `user_data.verify(user_data_hash)`, gated behind the `not(skip-user-qr-validation)` feature, and applied to data that ultimately originates from the app/session associated with the same unprivileged user going through the signup: [6](#0-5) 

Because `detect_fraud` is a stub returning `false` always, and `enroll_user` (the only code path that talks to the backend's real duplicate/fraud-detection logic) is skipped whenever `user_centric_signup` is set, the entire "did this signup actually pass the backend's authoritative fraud/uniqueness accounting" question is bypassed for that class of signups — exactly analogous to how `claimRewards()`'s accounting update can be skipped by reaching the underlying effect (fund transfer / here: "enrollment marked complete") through an alternate path.

### Impact Explanation
A signup can be locally marked as `success = true` and have its Personal Custody Package uploaded and its debug report marked `enrollment_status = Success` without the backend's own fraud/duplicate detection ever running. This is a misattributed/unauthorized signup: it allows enrollment records that were supposed to be gated by backend-side fraud/duplicate checks (as documented in `enroll_user.rs` poll-loop comments) to be finalized purely on the orb's local (and in this build, disabled) fraud check, producing state that is inconsistent with what the backend would have determined authoritatively.

### Likelihood Explanation
Any signup session where the backend-provided `user_data.user_centric_signup` flag is set, and where the deployment does not set `ignore_user_centric_signups`, follows this path automatically — no operator privilege or exotic timing is required, only a standard self-serve/user-centric signup session, since fraud detection is unconditionally disabled (`detect_fraud` always returns `false`) in this build.

### Recommendation
Do not let the `user_centric_signup` branch fully bypass backend-side validation. At minimum, still invoke the authoritative enrollment/fraud-check request/poll (or an equivalent lightweight backend confirmation call) before marking `success`, so that duplicate/fraud accounting performed server-side cannot be skipped by a locally-computed `signup_reason`. Restore/implement real fraud detection instead of the current stub that always returns `false`.

### Proof of Concept
1. Complete a signup session where the backend-returned `UserData.user_centric_signup == true` (src/backend/user_status.rs:46).
2. Proceed through capture and pipeline normally; `detect_fraud` returns `false` unconditionally (src/plans/mod.rs:1399-1405), so `fraud_detected` is always `false`.
3. In `do_signup`, since `user_centric_signup` is true and `ignore_user_centric_signups` is false, the `enroll_user` call (which would otherwise poll the backend for duplicate/fraud detection, per src/plans/enroll_user.rs:157-176) is never executed; `success` is set to `signup_reason == SignupReason::Normal` directly (src/plans/mod.rs:639-656).
4. The signup is reported as successful and the PCP is already uploaded before this branch runs, all without the backend's authoritative uniqueness/fraud verdict ever being consulted.

### Citations

**File:** src/plans/mod.rs (L563-571)
```rust
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

**File:** src/backend/user_status.rs (L44-48)
```rust
    pub pcp_version: u16,
    /// Whether the orb should perform app-centric signups.
    pub user_centric_signup: bool,
    /// The Orb Relay id which we will use to send information. New apps should always report this.
    pub orb_relay_app_id: Option<String>,
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
