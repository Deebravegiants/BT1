### Title
Unverified Local Success Determination for User-Centric Signups Bypasses Backend Uniqueness/Fraud Attestation - (File: src/plans/mod.rs)

### Summary
In the `MasterPlan::do_signup` flow, when a QR-derived `user_centric_signup` flag is set (and the Orb config does not force `ignore_user_centric_signups`), the Orb never performs the authoritative backend enrollment round-trip (`enroll_user` → `signup_post::request` + `signup_poll::request`). Instead it locally derives `enroll_user::Status::Success` purely from the on-device pipeline outcome (`signup_reason == SignupReason::Normal`). This mirrors the managed-veAERO bug class: a "receipt" (here, a signup-success attestation trusted by downstream consumers such as the self-serve app, `orb_relay` messaging, and analytics/enrollment records) is issued without ever confirming the true backing state (the backend's uniqueness/duplicate/fraud verdict), because the value that should back the receipt (server-side confirmation) is skipped.

### Finding Description
In the normal (non-user-centric) path, `enroll_user()` calls `enroll_user::Plan::run`, which POSTs the biometric result via `signup_post::request` and then polls `signup_poll::request` in a loop until the backend returns a definitive `Completed` status, which explicitly accounts for "Backend duplicates," "Backend inflight matches," and "Backend detected fraud" before returning `Status::Success` or `Status::SignupVerificationNotSuccessful`. [1](#0-0) 

However, for `user_centric_signup` sessions, this entire backend confirmation step is bypassed: [2](#0-1) 

The `success` value here is decided solely from `signup_reason`, which is itself computed purely from local pipeline output and local fraud detection: [3](#0-2) 

Critically, the local fraud-check function is a stub — all fraud checks have been removed: [4](#0-3) 

The `user_centric_signup` flag itself originates from `authenticated_app_data` returned alongside the user QR-code validation response, decoded from `orb_qr_link::UserData`: [5](#0-4) 

The net effect: a signup can be locally marked `Success`/`Normal` — and thus reported as `signup_successful()` and propagated through `orb_relay`/self-serve messaging and enrollment status — without ever consulting the backend's uniqueness or duplicate/fraud database, which is the actual "asset" the receipt is supposed to represent. Just as the veAERO exploit let an attacker detach a receipt from its backing collateral after issuance, this flow lets a signup's success "receipt" be issued detached from its backing verification (backend uniqueness/fraud confirmation).

### Impact Explanation
Any downstream party or system trusting the Orb-reported signup success for a `user_centric_signup` session (self-serve app, orb-relay peers, telemetry, or enrollment bookkeeping) receives an attestation of a "verified, unique, non-fraudulent" signup that was never actually confirmed by the backend's server-side uniqueness/fraud engine — the local `signup_reason` check only reflects pipeline execution success, not identity uniqueness. This can result in misattributed or duplicate signups being recorded/acted upon as legitimate, which is directly analogous to the "worthless receipt" impact in the report (a claim of validity disconnected from the actual backing verification), and falls within the disclosed impact classes of unauthorized/misattributed signup and cross-signup state bleed.

### Likelihood Explanation
The bypass is not a hypothetical edge case — it is a standard, config-gated code path (`user_centric_signup && !ignore_user_centric_signups`) that is exercised whenever the backend flags a session as app-centric, which is an intended supported mode of operation, not a rare failure state. Combined with the fact that all local fraud checks are deleted (`detect_fraud` is a no-op), the local "success" signal is weak and easily satisfied by any completed capture/pipeline run.

### Recommendation
For `user_centric_signup` sessions, still perform (or require confirmation of) the backend-side uniqueness/duplicate/fraud verdict before marking `enroll_user::Status::Success`, rather than deriving success purely from local pipeline state. At minimum, restore/verify that the backend's async signup verdict (equivalent to `signup_poll`) is consulted, or require server-issued signed success attestations before the Orb reports/propagates a successful signup for user-centric flows.

### Proof of Concept
Not applicable / not independently verifiable from static analysis alone — this is a logic-flow finding illustrating that [6](#0-5)  allows local success determination without invoking the backend confirmation path used elsewhere [1](#0-0) .

### Citations

**File:** src/plans/enroll_user.rs (L134-176)
```rust
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
