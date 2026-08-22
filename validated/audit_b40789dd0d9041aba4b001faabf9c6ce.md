### Title
Fraud detection is fully disabled, allowing fraudulent signups to bypass detection - (File: `src/plans/fraud_check.rs`, `src/plans/mod.rs`)

### Summary
The bug report describes a case where a fork (SolidlyV3) silently removed the LP-fee accounting logic present in the original UniswapV3 implementation, so a downstream integration (SolidlyV3AMO) that assumes fees are still tracked ends up never being able to collect them — the accounting/enforcement logic was stripped out of the code path that downstream logic depends on. The equivalent pattern in `orb-core` is that the fraud-check engine's core logic has been entirely stripped out (`N_FRAUD_CHECKS = 0`), while the orchestration code in `src/plans/mod.rs` still calls into it and treats its result as authoritative for signup fraud decisions.

### Finding Description
`src/plans/fraud_check.rs` defines `N_FRAUD_CHECKS: usize = 0` with the comment "FOSS: This is set to 0 because we manually deleted all fraud checks" [1](#0-0) . As a direct consequence, `fraud_checks()`, `enabled_checks_from_config()`, and `feedback_messages()` all return empty arrays [2](#0-1) , and `Report::fraud_detected()` / `fraud_detected_with_config()` can never return `true` since they iterate over zero-length arrays [3](#0-2) .

Consuming this, `Plan::detect_fraud` in `src/plans/mod.rs` explicitly documents the same removal ("// FOSS: WE HAVE DELETED ALL FRAUD CHECKS") and unconditionally returns `Ok(false)` regardless of the biometric pipeline output passed to it [4](#0-3) . This function's result is then used in `do_signup` to compute `fraud_detected`, which feeds into `signup_reason` (`SignupReason::Fraud` vs `SignupReason::Normal`), which in turn determines whether the debug report is flagged as fraud and whether the pipeline/build proceeds treating the signup as legitimate [5](#0-4) .

This mirrors the root cause pattern in the external report exactly: a fork/derivative removed the enforcement/accounting logic (fee tracking in SolidlyV3’s `Position.update`, fraud-check logic in `fraud_check.rs`), but the calling code (`SolidlyV3AMO`, `do_signup`) still invokes the higher-level function as if the underlying enforcement were intact, silently producing an always-benign result (no fees / no fraud) instead of surfacing the missing capability.

### Impact Explanation
Because `detect_fraud` always returns `false`, any fraudulent, duplicate, or otherwise disqualifying biometric signup that would normally be caught by the Fraud Check Engine is instead unconditionally classified as `SignupReason::Normal`, allowing enrollment to proceed via `enroll_user` [6](#0-5) . This is a concrete fraud/liveness enforcement bypass reachable by any unprivileged end user going through the standard signup flow — no special privileges or backend/hardware access are required.

### Likelihood Explanation
This is not a conditional or edge-case bug — it is unconditionally triggered on every signup that reaches the fraud-detection stage, since `N_FRAUD_CHECKS` is hardcoded to `0` and `detect_fraud` has no logic branch that can return `true`. Any signup attempt in this build will always be treated as fraud-free by the local fraud-check stage.

### Recommendation
Reintroduce the actual fraud-check logic (or, if this is an intentional open-source reduction, ensure that a build built from this code path is never used to gate real production signup/enrollment decisions, and that `signup_reason`/enrollment logic does not silently default to "normal" when fraud-check data is structurally absent). At minimum, `fraud_checks_strict()` and callers should fail closed (treat missing/absent fraud-check capability as inconclusive/fraud) rather than fail open (`false`) when `N_FRAUD_CHECKS == 0`.

### Proof of Concept
1. Any unprivileged user completes a signup through `do_signup` in `src/plans/mod.rs`.
2. `biometric_pipeline` succeeds (or even conditions that would normally be flagged fraudulent), producing a `Pipeline`.
3. `detect_fraud` is invoked with the pipeline result but ignores it, returning `Ok(false)` at `src/plans/mod.rs:1405` [7](#0-6) .
4. `signup_reason` is computed as `SignupReason::Normal` [8](#0-7) , and enrollment proceeds as a legitimate, non-fraudulent signup regardless of underlying fraud indicators.

### Citations

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
```

**File:** src/plans/fraud_check.rs (L67-82)
```rust
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

    fn feedback_messages() -> [Option<PipelineFailureFeedbackMessage>; N_FRAUD_CHECKS] {
        []
    }
```

**File:** src/plans/fraud_check.rs (L88-114)
```rust
    pub fn fraud_detected_with_config(
        &self,
        config: &BackendConfig,
    ) -> (bool, Vec<PipelineFailureFeedbackMessage>) {
        let enabled_checks = Self::enabled_checks_from_config(config);
        let fraud_results = self.fraud_checks_strict();
        let feedback_msgs = Self::feedback_messages();

        let feedback: Vec<PipelineFailureFeedbackMessage> = enabled_checks
            .iter()
            .zip(fraud_results.iter())
            .zip(feedback_msgs.iter())
            .filter_map(
                |((&enabled, &result), feedback_msg)| {
                    if enabled && result { feedback_msg.clone() } else { None }
                },
            )
            .collect();

        (!feedback.is_empty(), feedback)
    }

    /// If any fraud check fails or is missing data, fraud is reported.
    #[must_use]
    pub fn fraud_detected(&self) -> bool {
        self.fraud_checks_strict().iter().any(|&v| v)
    }
```

**File:** src/plans/mod.rs (L563-571)
```rust
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
