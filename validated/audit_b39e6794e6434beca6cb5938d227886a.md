### Title
Fraud/liveness enforcement is fully disabled in `MasterPlan::detect_fraud`, allowing every signup to bypass orb-side fraud detection - ([File: src/plans/mod.rs])

### Summary
The external report describes a smart-contract bug class where a registration/referral flow lacks any real verification or restriction, letting an attacker repeatedly pass through the flow and accumulate unearned credit because the enforcement mechanism is effectively a no-op. The closest concrete analog in `orb-core` is the orb-side fraud detection step in the signup pipeline: `MasterPlan::detect_fraud` in `src/plans/mod.rs` is stubbed to always return `Ok(false)` (no fraud), and the backing `fraud_check::Report` type has zero configured checks, so no biometric/fraud signal produced by the pipeline can ever cause a signup to be flagged as fraudulent at the orb.

### Finding Description
`do_signup` in `src/plans/mod.rs` computes `fraud_detected` by calling `self.detect_fraud(...)` and uses the result to decide the `SignupReason` (`Normal`, `Failure`, or `Fraud`) that is ultimately reported to the backend: [1](#0-0) 

The `detect_fraud` implementation itself is explicitly gutted: [2](#0-1) 
It unconditionally returns `Ok(false)` for any non-`None` pipeline, regardless of what the biometric pipeline (iris/face identifier fraud checks, occlusion, etc.) produced.

This is backed by `fraud_check::Report`, whose check arrays are all empty (`N_FRAUD_CHECKS` effectively 0), so `fraud_checks()`, `enabled_checks_from_config()`, and `feedback_messages()` return empty arrays — meaning `fraud_detected()` and `fraud_detected_with_config()` can never signal fraud even if underlying data indicated it: [3](#0-2) 

Because `fraud_detected` always evaluates to `false`, `signup_reason` in `do_signup` can only be `Normal` or `Failure`, never `Fraud`, and the enrollment proceeds to `enroll_user`, `build_pcp`, and PCP upload as if the biometric pipeline had cleared all fraud checks: [4](#0-3) 

This matches the report's root-cause pattern: a critical anti-abuse gate (referral/registration restriction in the original report; fraud/liveness enforcement here) exists as an API surface but performs no actual validation, so any input reaches the privileged state-mutating action (referral point award / user enrollment) unconditionally.

### Impact Explanation
With orb-side fraud detection disabled, any biometric capture that completes the pipeline (even one exhibiting fraud-indicative signals normally caught by iris/face-identifier fraud checks) is unconditionally treated as `SignupReason::Normal` at the orb, and the resulting Personal Custody Package is built and uploaded, and enrollment is submitted to the backend. This removes an entire layer of orb-side fraud/liveness enforcement described elsewhere in the codebase (`SignupReason::Fraud`, `debug_report.signup_fraud()`, UI/telemetry paths for fraud), creating a cross-signup integrity gap: fraudulent signup attempts that should be rejected at the orb are instead forwarded to the backend as legitimate, relying entirely on backend-side fraud checks (which the code comments distinguish as separate: "not to be confused with the backend fraud checks"). [5](#0-4) 

### Likelihood Explanation
This is not a probabilistic race or hard-to-reach edge case — it is a deterministic, always-triggered code path. Every signup that reaches the fraud-detection phase (`self.skip_fraud_checks()` is false by default outside of `allow-plan-mods`/test builds) executes `detect_fraud`, which is hardcoded to return `false`. No attacker action is even required to trigger it; it is unconditionally active in the mainline signup flow. The comment "FOSS: WE HAVE DELETED ALL FRAUD CHECKS" strongly suggests this is intentional redaction for the open-source release rather than a bug in the production binary — I could not verify from the available files whether the production (non-FOSS) build restores real fraud checks via a different mechanism (e.g., a proprietary crate substituted at build time, or feature flag). This is the key uncertainty: if this file is representative of what actually ships in production `orb-core`, the impact is critical; if a non-public overlay reintroduces the checks before compilation for production binaries, the exposed code here would not reflect a real vulnerability in the deployed system.

### Recommendation
- Confirm whether the production build of `orb-core` includes real implementations of `fraud_check::Report::fraud_checks`, `enabled_checks_from_config`, and `feedback_messages`, and whether `detect_fraud` in production actually inspects `pipeline` fraud signals rather than being hardcoded to `false`.
- If the FOSS repository is what is actually compiled and deployed (no closed-source override), reintroduce genuine fraud/liveness checks (e.g., face-identifier fraud checks, occlusion, contact-lens/spoof detection) into `detect_fraud` and `fraud_check::Report`, and ensure `SignupReason::Fraud` can be reached.
- Add regression tests asserting that a pipeline with fraud-indicative results (e.g., `face_identifier_fraud_checks` failures) causes `detect_fraud` to return `true` and blocks enrollment.
- Avoid shipping a "checks removed" stub in any code path that is reachable by the production binary; if redaction is required for open-sourcing, ensure the redacted module is swapped for a real implementation at build time via a clearly gated, verifiable mechanism (not a silent no-op).

### Proof of Concept
Not applicable in the traditional exploit sense since no attacker input is needed — the control-flow proof is the code itself:
1. `do_signup` calls `self.detect_fraud(orb, debug_report, pipeline.as_ref())` after `biometric_pipeline` runs.
2. `detect_fraud` returns `Ok(false)` unconditionally for any `Some(pipeline)`.
3. `signup_reason` is therefore never `SignupReason::Fraud`; only `Failure` (pipeline `None`) or `Normal`.
4. Enrollment (`enroll_user`) and PCP upload proceed with `SignupReason::Normal`, submitting the signup to the backend as legitimate regardless of underlying fraud signals in the biometric pipeline. [2](#0-1) [1](#0-0)

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

**File:** src/plans/fraud_check.rs (L64-114)
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

    /// Get the || result of all fraud checks, but under the Orb configuration.
    /// The end result might be different from the || of all fraud booleans as
    /// we might decide to not block a signup even if it's fraudulent.
    #[must_use]
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

**File:** src/backend/signup_post.rs (L79-82)
```rust
    Failure,
    /// Signup was detected as a fraud attempt at the orb (not to be confused with the backend fraud checks).
    Fraud,
}
```
