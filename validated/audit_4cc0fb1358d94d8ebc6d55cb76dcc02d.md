### Title
`FraudChecks::run` / `Report::fraud_detected_with_config` are hard-wired no-ops that always report "no fraud" - ([File: src/plans/fraud_check.rs])

### Summary
`N_FRAUD_CHECKS` in `src/plans/fraud_check.rs` is hardcoded to `0`, and the comment explicitly states "This is set to 0 because we manually deleted all fraud checks." All arrays derived from this constant (`fraud_checks`, `fraud_checks_strict`, `enabled_checks_from_config`, `feedback_messages`) are empty, so `Report::fraud_detected()` and `Report::fraud_detected_with_config()` are structurally guaranteed to return `false` / an empty feedback vector no matter what the biometric pipeline observed. `FraudChecks::run` also unconditionally returns an empty `Report {}` without inspecting the `Pipeline` it was constructed with.

### Finding Description
`FraudChecks::new(&pipeline)` stores only a `PhantomData` reference and never reads pipeline fields; `run()` simply returns `Report {}` [1](#0-0) . `Report::fraud_checks()`, `fraud_checks_strict()`, `enabled_checks_from_config()`, and `feedback_messages()` all return `[]` because their array length is fixed by `const N_FRAUD_CHECKS: usize = 0` [2](#0-1) [3](#0-2) . Consequently `fraud_detected_with_config` zips three empty iterators and always yields `(false, vec![])`, and `fraud_detected()` calls `.any(|&v| v)` on an empty array, which is vacuously `false` [4](#0-3) . This matches the question's claim precisely, and is not test/mock-only code — it is the production `Report`/`FraudChecks` type used by the signup plan.

However, the `Pipeline` fed into `FraudChecks::new` does carry real occlusion/fraud-relevant data — `occlusion::EstimateOutput` and `face_identifier::FraudChecks` model outputs are present on the struct [5](#0-4)  — but this file's `FraudChecks::run` never consumes them; the wiring to those model outputs (if any exists at all) is absent in this file, and the emptied arrays mean no downstream signal can ever be produced from `Report` regardless of what the models detected.

### Impact Explanation
Because `fraud_detected()`/`fraud_detected_with_config()` are provably `false`/empty for any input, no signup can ever be blocked by this fraud-check stage — masks, multiple faces, contact lenses, or other occlusion conditions represented by `PipelineFailureFeedbackMessage` variants (`ContactLenses`, `EyeGlasses`, `Mask`, `MultipleFaces`, `EyesOcclusion`, `Underaged`, etc., defined at [6](#0-5) ) can never trigger a fraud verdict through this path, even though those enum variants still exist and imply the intent to detect them. This corresponds to a liveness/fraud-detection bypass allowing fraudulent, underage, or otherwise disqualified signups to be enrolled as normal signups.

### Likelihood Explanation
The comment "FOSS: This is set to 0 because we manually deleted all fraud checks" strongly indicates this is an intentional, documented removal for the open-source release of this repository (i.e., proprietary fraud-detection logic was stripped out before publishing), rather than an accidental defect introduced by an attacker-reachable code path. There is no attacker input needed to trigger this — it is a static, always-true condition of the shipped code, so "likelihood" in the traditional exploit sense doesn't apply; the question is whether the disclosed source matches what actually runs on production Orbs, which cannot be determined from this repository alone.

### Recommendation
If this repository/build config is what's deployed in production, the fraud-check stage must be restored: `N_FRAUD_CHECKS` should reflect the actual number of implemented checks, `FraudChecks::run` should compute real results from the `Pipeline`'s `occlusion`, `face_identifier_fraud_checks`, and related model outputs, and `fraud_detected`/`fraud_detected_with_config` should fail closed (already correct: missing data → `true`) once real checks are wired in. If this is intentionally a FOSS-stripped version and the real checks exist in a private counterpart used for actual signups, this should be explicitly documented in the repo and the impact scoped to informational only.

### Proof of Concept
```rust
// src/plans/fraud_check.rs (test module)
#[test]
fn fraud_detected_is_vacuously_false_by_construction() {
    // N_FRAUD_CHECKS == 0 forces empty arrays regardless of input.
    let report = Report::default();
    assert!(!report.fraud_detected());
    let (detected, feedback) = report.fraud_detected_with_config(&BackendConfig::default());
    assert!(!detected);
    assert!(feedback.is_empty());
}

// Even constructing FraudChecks from an "adversarial" pipeline can't change the verdict,
// because run() ignores the pipeline entirely:
#[test]
fn fraud_checks_run_ignores_pipeline_content() {
    let pipeline = biometric_pipeline::Pipeline::default_with_ok(); // stand-in for adversarial capture
    let mut checks = FraudChecks::new(&pipeline);
    let report = checks.run();
    assert!(!report.fraud_detected()); // fails to ever be true — structurally impossible
}
```
Both assertions pass unconditionally today, demonstrating that `Report::fraud_detected()`/`fraud_detected_with_config()` cannot signal fraud under any circumstance while `N_FRAUD_CHECKS == 0`.

### Citations

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
```

**File:** src/plans/fraud_check.rs (L42-62)
```rust
#[derive(Debug, Clone, SerdeSerialize, JsonSchema)]
pub enum PipelineFailureFeedbackMessage {
    /// Contact Lenses detected
    ContactLenses,
    /// Face occluded by eye glasses detected
    EyeGlasses,
    /// Face occluded by mask
    Mask,
    /// Generic face occlusion
    FaceOcclusion,
    /// Multiple faces during signup
    MultipleFaces,
    /// Eyes were occluded during signup
    EyesOcclusion,
    /// Head pose not straight up
    HeadPose,
    /// Underaged
    Underaged,
    /// Poor Image Quality
    LowImageQuality,
}
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

**File:** src/plans/fraud_check.rs (L141-152)
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
```

**File:** src/plans/biometric_pipeline/mod.rs (L56-71)
```rust
/// Biometric pipeline output.
#[derive(Clone, Debug)]
pub struct Pipeline {
    /// Pipeline v2 output.
    pub v2: PipelineV2,
    /// Occlusion detection estimate output.
    pub occlusion: Result<occlusion::EstimateOutput, PyError>,
    /// Face identifier model output for the fraud checks.
    pub face_identifier_fraud_checks: Result<face_identifier::FraudChecks, PyError>,
    /// Face identifier model output for the self-custody bundle.
    pub face_identifier_bundle: Result<face_identifier::Bundle, PyError>,
    /// Mega Agent One's configuration.
    pub mega_agent_one_config: mega_agent_one::MegaAgentOne,
    /// Mega Agent One's configuration.
    pub mega_agent_two_config: mega_agent_two::MegaAgentTwo,
}
```
