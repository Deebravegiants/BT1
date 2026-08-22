### Title
Fraud checks are hardcoded to a "no fraud" outcome, allowing enrollment to proceed for signups that should be rejected as fraudulent - (File: src/plans/mod.rs, src/plans/fraud_check.rs)

### Summary
`FraudChecks::run` in `src/plans/fraud_check.rs` always returns an empty `Report {}` because `N_FRAUD_CHECKS` is hardcoded to `0`, and `Report::fraud_detected`/`fraud_detected_with_config` operate over that empty array, so they can never report fraud. This directly drives `MasterPlan::detect_fraud` in `src/plans/mod.rs`, whose result feeds `signup_reason` and ultimately `Builder::signup_successful` via `report_signup_reason`.

### Finding Description
In `do_signup` (`src/plans/mod.rs`), the flow is: [1](#0-0) 
`pipeline` is produced by `biometric_pipeline`, then `fraud_detected` is computed by calling `self.detect_fraud(orb, debug_report, pipeline.as_ref())`. This value gates `signup_reason`: `Fraud` vs `Normal`.

Tracing into the fraud-check implementation, `FraudChecks::run` (`src/plans/fraud_check.rs`) unconditionally returns `Report {}` regardless of any input pipeline data: [2](#0-1) 
This is because the module-level constant that sizes every fraud-relevant array is zero: [3](#0-2) 
Consequently `Report::fraud_checks()` returns `[]`, `fraud_checks_strict()` maps over an empty array, and both `fraud_detected()` and `fraud_detected_with_config()` structurally cannot return `true`: [4](#0-3) [5](#0-4) 

Even though `Builder::face_identifier_results`, `Builder::fraud_check_report`, and `Builder::occlusion_error` in `src/debug_report.rs` exist to record face-identifier fraud outputs, occlusion errors, and pipeline errors into the debug report structures, nothing in the reachable code path consumes those recorded values to compute the boolean fed into `signup_reason`. The `FraudChecks` plan constructor even ignores its `pipeline` argument (`_pipeline: &'a biometric_pipeline::Pipeline`), so pipeline-detected anomalies (duplicate face, occlusion, contact lenses, printed photo, etc.) are captured for reporting/telemetry purposes only and never influence the pass/fail decision.

As a result, `report_signup_reason` (`src/plans/mod.rs`) will only take the `SignupReason::Fraud` branch if `detect_fraud` ever returns `true`, which given the current implementation, is unreachable: [6](#0-5) 

The comment in the fraud-check module explicitly acknowledges this is an intentional FOSS deletion ("FOSS: This is set to 0 because we manually deleted all fraud checks"), confirming the stub is not an accidental omission but a deliberate removal of enforcement logic, without any fail-closed fallback.

### Impact Explanation
An unprivileged attacker who deliberately presents fraudulent biometric conditions (duplicate face, occluded eyes, printed photo, contact lenses) during their own signup session can reach `enroll_user`/`signup_successful` because the orb-side fraud gate can never flag `fraud_detected = true`. This matches the described critical scope: a liveness/fraud bypass that allows an attacker to complete and become fully enrolled for a signup that should have been rejected. This is a fail-open condition on a safety/anti-fraud control (violating "missing/deleted fraud check must never be treated as passing"), directly enabling identity/policy bypass at signup time from the orb's local decision path.

Note: whether this results in an actually usable identity depends on whether backend-side (server) validation independently rejects fraudulent signups; the code in scope here only proves the orb-local fail-open behavior, since I could not verify server-side fraud gating within these files.

### Likelihood Explanation
Fully attacker-controlled and repeatable: the only precondition is completing `biometric_capture` and `biometric_pipeline` with any input (including deliberately fraudulent presentations), which is explicitly allowed to an unprivileged, ordinary signup participant. No operator privileges, keys, or backend collusion are required — the vulnerable code executes unconditionally on every signup unless `skip_fraud_checks` is already disabling it (in which case the outcome is identical: no fraud gating), as seen at: [7](#0-6) 

### Recommendation
Restore fail-closed semantics for `FraudChecks`/`Report` in `src/plans/fraud_check.rs`: populate `N_FRAUD_CHECKS` with the actual number of enabled checks, wire `FraudChecks::run` to consume face-identifier results, occlusion errors, and any pipeline-provided fraud signals from `biometric_pipeline::Pipeline`, and ensure `fraud_checks_strict()` treats missing/error data as fraud (`unwrap_or(true)`, already present structurally but unreachable with zero checks). At minimum, until real checks are reintroduced, `detect_fraud` in `src/plans/mod.rs` should not unconditionally return `Ok(false)`; any known pipeline errors (e.g., `pipeline_errors.occlusion_error`, `face_identifier_error`) already recorded on `debug_report` should be treated as fraud/failure rather than being ignored.

### Proof of Concept
Integration test (in a test module alongside `src/plans/mod.rs` or `src/plans/fraud_check.rs`) with expected assertions:
1. Construct a `biometric_pipeline::Pipeline` (or the equivalent debug-report state) with `Builder::face_identifier_results` fed `Err(PyError)`/fraudulent `FraudChecks`, and `Builder::occlusion_error` fed `Some(PyError)` simulating occluded eyes/contact lenses detection.
2. Call `FraudChecks::new(&pipeline).run()` and assert `report.fraud_detected() == true`. Currently this assertion fails because `fraud_checks_strict()` iterates over `[]` and `any()` on an empty iterator is always `false`.
3. Drive `MasterPlan::do_signup` (or a directly-callable wrapper around `detect_fraud`) with the same fraudulent pipeline state and assert `result.success == false` and that `debug_report.signup_status == Some(SignupStatus::Fraud)` (i.e., `Builder::signup_fraud()` was invoked instead of `Builder::signup_successful()`). Currently this fails: `detect_fraud` returns `Ok(false)`, `signup_reason` becomes `SignupReason::Normal`, and `report_signup_reason` calls `debug_report.signup_successful()`.

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

**File:** src/plans/mod.rs (L665-683)
```rust
    fn report_signup_reason(
        success: bool,
        signup_reason: SignupReason,
        debug_report: &mut debug_report::Builder,
    ) {
        if signup_reason == SignupReason::Failure {
            tracing::info!("User enrollment failed due to a failure in the pipeline");
            debug_report.signup_orb_failure();
        } else if signup_reason == SignupReason::Fraud {
            tracing::info!("User enrollment failed due to fraud");
            debug_report.signup_fraud();
        } else if success {
            debug_report.signup_successful();
            dd_incr!("main.count.signup.result.success.successful_signup");
        } else {
            tracing::info!("User enrollment failed");
            debug_report.signup_server_failure();
        }
    }
```

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
```

**File:** src/plans/fraud_check.rs (L88-108)
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
```

**File:** src/plans/fraud_check.rs (L110-114)
```rust
    /// If any fraud check fails or is missing data, fraud is reported.
    #[must_use]
    pub fn fraud_detected(&self) -> bool {
        self.fraud_checks_strict().iter().any(|&v| v)
    }
```

**File:** src/plans/fraud_check.rs (L148-152)
```rust
    /// Run all fraud checks.
    #[must_use]
    pub fn run(&mut self) -> Report {
        Report {}
    }
```
