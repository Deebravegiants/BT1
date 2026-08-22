### Title
Backend-side duplicate/fraud verification is bypassed for "user-centric" signups, allowing local-only self-attested success - (File: `src/plans/mod.rs`)

### Summary
`do_signup` in the master signup plan branches into two mutually exclusive completion paths: a formal path that calls `enroll_user`, which contacts the backend via `signup_post`/`signup_poll` and only succeeds once the backend confirms the signup (checking for duplicates, inflight matches, and fraud), and a "user-centric signup" path that skips this backend round-trip entirely and derives success purely from the orb's own local `signup_reason` value. This mirrors the reported bug class: a formal path enforces backend-side checks (analogous to distribution fees), while an alternate path bypasses them entirely and still produces the same "successful signup" outcome.

### Finding Description
In `do_signup`, after biometric capture/pipeline/fraud-detection and PCP upload, the code decides how to finalize a signup: [1](#0-0) 

When `user_centric_signup` is `true` (a flag delivered from the backend inside the signed user QR data) and the orb config `ignore_user_centric_signups` is `false` (the default), the orb never invokes `enroll_user`, i.e. it never calls the backend `signup_post`/`signup_poll` flow. Instead `success` is computed as `signup_reason == SignupReason::Normal`, a value derived entirely from local capture/pipeline/fraud-detection results. [2](#0-1) 

The formal path (`enroll_user`) is the only path that talks to the backend to determine success, and its own comments document that a backend-reported failure specifically covers backend-side duplicate detection, inflight matches, and backend-detected fraud — checks that only happen when this code path is exercised: [3](#0-2) 

Because the "user-centric" branch short-circuits before ever calling `enroll_user::Plan::run`, none of these backend-side dedup/fraud checks are performed for that signup. Locally, `detect_fraud` currently is a stub that always returns `false` in this build (`// FOSS: WE HAVE DELETED ALL FRAUD CHECKS`), so the branch's "success" determination in practice reduces to whether the pipeline itself produced a result at all: [4](#0-3) 

The `user_centric_signup` flag itself is sourced from backend-signed user QR data and verified via `user_data.verify(user_data_hash)` in the normal (non-test) build, so this is a real production code path, not a test-only or feature-gated path. [5](#0-4) [6](#0-5) 

### Impact Explanation
Just as the Party contract's rage-quit path lets a user obtain the economic outcome of a distribution while skipping the fee enforcement that only the formal distribution path performs, the "user-centric signup" branch lets a signup reach the same terminal "success" state as a formal signup while skipping the backend enrollment call that is the sole enforcement point for duplicate-identity and backend-side fraud detection. This is a control bypass on the signup finalization path: any conditions under which the backend intended to reject/flag a signup via `signup_post`/`signup_poll` (duplicate iris, inflight match, backend fraud signal) are never evaluated for user-centric signups, creating a path for misattributed/duplicate signup completion that the operator-facing formal path would have caught.

### Likelihood Explanation
`ignore_user_centric_signups` defaults to `false`, and `user_centric_signup` is a backend-controlled, signature-verified flag intended to be set for legitimate app-centric flows — so this branch is expected to be reached in normal production self-serve/app-centric operation, not merely in a rare or misconfigured state. The bypass is therefore reachable during ordinary orb operation whenever the backend marks a signup as user-centric.

### Recommendation
Do not treat "user-centric signup" as a reason to skip backend verification of the signup outcome. Either (a) still invoke the backend `signup_post`/`signup_poll` verification (or an equivalent lightweight backend confirmation call) before reporting success for user-centric signups, or (b) require the backend to independently confirm duplicate/fraud status out-of-band before the orb is allowed to self-report success for this branch. At minimum, the local-only success determination should not be able to fully substitute for backend-side duplicate/fraud detection.

### Proof of Concept
1. Backend returns user QR status data with `user_centric_signup: true` (a legitimate, signed flag for app-centric flows) and default orb config `ignore_user_centric_signups: false`.
2. Orb completes biometric capture and local pipeline; `detect_fraud` returns `false` (fraud checks stubbed out) so `signup_reason == SignupReason::Normal`.
3. In `do_signup`, execution takes the `user_centric_signup` branch and sets `success = true` without ever calling `enroll_user`, meaning `signup_post`/`signup_poll` (and therefore backend duplicate/fraud detection) is never executed for this signup, yet the signup is finalized as successful — see `src/plans/mod.rs` lines 639-656.

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

**File:** src/config.rs (L436-436)
```rust
            ignore_user_centric_signups: false,
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

**File:** src/backend/user_status.rs (L166-179)
```rust
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
