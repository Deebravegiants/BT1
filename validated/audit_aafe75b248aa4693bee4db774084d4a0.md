### Title
Fraud detection is a no-op (N_FRAUD_CHECKS = 0) causing fail-open acceptance of any biometric capture - (File: src/plans/fraud_check.rs)

### Summary
`FraudChecks::run` unconditionally returns an empty `Report {}`, and `Report::fraud_detected` iterates over the (always empty) `fraud_checks_strict()` array, so it always returns `false`. As a result, `MasterPlan::do_signup`'s fraud-detection branch can never select `SignupReason::Fraud`, and every completed capture pipeline is treated as `SignupReason::Normal`.

### Finding Description
`N_FRAUD_CHECKS` is hardcoded to `0` with the comment "we manually deleted all fraud checks", and every method on `Report` (`fraud_checks`, `fraud_checks_strict`, `enabled_checks_from_config`, `feedback_messages`) returns a fixed-size-0 array/empty vec. `fraud_detected` computes `.any(|&v| v)` over an empty iterator, which is always `false` regardless of any biometric data. `FraudChecks::new` takes a `&biometric_pipeline::Pipeline` but stores it only as `PhantomData`, ignoring its contents entirely, and `run` just returns `Report {}` unconditionally. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

In `MasterPlan::do_signup`, the result of the pipeline (`detect_fraud`) feeds directly into `signup_reason`, which is `SignupReason::Fraud` only if `fraud_detected` is true — a branch that is now dead code because `fraud_detected` is a compile-time constant `false`. [5](#0-4) 

The `fraud-engine` crate (`fraud-engine/src/report.rs`, `fraud-engine/src/pipeline.rs`) does contain a real rule-based `Report::fraud_detected` and `Pipeline::run` implementation, but that is a separate, generic library — the actual runtime plan `plans::fraud_check::FraudChecks` used by `do_signup` does not call into it; it is self-contained and stubbed out.

### Impact Explanation
Since `fraud_detected` can never be `true`, no signup can ever be flagged and rejected as fraud through this code path. Any presented capture — spoofed iris, printed photo, replay attack, or otherwise degenerate/garbage biometric data — reaches `SignupReason::Normal` as long as it passes `biometric_capture`/`biometric_pipeline` (image quality/liveness gates that are separate from this fraud engine). This corresponds to a liveness/fraud-detection bypass allowing unauthorized/fraudulent signups to be accepted as legitimate.

### Likelihood Explanation
No preconditions are required — this is unconditional dead code triggered on every single signup attempt that reaches the fraud-check stage (`!self.skip_fraud_checks()` and pipeline present), fully reproducible on demand, since `N_FRAUD_CHECKS` is a compile-time constant. [6](#0-5) 

### Recommendation
Restore or reintroduce concrete fraud-check rules (populate `N_FRAUD_CHECKS` with the real checks and implement `fraud_checks`/`enabled_checks_from_config`/`feedback_messages` against actual biometric-pipeline outputs) so `Report::fraud_detected` can express a positive fraud verdict, or route fraud detection into the generic `fraud-engine::Pipeline` implementation which already supports rule evaluation, wiring `biometric_pipeline::Pipeline` results into it instead of discarding them via `PhantomData`.

### Proof of Concept
Unit test in `src/plans/fraud_check.rs`:
```rust
#[test]
fn fraud_checks_never_detect_fraud() {
    let pipeline = biometric_pipeline::Pipeline::default(); // or any attacker-controlled/garbage data
    let mut checks = FraudChecks::new(&pipeline);
    let report = checks.run();
    assert!(!report.fraud_detected()); // always false, proving fail-open
}
```
This proves that regardless of `Pipeline` contents, `fraud_detected()` is always `false`, confirming the fraud engine cannot flag any signup as fraudulent.

### Citations

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

**File:** src/plans/fraud_check.rs (L110-114)
```rust
    /// If any fraud check fails or is missing data, fraud is reported.
    #[must_use]
    pub fn fraud_detected(&self) -> bool {
        self.fraud_checks_strict().iter().any(|&v| v)
    }
```

**File:** src/plans/fraud_check.rs (L141-153)
```rust
impl<'a> FraudChecks<'a> {
    /// Create a new FraudCheck.
    #[must_use]
    pub fn new(_pipeline: &'a biometric_pipeline::Pipeline) -> Self {
        Self { _phantom: PhantomData }
    }

    /// Run all fraud checks.
    #[must_use]
    pub fn run(&mut self) -> Report {
        Report {}
    }
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
