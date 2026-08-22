### Title
Fraud Detection Is Fully Disabled and User-Centric Signups Bypass Backend Confirmation, Enabling Unauthorized/Fraudulent Signups to Be Marked Successful - (`src/plans/mod.rs`)

### Summary
The external report describes a cross-chain lending bug where a borrow-authorization decision is made using only locally-available state (Chain B's own collateral) while ignoring the authoritative state that actually determines correctness (Bob's collateral on Chain A), causing an incorrect (in that case overly-restrictive, but structurally an "incomplete-state authorization decision") outcome. The analogous bug class in orb-core is a signup-authorization decision that is made using only local, incomplete state — a fraud check that is a stubbed no-op — while additionally short-circuiting the one code path that would otherwise consult the authoritative (backend) state, for user-centric signups.

### Finding Description
In `MasterPlan::detect_fraud`, all actual fraud-detection logic has been removed, and the function unconditionally returns `Ok(false)` (no fraud detected) whenever a pipeline exists: [1](#0-0) 

This `fraud_detected` value directly determines `signup_reason`: [2](#0-1) 

Downstream, when `qr_codes.user_data.user_centric_signup` is `true` (a flag which comes back from the backend/app QR-linking flow) and the orb is not configured to `ignore_user_centric_signups`, the orb skips the normal `enroll_user` flow entirely. That normal flow (`enroll_user::Plan::run`) is the only code path that calls `signup_post::request` / `signup_poll::request` against the backend, which is where the backend’s own authoritative checks are performed (duplicate detection, "backend inflight matches", "backend detected fraud", etc., as documented in the match arms of `enroll_user.rs`): [3](#0-2) 

Instead, for the user-centric-signup path, `do_signup` computes `success` purely from the local `signup_reason` value with no backend round-trip at all: [4](#0-3) 

Because `detect_fraud` never returns `true` (fraud checks were deleted, per the `FOSS: WE HAVE DELETED ALL FRAUD CHECKS` comment), `signup_reason` can only be `Failure` (pipeline failed) or `Normal` (pipeline succeeded) — it can never be `Fraud`. Combined with the user-centric-signup branch bypassing the backend call, a signup is marked `Success` purely on the strength of an on-device biometric pipeline producing a result, with no local fraud signal (since it's disabled) and no backend-side fraud/duplicate confirmation (since that call is skipped in this mode).

### Impact Explanation
This mirrors the reported bug class: an authorization/acceptance decision (signup success) is made from an incomplete, local-only view of state, omitting the authoritative check (backend fraud/duplicate detection) that the system's design otherwise relies on via `enroll_user`/`signup_post`/`signup_poll`. The practical impact is that fraudulent or duplicate signups that would normally be caught by backend-side fraud/duplicate checks can be accepted as successful when `user_centric_signup` is set, and that even in the non-user-centric path, the local `signup_reason` fed to the backend can never carry a `Fraud` classification because the local detector is a stub. This is a concrete fraud/liveness-enforcement bypass with a signup-authorization impact, matching the allowed impact categories (fraud/liveness bypass, unauthorized signup).

### Likelihood Explanation
`user_centric_signup` is a value the backend returns to the orb for a given user QR/session and is not gated behind any operator privilege — it is part of the normal signup flow reachable by an ordinary user completing a QR-linked signup, and the `detect_fraud` stub applies to every signup unconditionally. No special access or malicious operator/node behavior is needed; this executes on every ordinary end-user signup attempt.

### Recommendation
Restore local fraud detection in `detect_fraud` (or otherwise ensure `SignupReason::Fraud` remains reachable), and require the user-centric-signup path to still perform the backend `signup_post`/`signup_poll` round trip (or an equivalent authoritative check) before reporting the signup as successful, rather than deriving success solely from the locally computed `signup_reason`.

### Proof of Concept
1. Complete a signup where the backend-provided `UserData.user_centric_signup == true` (and `Config.ignore_user_centric_signups == false`, the default per `src/config.rs`).
2. The biometric pipeline runs and produces `Some(pipeline)`; `detect_fraud` unconditionally returns `false` since all fraud checks were removed (`src/plans/mod.rs:1390-1406`).
3. `signup_reason` is computed as `SignupReason::Normal`.
4. `do_signup` takes the `user_centric_signup` branch (`src/plans/mod.rs:639-656`), which never calls `enroll_user`/`signup_post`/`signup_poll`, so no backend duplicate/fraud confirmation ever occurs.
5. `success` is set to `true` purely because `signup_reason == SignupReason::Normal`, and the signup is reported as successful without any backend-side fraud or duplicate check ever being consulted.

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
