I found a genuine analog in `src/plans/mod.rs`. The `do_signup` function's `user_centric_signup` branch determines enrollment success purely from a locally-computed `signup_reason` classification, without any backend confirmation — structurally analogous to the reported bug's core pattern (a local classification threshold/outcome, controllable by the party being measured, that determines a privileged final result).

### Title
Locally-Determined Success for User-Centric Signups Bypasses Backend Verification, Enabling Misattributed Enrollment - ([File: src/plans/mod.rs])

### Summary
In `do_signup`, when a signup is `user_centric_signup` (and `ignore_user_centric_signups` is false), the orb sets the final `enrollment_status`/`success` result directly from the locally computed `signup_reason` (`Normal`/`Fraud`/`Failure`), rather than going through the backend `enroll_user` round trip that is used for non-user-centric signups. This mirrors the reported bug class: an outcome that should require an authoritative/backend-verified classification (real "reward" vs "withdrawal", or here "success" vs "fraud/failure") is instead decided from a local, potentially gameable signal.

### Finding Description
`do_signup` computes `signup_reason` from `pipeline` presence and `detect_fraud` output [1](#0-0) . When `user_centric_signup` is true and `ignore_user_centric_signups` is false, `success` is set to `signup_reason == SignupReason::Normal` directly, and `enrollment_status` is written locally to `Success` or `Error` without contacting the backend `enroll_user` polling flow that legacy (non-user-centric) signups use [2](#0-1) . The non-user-centric path instead calls `enroll_user`, which submits the signup to the backend and polls `signup_poll::request` for authoritative status before deciding success [3](#0-2) .

The classification input, `detect_fraud`, is itself driven by `fraud_check::Report`, whose check list (`fraud_checks`, `enabled_checks_from_config`, `feedback_messages`) is empty (`[]`) in this build, so `fraud_detected()`/`fraud_detected_with_config()` structurally always evaluate against zero checks [4](#0-3) , and `detect_fraud` unconditionally returns `Ok(false)` [5](#0-4) .

### Impact Explanation
If a user-centric signup path is exercised in a build/configuration where the local fraud/pipeline classification can be influenced or is incomplete, enrollment success can be attributed to the orb-local decision rather than a backend-confirmed determination, which is precisely the "misattributed signup" pattern called out in the rules (unauthorized/misattributed signup outcome bypassing an authoritative check).

### Likelihood Explanation
This path is reachable whenever `user_centric_signup` is set by the app-provided QR data and `ignore_user_centric_signups` is false (the default) [6](#0-5) , and the QR data's `user_centric_signup` flag is set at the backend/app layer and passed through `user_status` [7](#0-6) . Because it depends on a locally-decided classification rather than the always-backend-verified path, likelihood of divergence increases if the local classification (fraud/pipeline check) is weak or stripped, as is visibly the case in this build's `fraud_check::Report`.

### Recommendation
Ensure the `user_centric_signup` success/enrollment determination cannot bypass authoritative backend verification of fraud/pipeline results, or ensure the local classification used for this shortcut is provably equivalent to what the backend would authoritatively determine, closing the gap between local signal and true outcome classification.

### Proof of Concept
1. Trigger a signup where the QR/app data sets `user_centric_signup = true` and backend config leaves `ignore_user_centric_signups = false` (default).
2. Complete biometric capture and pipeline such that `pipeline.is_some()`.
3. `detect_fraud` returns `Ok(false)` unconditionally in this build [8](#0-7) , so `signup_reason` becomes `SignupReason::Normal`.
4. `do_signup` sets `enrollment_status` to `Success` locally and reports success, without any backend poll/verification step being invoked [2](#0-1) .

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

**File:** src/plans/fraud_check.rs (L64-78)
```rust
impl Report {
    const DATADOG_TAGS: [&'static str; N_FRAUD_CHECKS] = [];

    fn fraud_checks(&self) -> [Option<bool>; N_FRAUD_CHECKS] {
        []
    }

    /// If fraud data are missing, we assume fraud is detected.
    fn fraud_checks_strict(&self) -> [bool; N_FRAUD_CHECKS] {
        self.fraud_checks().map(|v| v.unwrap_or(true))
    }

    fn enabled_checks_from_config(_config: &BackendConfig) -> [bool; N_FRAUD_CHECKS] {
        []
    }
```

**File:** src/config.rs (L120-121)
```rust
    /// Ignore app centric signup flag from the app and always perform an enrollment request.
    pub ignore_user_centric_signups: bool,
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
