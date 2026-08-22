This confirms that the fraud-check mechanism is explicitly deactivated in this open-source build: `N_FRAUD_CHECKS` is hardcoded to `0` and the comment states "FOSS: This is set to 0 because we manually deleted all fraud checks", with `Report::fraud_checks()` returning an empty array and `Plan::detect_fraud` in `src/plans/mod.rs` unconditionally returning `Ok(false)` for any completed pipeline.

### Title
Fraud/liveness enforcement is unconditionally disabled in signup pipeline, allowing every completed capture to be enrolled without abuse penalization - ([File: src/plans/mod.rs, src/plans/fraud_check.rs])

### Summary
The analog to the CurveDAO report's "unmonitored `kick` function → abusive users go unpenalized" issue is the orb-core signup flow's fraud-detection stage, which has been stubbed out to always report "no fraud," regardless of the biometric pipeline's actual output.

### Finding Description
`Plan::detect_fraud` in [1](#0-0)  takes the completed biometric `pipeline` as input but, instead of evaluating any fraud signal, contains only the comment `// FOSS: WE HAVE DELETED ALL FRAUD CHECKS` and unconditionally returns `Ok(false)`. This return value feeds directly into `signup_reason` selection in the caller: [2](#0-1)  which sets `SignupReason::Fraud` only if `fraud_detected` is `true` — a condition that can never occur.

The underlying `fraud_check::Report` type backs this behavior structurally: `N_FRAUD_CHECKS` is hardcoded to `0` with the comment "FOSS: This is set to 0 because we manually deleted all fraud checks" [3](#0-2) , and `fraud_checks()`, `enabled_checks_from_config()`, and `feedback_messages()` all return empty arrays [4](#0-3) . Consequently `fraud_detected()` and `fraud_detected_with_config()` — which iterate over these empty arrays — can never signal fraud [5](#0-4) .

This is the direct structural analog of the CurveDAO report's core concern: a control meant to penalize/flag abusive behavior (there, the `kick` function in `LiquidityGauge`; here, the fraud-check stage gating `SignupReason::Fraud`) is present in the architecture but effectively inert, so abuse that the system is designed to catch flows through unchecked.

### Impact Explanation
Any unprivileged user completing the biometric capture and pipeline stages will always be tagged `SignupReason::Normal` (assuming pipeline success) instead of `SignupReason::Fraud`, because `detect_fraud` cannot return `true`. This removes an entire enforcement layer intended to reject or penalize fraudulent/abusive signup attempts (e.g., detected occlusions, spoofing indicators, or other fraud-engine signals that would otherwise map into this report), directly mirroring the external report's exploit scenario where users benefit from an un-enforced penalty mechanism and receive entitlements (there, CRV rewards) they should not receive (here, a completed/normal signup they should not receive).

### Likelihood Explanation
This is reachable on every signup by any unprivileged user — it is not a malicious-operator or hardware-access scenario, and it is on the default/only code path (`detect_fraud` is called unconditionally for every non-`None` pipeline) [6](#0-5) , making likelihood high given the disabled state is unconditional rather than a rare edge case.

### Recommendation
- **Short term:** Confirm whether this FOSS build is intended to run with fraud checks entirely absent in production; if not, restore/re-enable the fraud-check pipeline logic (or gate the FOSS build behind a feature flag that cannot be enabled in production signup flows) so `detect_fraud` reflects real fraud-engine output rather than a hardcoded `false`.
- **Long term:** Treat any "stub" security-relevant logic (fraud detection, liveness enforcement) merged for open-sourcing purposes as a build-time hazard; add CI/config assertions that fail production builds if `N_FRAUD_CHECKS == 0` or fraud checks are empty, and document the FOSS-vs-production divergence explicitly so it cannot be shipped inadvertently.

### Proof of Concept
1. Complete biometric capture and biometric pipeline stages as any unprivileged user (Alice-analog) at an orb running this FOSS build.
2. `Plan::detect_fraud` is invoked with `Some(pipeline)`; it does not evaluate `pipeline` at all and returns `Ok(false)` [7](#0-6) .
3. `signup_reason` is computed as `SignupReason::Normal` (since `fraud_detected == false`) even if the underlying capture/pipeline contained data that a real fraud-check implementation would have flagged [2](#0-1) .
4. Enrollment proceeds as a normal, non-fraud signup, and the abuse-penalization step that the architecture is designed to perform never triggers.

### Citations

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

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
```

**File:** src/plans/fraud_check.rs (L64-82)
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
