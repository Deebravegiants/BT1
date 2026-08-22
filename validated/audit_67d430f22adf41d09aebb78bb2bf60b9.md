## Title
Inconsistent signup outcome determination bypasses backend enrollment/verification for user-centric signups - ([File: src/plans/mod.rs])

### Summary
Analogous to the reported `TradingCallbacksLib::getDynamicTradePriceImpact` issue — where one code path used a stale/pre-update value while a parallel path used the correct post-update value, causing inconsistent outcomes — `do_signup()` in `src/plans/mod.rs` computes a single locally-derived `signup_reason` value and then uses it in two structurally different ways depending on `user_centric_signup`, producing inconsistent enrollment decisions between the two paths.

### Finding Description
In `do_signup`, after the biometric pipeline runs, `signup_reason` is derived purely from local, Orb-side state: [1](#0-0) 

`detect_fraud` in this build is a no-op stub that always returns `Ok(false)` (fraud checks have been deleted in this FOSS build): [2](#0-1) 

The function then branches on `user_centric_signup`: [3](#0-2) 

- In the **non-user-centric** path, `enroll_user()` is called, which invokes `enroll_user::Plan::run`, POSTs the signup to the backend (`signup_post::request`) with the codes/signature, and then polls (`signup_poll::request`) for the backend's authoritative decision (including backend-side duplicate/uniqueness detection, as suggested by the `success_unique` metric) before returning `Status::Success`/failure: [4](#0-3) 
- In the **user-centric** path, none of this backend round-trip happens. `debug_report.enrollment_status` is set directly from the locally computed `signup_reason`, and `success` is simply `signup_reason == SignupReason::Normal`: [5](#0-4) 

Because local `detect_fraud` always returns `false` in this build, `signup_reason` is `Normal` whenever the pipeline itself produced a result — i.e. the user-centric path treats the signup as successful/enrolled based solely on local computation, without ever submitting the biometric codes to the backend for the authoritative uniqueness/fraud/dedup check that the standard path relies on (`signup_post::request` → `signup_poll::request`).

This mirrors the report's root cause pattern: two code paths that are supposed to reach the same conclusion instead consume the decision value (`signup_reason`/price impact) inconsistently — one path incorporates the authoritative, "post-update" check (backend fraud/dedup, analogous to post-fee collateral), the other uses only the earlier, "pre-update" local value (analogous to pre-fee collateral).

### Impact Explanation
If a signup is processed via the `user_centric_signup` branch, the Orb reports and locally records the signup as successfully enrolled without the backend ever validating uniqueness or fraud against its authoritative store. This can result in misattributed/unauthorized signup success being reported to the operator/user and inconsistent enrollment state between the two signup flows, since one flow enforces backend-side fraud/dedup and the other does not.

### Likelihood Explanation
Likelihood depends entirely on whether `user_centric_signup` is set by the QR/user data (`qr_codes.user_data.user_centric_signup`) and whether `orb.config.lock().await.ignore_user_centric_signups` is false at runtime; this is config/QR-data-driven rather than requiring privileged access, matching the "High likelihood" pattern of the referenced report.

### Recommendation
Ensure the `user_centric_signup` path also performs (or is provably backed by) an equivalent backend-side verification/uniqueness check before deriving `success`/`enrollment_status` from `signup_reason`, rather than trusting the purely local fraud/pipeline outcome — analogous to recommending that price impact be computed only after all relevant state (fee deductions) is finalized.

### Proof of Concept
Not applicable as a runtime PoC — this is a control-flow/logic proof: with `user_centric_signup == true` and `ignore_user_centric_signups == false`, follow `do_signup` (`src/plans/mod.rs:639-656`) and observe that `enroll_user()` / `signup_post::request` / `signup_poll::request` (`src/plans/enroll_user.rs:90-156`) are never invoked, so no backend-side check occurs before `success` is set from the locally computed `signup_reason`.

**Uncertainty note:** I could not fully verify, within the available indexed context, whether the backend performs a separate out-of-band uniqueness/fraud check for user-centric signups through another mechanism (e.g., `src/backend/user_status.rs`, which also references `user_centric_signup` but whose content I was unable to inspect in this session). If such a check exists elsewhere in the flow, the severity of this analog would be reduced. Given the size limits on the codebase index, I recommend starting a full Devin session to inspect `src/backend/user_status.rs` and `src/config.rs` in full to confirm whether any backend-side validation is performed for user-centric signups before this branch executes.

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

**File:** src/plans/enroll_user.rs (L90-156)
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
```
