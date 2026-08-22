### Title
`detect_fraud` unconditionally returns `Ok(false)`, permanently disabling fraud detection during signup - ([File: src/plans/mod.rs])

### Summary
`MasterPlan::detect_fraud` in `src/plans/mod.rs` never performs any actual fraud analysis: for `pipeline = None` it returns `Ok(false)`, and for `pipeline = Some(_)` it falls through a comment stating all fraud checks were deleted and also returns `Ok(false)`. Because `do_signup` uses this return value directly to decide `SignupReason::Fraud` vs `SignupReason::Normal`, no signup can ever be flagged as fraudulent through this path, regardless of the biometric pipeline's content.

### Finding Description
In `do_signup`, the signup reason is computed as:
```
let fraud_detected = !self.skip_fraud_checks() && self.detect_fraud(orb, debug_report, pipeline.as_ref()).await?;
let signup_reason = if pipeline.is_none() { SignupReason::Failure } else if fraud_detected { SignupReason::Fraud } else { SignupReason::Normal };
``` [1](#0-0) 

`detect_fraud` itself is:
```
async fn detect_fraud(&mut self, orb: &mut Orb, _debug_report: &mut debug_report::Builder, pipeline: Option<&biometric_pipeline::Pipeline>) -> Result<bool> {
    orb.set_phase("Fraud detection").await;
    let Some(_pipeline) = pipeline else { return Ok(false); };
    // FOSS: WE HAVE DELETED ALL FRAUD CHECKS
    Ok(false)
}
``` [2](#0-1) 

The underlying `fraud_check::Report` type corroborates this: `N_FRAUD_CHECKS` is hardcoded to `0`, and every check-derivation function (`fraud_checks`, `fraud_checks_strict`, `enabled_checks_from_config`, `feedback_messages`) returns an empty array, so `fraud_detected()` can never be `true`. [3](#0-2) [4](#0-3) 

The `fraud_check::FraudChecks::run` plan similarly always returns an empty `Report {}` regardless of pipeline content. [5](#0-4) 

No other gate re-validates fraud status downstream in `do_signup`: `signup_reason` (already fixed to `Normal`/`Failure`) is passed straight into `build_pcp` and `enroll_user`. [6](#0-5) 

Since the function body ignores the `pipeline` argument entirely aside from the `None` check, the invariant claimed in the question holds exactly: for any `Some(pipeline)`, including fuzzed/malformed pipeline data (mismatched iris shares, empty codes, etc.), `detect_fraud` returns `Ok(false)` deterministically.

### Impact Explanation
Any attacker able to complete biometric capture (an unprivileged, in-session signup attempt) is guaranteed the backend will receive `SignupReason::Normal` instead of `SignupReason::Fraud`, since the fraud pipeline that would normally gate this decision is a no-op. This is a full fraud/liveness-enforcement bypass affecting every signup, not merely an edge case — it removes the Orb-side fraud safety net documented by the code's own type definitions (`Report`, `PipelineFailureFeedbackMessage`) which imply an active fraud-detection contract that no longer executes.

### Likelihood Explanation
Fully deterministic and reachable by any attacker who can just complete a normal signup flow up through `biometric_pipeline` (no privilege, keys, or tampering needed) — `do_signup` calls `detect_fraud` unconditionally on the happy path whenever `skip_fraud_checks()` is false and a pipeline was produced. There is no dependency on rare state or race conditions.

### Recommendation
Restore real fraud-check logic in `fraud_check::Report`/`FraudChecks::run` and wire `detect_fraud` in `src/plans/mod.rs` to actually evaluate the biometric `Pipeline` (e.g., via `fraud-engine::pipeline::Pipeline::run`) instead of returning a hardcoded `Ok(false)`. At minimum, add a compile-time or runtime gate to prevent this fail-open stub from being used in a production/non-FOSS build to enforce fail-closed behavior.

### Proof of Concept
Add a fuzz/invariant test in `src/plans/mod.rs` (or a test module with access to `MasterPlan`) that constructs a range of `biometric_pipeline::Pipeline` values — including deliberately malformed ones with empty `iris_code_shares`/`mask_code_shares` or mismatched left/right eye data — wraps each in `Some(...)`, and calls `detect_fraud(orb, debug_report, pipeline.as_ref())`. Assert `matches!(result, Ok(false))` for every case, demonstrating the function never returns `Ok(true)` regardless of `Pipeline` content, and separately trace `do_signup` to show this guarantees `signup_reason != SignupReason::Fraud` whenever `pipeline.is_some()`. [7](#0-6)

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

**File:** src/plans/mod.rs (L580-587)
```rust
            let packages = match Box::pin(self.build_pcp(
                orb,
                credentials,
                &capture,
                pipeline.as_ref(),
                debug_report,
                signup_reason,
            ))
```

**File:** src/plans/mod.rs (L1392-1406)
```rust
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
