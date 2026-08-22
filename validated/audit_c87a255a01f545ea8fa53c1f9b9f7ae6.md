### Title
Backend signup verification (`enroll_user`) is skipped for user-centric signups, allowing an unverified/misattributed signup to be marked successful - ([File: src/plans/mod.rs])

### Summary
In `MasterPlan::do_signup`, the final enrollment decision branches on `user_centric_signup`. When that flag is set (and `ignore_user_centric_signups` is `false`), the orb **never calls `enroll_user`**, the function that submits the signup to the backend (`signup_post::request`) and polls for backend confirmation (`signup_poll::request`) — the step that actually verifies duplicates, inflight matches, legacy signups, and backend-side fraud detection. Instead, success is derived purely from the locally computed `signup_reason`, mirroring the reported pattern where a critical post-action check (`afterWithdrawChecks`) is applied only inside one branch of an if-statement and is skipped in the other.

### Finding Description
The relevant branch is: [1](#0-0) 

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

`enroll_user` (else branch) is the only code path that performs backend verification: it computes the iris signature, sends the signup via `signup_post::request`, and polls `signup_poll::request` in a loop until the backend confirms `Completed`/`success: true`, explicitly guarding against "Backend duplicates," "Backend inflight matches," and "Backend detected fraud" (see comments in `enroll_user::Plan::run`): [2](#0-1) 

For the `if` branch (`user_centric_signup == true`), none of this backend round-trip happens — `signup_reason` (computed earlier, locally, from `detect_fraud`) is treated as sufficient proof of a valid, non-duplicate, non-fraudulent enrollment. Note also that `detect_fraud` itself is currently a stub that unconditionally returns `false` in this build: [3](#0-2) 

So for user-centric signups, the entire chain of server-side verification (duplicate/fraud/inflight detection normally enforced via `signup_poll`) is bypassed, and `signup_reason == SignupReason::Normal` becomes the sole criterion for declaring signup success — exactly analogous to the reported bug where the important post-action health check is applied only in one conditional branch and omitted in the other, causing an unchecked action to be treated as valid.

### Impact Explanation
Skipping `enroll_user`'s backend verification for `user_centric_signup` means the orb can locally mark a signup as `Success` (and proceed to build/enroll a Personal Custody Package and upload credentials) without the backend ever confirming the signup is not a duplicate, not fraudulent, or not already in-flight for another orb/session. This can result in an unauthorized or misattributed signup being accepted purely on local determination, undermining the fraud/duplicate detection guarantees the backend enrollment step exists to enforce.

### Likelihood Explanation
This path is reached whenever the backend marks a user QR/session as `user_centric_signup: true` (a normal, backend-controlled flag returned in `UserData`, see `src/backend/user_status.rs` line 46) and the orb's `ignore_user_centric_signups` config is not set. This is not a rare or attacker-crafted edge case — it is a standard signup flow toggle, so any signup routed through this flag reliably skips backend confirmation.

### Recommendation
Route the `user_centric_signup` branch through the same backend confirmation mechanism as the standard branch, or add an equivalent unconditional backend verification step after the if/else block (mirroring the report's recommendation to move `afterWithdrawChecks` outside the conditional) so that backend-side duplicate/fraud/inflight checks are always performed regardless of which enrollment path is taken.

### Proof of Concept
1. Backend returns `UserData { user_centric_signup: true, .. }` for a session (`src/backend/user_status.rs`).
2. Orb performs biometric capture/pipeline; `detect_fraud` returns `false` (stubbed out, `src/plans/mod.rs:1390-1406`), so `signup_reason == SignupReason::Normal`.
3. In `do_signup`, execution enters the `user_centric_signup` branch (`src/plans/mod.rs:639-645`) and sets `success = true` without ever calling `enroll_user`/`signup_post`/`signup_poll`.
4. The signup is treated as fully successful and PCP tiers are uploaded, even though the backend never confirmed the signup wasn't a duplicate or fraudulent/inflight match — the check that normally guards against this (`enroll_user::Plan::run`, `src/plans/enroll_user.rs:146-176`) never executes.

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
