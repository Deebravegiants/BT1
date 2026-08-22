### Title
Local-only success determination for user-centric signups bypasses backend enrollment verification - ([File: src/plans/mod.rs])

### Summary
The reported bug class is: a function computes an *expected* result before/instead of an authoritative external check, and acts on that expectation without verifying the actual outcome from the trusted external party — risking an inconsistent/incorrect final state. The direct analog in `orb-core` is in `MasterPlan::do_signup`, where for "user-centric" signups the orb determines and records signup **success locally**, based only on its own pipeline/capture result, instead of performing the same backend round-trip (`signup_post` + `signup_poll`) used for normal signups, which is the only path that actually asks the backend whether the enrollment (including duplicate/fraud detection) was accepted.

### Finding Description
In the normal signup path, `enroll_user::Plan::run` (`src/plans/enroll_user.rs:69-287`) is the authoritative check: it posts the signup to the backend via `signup_post::request` and then polls `signup_poll::request` until the backend explicitly returns `Status::Completed` with `success: true`. Only then does orb-core consider the signup a success [1](#0-0) .

However, in `do_signup` (`src/plans/mod.rs:490-663`), when `user_centric_signup` is true and `ignore_user_centric_signups` is not set, this backend round-trip is skipped entirely. Instead, success is derived purely from the locally computed `signup_reason`: [2](#0-1) 

`signup_reason` itself is computed a few lines earlier purely from local pipeline output and a `detect_fraud` call: [3](#0-2) 

Critically, `detect_fraud` in this build always returns `Ok(false)` — the actual fraud-check logic has been removed ("FOSS: WE HAVE DELETED ALL FRAUD CHECKS"): [4](#0-3) 

So for the user-centric branch, `signup_reason` can only be `Failure` (pipeline failed) or `Normal` (pipeline succeeded) — it can never reflect backend-side duplicate detection, inflight-match detection, or fraud detection, because the code path that would surface those (`enroll_user::Plan::run` → `signup_post`/`signup_poll`, whose `SignupVerificationNotSuccessful`/`ServerError` statuses correspond to exactly "Backend duplicates… Backend inflight matches… Backend detected fraud", per the comment at lines 162-168 of `enroll_user.rs`) is never invoked for this signup type.

This mirrors the reported bug precisely: the code computes an "expected" final state (`signup_reason == Normal` → success) instead of checking the actual authoritative external result (the backend's verification), and acts on/report that unverified expectation as fact — the local success value is then used to set `debug_report.enrollment_status`, gate `Self::report_signup_reason` (`src/plans/mod.rs:665-683`), and ultimately determines what is reported to the connected app via `SignupEnded { success, .. }` (`src/plans/mod.rs:1485-1495`).

### Impact Explanation
For self-serve/user-centric signups, orb-core can locally report/record a signup as `Success` even in cases the backend would have rejected (duplicate user, inflight match with another concurrent session, or detected fraud) had the normal `enroll_user` verification path been executed. Since PCP/biometric data has already been uploaded to the backend by this point (`build_pcp`/`upload_pcp_tier_0`, lines 580-636), a locally-declared "success" without backend confirmation is a misattributed-signup / inconsistent-state condition: the Orb's UI, debug report, and the app-facing `SignupEnded` message can diverge from the backend's true acceptance state of the enrollment.

### Likelihood Explanation
This is reachable on the standard self-serve signup flow whenever `user_centric_signup` is true and `ignore_user_centric_signups` is not enabled — no special privileges are required to trigger a signup as an unprivileged user/operator pair. The bypass is deterministic (not a bug that occurs "sometimes") given the current code structure; the only remaining ambiguity is whether this branch is intentionally designed to have enrollment verified elsewhere (e.g., by the paired mobile app / relay flow) rather than by orb-core.

### Recommendation
For the user-centric signup branch, do not synthesize a local `Success`/`Error` status solely from `signup_reason`. Either:
- Still perform the backend `signup_post`/`signup_poll` verification (as in the non-user-centric branch) before reporting completion, or
- If verification is intentionally delegated to the app/backend via another channel, ensure the reported "success" clearly reflects only "pipeline succeeded locally" and is not conflated with an authoritative enrollment-success signal, and confirm that the same duplicate/inflight/fraud checks are guaranteed to occur before any UI or debug-report state marks the signup as final/successful.

### Proof of Concept
1. Configure a signup as `user_centric_signup = true` with `ignore_user_centric_signups = false` (default self-serve/app-driven flow).
2. Complete a valid biometric capture and pipeline (`do_signup`, `src/plans/mod.rs:553-562`) so `pipeline.is_some()`.
3. Since `detect_fraud` always returns `false` (`src/plans/mod.rs:1390-1406`), `signup_reason` becomes `SignupReason::Normal`.
4. Execution reaches the user-centric branch (`src/plans/mod.rs:639-645`) and sets `enrollment_status = Success` and `success = true` **without ever calling `signup_post`/`signup_poll`** — i.e., without the backend ever confirming this specific enrollment was accepted (not a duplicate, not an inflight match, not flagged as fraud by server-side logic).
5. `report_signup_reason`/`after_signup` then report this locally-derived success to the debug report and to the paired app via `SignupEnded { success: true, .. }` (`src/plans/mod.rs:1485-1495`), even though the backend's authoritative enrollment-acceptance check for this signup_id was never performed by orb-core.

### Citations

**File:** src/plans/enroll_user.rs (L146-156)
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
```

**File:** src/plans/mod.rs (L565-571)
```rust
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
