Based on my investigation, I found a plausible analog in the signup finalization logic of `MasterPlan::do_signup`, though the mapping is more "skip-the-authoritative-step" than a literal reordering, and I could not fully verify whether `user_centric_signup` is attacker-influenceable within the index size limits (I could not read the full `backend::user_status.rs` and `config.rs` definitions before running out of iterations).

### Title
Signup success is finalized from stale, unverified local state instead of the authoritative backend confirmation - (File: src/plans/mod.rs)

### Summary
In `do_signup`, when a signup is flagged `user_centric_signup`, the orb determines final enrollment `success` purely from a locally-computed `signup_reason` value — never invoking the backend-authoritative `enroll_user` verification (`signup_post` + `signup_poll`). This mirrors the reported bug class: a critical state value (the vault's price-per-share / here, "signup success") is finalized using an intermediate, non-authoritative computation instead of waiting for the operation that actually performs verification/fulfillment.

### Finding Description
`do_signup` computes `signup_reason` from only two local signals: whether the biometric `pipeline` produced a result, and the return of `detect_fraud`. In this build, `detect_fraud` is a no-op stub — "FOSS: WE HAVE DELETED ALL FRAUD CHECKS" — that unconditionally returns `Ok(false)`. [1](#0-0) [2](#0-1) 

When `user_centric_signup` is true (and not overridden by config), the code sets `enrollment_status` and `success` directly from this local `signup_reason`, completely bypassing the call to `enroll_user`, which is the path that contacts the backend via `signup_post::request` and polls `signup_poll::request` for the authoritative result — the only place where backend-side dedup/fraud/inflight-match detection occurs, as documented in the poll response handling comment ("Backend duplicates… Backend inflight matches… Backend detected fraud… Orb detected fraud"). [3](#0-2) [4](#0-3) 

This is the same root-cause shape as the reported bug: a downstream/authoritative step that should gate the final state transition (here, backend verification of a signup; there, share-burning/fulfillment) is skipped or its result is not awaited, and the finalization instead relies on an earlier, incomplete piece of state (locally computed `signup_reason`, with fraud checks fully stripped in this build).

### Impact Explanation
If this branch is reached, a signup can be marked `Success` (and later credentials/PCP tiers already uploaded and tied to `signup_id`/`user_id`) without ever going through backend fraud/dedup/liveness confirmation. This is a fraud/liveness-enforcement bypass and potential misattributed-signup impact, since the orb self-attests success rather than the backend confirming it.

### Likelihood Explanation
I could not confirm, within available context, whether `user_centric_signup` (sourced from `backend::user_status::UserData` via the scanned user QR code) can be influenced by an unprivileged end user, or whether it is strictly backend-issued and trustworthy per-account metadata. This materially affects likelihood, and I was unable to resolve it before running out of tool budget — this should be verified against `src/backend/user_status.rs` and `src/config.rs` (`ignore_user_centric_signups`) directly.

### Recommendation
Do not finalize `success`/`enrollment_status` from the local `signup_reason` alone for `user_centric_signup`. Route this branch through `enroll_user` (or an equivalent backend confirmation call) so the authoritative backend check (dedup/fraud/liveness) always gates a `Success` result, consistent with the non-`user_centric_signup` branch.

### Proof of Concept
Not independently reproducible from static analysis alone: exploitability depends on whether `qr_codes.user_data.user_centric_signup` can be set to `true` for a signup under attacker/user influence and whether `orb.config.lock().await.ignore_user_centric_signups` is `false` in the deployed configuration. Given `detect_fraud` is stubbed to always return `false` in this build, any signup that enters this branch with a non-`None` pipeline will be reported as `Status::Success` without backend confirmation. [3](#0-2)

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
