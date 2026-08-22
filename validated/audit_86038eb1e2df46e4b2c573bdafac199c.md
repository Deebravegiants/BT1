Based on my investigation, I found a plausible analog in the signup finalization logic, but I was not able to fully verify all the surrounding context (definition of `user_centric_signup` and `ignore_user_centric_signups` in `src/config.rs` / `src/backend/user_status.rs`) before running out of tool iterations. I'll present what I can support with concrete file/line evidence, and flag the parts that remain unverified.

### Title
Local-only enrollment decision bypasses backend uniqueness/fraud verification for user-centric signups - (File: src/plans/mod.rs)

### Summary
In the original report, `absorber.cairo` computes a trove's post-redistribution health using yang amounts that are not yet reflected in the trove's actual on-chain deposits (the state-updating `charge`/`melt` call happens *after* the value is used to pay out compensation), so the payout is computed against a state that hasn't been persisted yet. The analog in `orb-core` is in `MasterPlan::run` (`src/plans/mod.rs`): for signups flagged `user_centric_signup`, the enrollment `success`/`Status` is derived purely from the **already-computed, locally-derived** `signup_reason` (which itself is sourced from `detect_fraud`, a function that in this build always returns `false` — see `// FOSS: WE HAVE DELETED ALL FRAUD CHECKS`) — without ever invoking `enroll_user`, the function that performs the authoritative round-trip to the backend (`signup_post::request` + `signup_poll::request`) to check for duplicate/fraudulent signups.

### Finding Description
The relevant code path in `MasterPlan::run`: [1](#0-0) 

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

`signup_reason` is derived earlier purely from local pipeline/fraud state: [2](#0-1) 

and `detect_fraud` in this codebase is a stub that always returns `false`: [3](#0-2) 

Compare this to the non-user-centric branch, which calls `self.enroll_user`, whose underlying `enroll_user::Plan::run` performs the real backend round trip (`signup_post::request` then repeated `signup_poll::request` polling), explicitly checking for “Backend duplicates … Backend inflight matches … Backend detected fraud”: [4](#0-3) 

Crucially, by the time this success determination is made, the user's Personal Custody Package (including face/iris biometric bundles) has *already* been built and uploaded to the backend via `build_pcp` and `upload_pcp_tier_0`/tier1/tier2: [5](#0-4) 

So for the `user_centric_signup` path, the “compensation”-equivalent action (marking the enrollment a `Success`, uploading/committing biometric credential data, and surfacing `signup_success()` in the UI) is finalized using only the pre-backend-verification `signup_reason`, without the state-synchronizing step (`enroll_user`, i.e., the backend's authoritative duplicate/fraud/liveness determination) ever running — mirroring the reported root cause where a value/decision is used for an externally-visible payout/action before the corresponding canonical state update occurs.

### Impact Explanation
If `user_centric_signup` is true and `ignore_user_centric_signups` is false (a config-controlled runtime path, not verified further due to tool-iteration limits), a signup can be marked successful (and its data already uploaded) purely on the strength of local-only checks — and in this build, `detect_fraud` unconditionally returns `false`, so no fraud reason will ever be set through that path. This allows a signup to be finalized as legitimate/unique without the backend’s uniqueness/duplicate/fraud check ever executing, risking misattributed or unauthorized signups (i.e., a person being enrolled as “new”/“unique” without the backend confirming they haven't already signed up, or without server-side fraud detection being consulted).

### Likelihood Explanation
This does not require a malicious peer, hardware access, or a test-only path — it is a straight-line code path reachable whenever the `user_centric_signup` flag is set for a given signup and the orb's config does not force `ignore_user_centric_signups`. I was unable to fully confirm, within the remaining tool budget, the exact conditions under which `user_centric_signup` becomes true or how `ignore_user_centric_signups` is normally configured (both are defined across `src/config.rs`, `src/backend/config.rs`, and `src/backend/user_status.rs`, which I located but did not have iterations left to read in full).

### Recommendation
- Short term: Do not finalize `success`/`enrollment_status` for `user_centric_signup` signups without also invoking the backend verification (`enroll_user` / `signup_post` + `signup_poll`), or otherwise ensure the backend has independently confirmed uniqueness/non-fraud before treating the signup as `Success`.
- Long term: Audit all branches that bypass `enroll_user` for correctness, and add test coverage asserting that no `user_centric_signup` path can reach `SignupReason::Normal`/`Status::Success` without a corresponding backend confirmation, matching the recommendation from the source report to validate correct ordering of state updates relative to consequential actions.

### Proof of Concept
Cannot be fully constructed without confirming how `user_centric_signup` is set and how `ignore_user_centric_signups` defaults/is configured (this requires reading `src/config.rs` and `src/backend/user_status.rs` in full, which was not completed before the tool budget was exhausted). Conceptually: trigger a signup where the QR/session data marks `user_centric_signup = true`, ensure `ignore_user_centric_signups` is `false` in the active config, and complete the biometric capture/pipeline normally (fraud checks in this build are stubbed to always pass) — this reaches `SignupReason::Normal` and the code marks `enrollment_status = Success` and `success = true` at `src/plans/mod.rs:641-645` without ever calling `enroll_user`/hitting the backend duplicate/fraud check at `src/plans/enroll_user.rs:90-176`.

**Caveat on confidence**: I was able to concretely verify the code path and stub fraud-check behavior, but I was not able to verify (within the remaining tool iterations) the real-world conditions that set `user_centric_signup` to `true` or the default/production value of `ignore_user_centric_signups`, which are necessary to fully confirm exploitability. A Devin session with full repo access could inspect `src/config.rs`, `src/backend/config.rs`, and `src/backend/user_status.rs` in their entirety to close this gap.

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

**File:** src/plans/mod.rs (L580-636)
```rust
            let packages = match Box::pin(self.build_pcp(
                orb,
                credentials,
                &capture,
                pipeline.as_ref(),
                debug_report,
                signup_reason,
            ))
            .await
            {
                Ok(Some(p)) => p,
                Ok(None) => {
                    return Ok(result);
                }
                Err(e) => {
                    tracing::error!("{e}");
                    return Ok(result);
                }
            };
            data_uploader::wait_queues(orb.data_uploader.enabled().unwrap()).await?;
            if !self
                .upload_pcp_tier_0(
                    orb,
                    &result.signup_id,
                    &user_id,
                    packages.tier0,
                    packages.tier0_checksum,
                    if pcp_version >= 3 { Some(0) } else { None },
                )
                .await?
            {
                return Ok(result);
            }
            if pcp_version >= 3 {
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id: user_id.clone(),
                        data: packages.tier1,
                        checksum: packages.tier1_checksum.as_ref().to_vec(),
                        tier: 1,
                    })))
                    .await?;
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id,
                        data: packages.tier2,
                        checksum: packages.tier2_checksum.as_ref().to_vec(),
                        tier: 2,
                    })))
                    .await?;
            }
```

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

**File:** src/plans/enroll_user.rs (L90-176)
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
            match response {
                Ok(signup_post::Response {
                    software_version_status:
                        versions @ (signup_post::SoftwareVersionStatus::Allowed
                        | signup_post::SoftwareVersionStatus::Deprecated
                        | signup_post::SoftwareVersionStatus::Unknown
                        | signup_post::SoftwareVersionStatus::Empty),
                }) => {
                    if matches!(versions, signup_post::SoftwareVersionStatus::Deprecated) {
                        tracing::warn!("Orb component versions are deprecated");
                        notify_failed_signup(
                            orb,
                            Some(SignupFailReason::SoftwareVersionDeprecated),
                        );
                    }
                    if matches!(versions, signup_post::SoftwareVersionStatus::Empty)
                        || matches!(versions, signup_post::SoftwareVersionStatus::Unknown)
                    {
                        tracing::warn!("Backend doesn't know this software version.");
                        tracing::warn!(
                            "This is considered a deprecated version on staging builds, and \
                             blocked on prod."
                        );
                        #[cfg(feature = "stage")]
                        notify_failed_signup(
                            orb,
                            Some(SignupFailReason::SoftwareVersionDeprecated),
                        );
                        #[cfg(not(feature = "stage"))]
                        return Status::SoftwareVersionUnknown;
                    }
                    for i in 0..POLL_STATUS_COUNT {
                        sleep(POLL_STATUS_INTERVAL).await;
                        #[cfg(not(feature = "ui-test-successful-signup"))]
                        let response = signup_poll::request(&signup_id).await;

                        #[cfg(feature = "ui-test-successful-signup")]
                        let response: Result<signup_poll::Response> = Ok(signup_poll::Response {
                            status: signup_poll::Status::Completed,
                            success: true,
                            error: None,
                        });

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
