Based on my investigation, I found a genuine analog to the reported bug class. The core issue in the Solidity report is: **trusting a locally-computed value as final/authoritative instead of waiting for/requiring the authoritative party's confirmation before committing an outcome that grants a benefit (winning the lottery / here, a successful signup).**

### Title
User-centric signup success is determined from locally-computed `signup_reason` without backend confirmation of enrollment - ([File: src/plans/mod.rs])

### Summary
When a QR-linked app reports `user_centric_signup = true`, the Orb never calls the backend enrollment/verification endpoint (`enroll_user::Plan::run`, which POSTs to `signup_post::request` and polls `signup_poll::request` for authoritative completion). Instead, it locally derives `success` purely from `signup_reason`, a value computed entirely on-device from the biometric pipeline and (FOSS-stripped) fraud checks.

### Finding Description
In `do_signup`, `signup_reason` is computed locally: `SignupReason::Failure` if pipeline is `None`, `SignupReason::Fraud` if `detect_fraud` returns true, else `SignupReason::Normal`. Then: [1](#0-0) 
When `user_centric_signup` is true (a flag that comes from `orb_qr_link::UserData`, itself sourced from the backend response but only integrity-checked via `user_data.verify(user_data_hash)`, not tied to a completed identity-commitment registration), the Orb sets the enrollment status to `Success`/`Error` purely from `signup_reason` — it never invokes `enroll_user::Plan` (which is the only path that actually calls `signup_post::request` and polls `signup_poll::request` for backend confirmation), analogous to the VRFLottery contract computing `winner` and mutating state immediately instead of waiting for `fulfillRandomWords`/an authoritative external confirmation. [2](#0-1) 
This mirrors the reported bug's root cause precisely: a security/outcome-determining action (declaring a signup "successful," i.e., "declaring a winner") is finalized based on a value produced by the requesting party's own local computation, without waiting on/requiring the authoritative party (backend, analogous to the VRF coordinator) to confirm and record that outcome.

### Impact Explanation
If the local fraud/liveness/pipeline determination is bypassed, spoofed, or simply diverges from the backend's own re-validation (e.g. due to a compromised or buggy on-device pipeline, or a QR/app that sets `user_centric_signup: true` to skip the authoritative check), `debug_report.enrollment_status` and `result.success` are marked `Success` and UI shows `signup_success()` without the backend ever confirming or recording the enrollment via `signup_post`/`signup_poll`. This can produce a signup that the Orb believes succeeded (and reports to the user/operator as such) without corresponding backend-side state, i.e., a misattributed/unconfirmed signup outcome analogous to the lottery paying a "winner" before the random draw was ever authoritatively finalized.

### Likelihood Explanation
This path is reachable whenever the backend/app marks a QR session `user_centric_signup: true` (the intended app-centric flow) and `ignore_user_centric_signups` config flag is false (the default per `src/config.rs`): [3](#0-2) 
Since the FOSS build has all fraud checks stripped (`N_FRAUD_CHECKS = 0`), `detect_fraud` always returns `false`, making `signup_reason` effectively always `Normal` whenever the pipeline succeeds: [4](#0-3) [5](#0-4) 
This substantially increases the practical likelihood that the on-device-only decision is treated as ground truth for "success" without ever being checked against the backend's authoritative enrollment result.

### Recommendation
Do not report `success`/`Success` enrollment status based solely on locally-derived `signup_reason` for user-centric signups. Instead, always call the backend (`signup_post::request` + `signup_poll::request`, as done in `enroll_user::Plan::run`) — or an equivalent authoritative confirmation endpoint — before finalizing and reporting a signup outcome, mirroring the recommended Solidity fix of only finalizing state changes after the authoritative asynchronous response (`fulfillRandomWords`) is received.

### Proof of Concept
1. Configure a QR session with `user_centric_signup: true` (default `ignore_user_centric_signups = false`). [6](#0-5) 
2. Complete biometric capture such that the local pipeline succeeds and (FOSS) `detect_fraud` trivially returns `false`, yielding `signup_reason = SignupReason::Normal`. [7](#0-6) 
3. Observe that `do_signup` marks `enrollment_status` as `Success` and sets `result.success = true` at lines 639–656, without ever invoking `enroll_user::Plan::run` (i.e., without any backend `signup_post`/`signup_poll` round trip that would authoritatively confirm the enrollment): [8](#0-7)

### Citations

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

**File:** src/plans/mod.rs (L639-661)
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

**File:** src/plans/enroll_user.rs (L72-102)
```rust
    pub async fn run(self, orb: &mut Orb) -> Status {
        let user_qr_code = self.user_qr_code.clone();
        let signature = if let Some(p) = self.pipeline.cloned() {
            match task::spawn_blocking(move || make_signature(&user_qr_code, &p)).await {
                Ok(Ok(signature)) => Some(signature),
                Ok(Err(err)) => {
                    tracing::error!("Failed to calculate signature: {err:?}");
                    return Status::SignatureCalculationError;
                }
                Err(err) => {
                    tracing::error!("Failed to calculate signature: {err:?}");
                    return Status::SignatureCalculationError;
                }
            }
        } else {
            None
        };
        tracing::info!("Iris code signature: {:?}", signature);
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
```

**File:** src/config.rs (L120-121)
```rust
    /// Ignore app centric signup flag from the app and always perform an enrollment request.
    pub ignore_user_centric_signups: bool,
```

**File:** src/config.rs (L436-437)
```rust
            ignore_user_centric_signups: false,
            user_qr_validation_use_full_operator_qr: false,
```

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
```
