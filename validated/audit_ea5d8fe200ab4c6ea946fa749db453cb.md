### Title
Fraud/liveness enforcement is fully disabled, allowing any signup to bypass on-device fraud detection - ([File: src/plans/mod.rs])

### Summary
`MasterPlan::detect_fraud` in `src/plans/mod.rs` and `fraud_check::Report` in `src/plans/fraud_check.rs` implement the on-device fraud/liveness enforcement gate that runs during every signup, but the implementation has been stubbed out to always report "no fraud detected," regardless of the biometric pipeline output. This mirrors the reported bug class — a critical state-changing/decision-making function that lacks any actual validation of its inputs before allowing a security-relevant action (accepting a signup) — except here the "validation" is a no-op on every unprivileged user's signup attempt, not an admin-gated write.

### Finding Description
`detect_fraud` is called for every signup on the biometric pipeline output, but immediately discards any real detection logic: [1](#0-0) 

It unconditionally returns `Ok(false)` (no fraud detected) whenever a pipeline exists, with the comment `// FOSS: WE HAVE DELETED ALL FRAUD CHECKS` marking the intentional removal of the checks. The backing `fraud_check::Report` type structurally supports zero checks: [2](#0-1) 

`fraud_checks()` returns an empty array, so `fraud_detected()` (`self.fraud_checks_strict().iter().any(|&v| v)`) can never be `true`, and `fraud_detected_with_config` can never surface a fraud feedback message. This function is invoked directly in the main signup flow to decide the `SignupReason` (`Normal` vs `Fraud`) sent to the backend: [3](#0-2) 

Since `fraud_detected` is always `false`, `signup_reason` can never become `SignupReason::Fraud` through this path, and the enrollment/personal-custody-package pipeline proceeds as if the signup were always legitimate.

### Impact Explanation
This directly enables a "fraud/liveness bypass" as flagged as valid impact: any unprivileged user completing a signup on this build has zero on-device fraud/liveness gating, no matter what anomalies the biometric pipeline may have surfaced (e.g., duplicate/spoofed captures, non-live subjects, occlusion-based tampering signals that the pipeline may compute but that never reach a decision point). The trust boundary between "biometric pipeline produced suspicious signals" and "signup is accepted as Normal" is completely severed, since the intermediate decision function is a stub that always returns "not fraud." This is analogous to the reported admin-rug-vector pattern in that a critical gating function silently no-ops instead of enforcing its intended invariant, but here the affected actor is any regular, unprivileged signup participant rather than a protocol admin.

### Likelihood Explanation
Likelihood is high/certain: this code path is on the default signup flow (`do_signup`) executed for every signup on any orb running this build, with no additional preconditions, feature flags, or attacker sophistication required — the bypass is unconditional and structural rather than requiring a crafted input.

### Recommendation
Reintroduce the actual fraud/liveness checks in `fraud_check::Report::fraud_checks()` (and populate `N_FRAUD_CHECKS`/`DATADOG_TAGS`/`enabled_checks_from_config`/`feedback_messages`) so that `detect_fraud` in `src/plans/mod.rs` reflects the real output of the biometric pipeline's fraud signals, and ensure `SignupReason::Fraud` is set whenever those checks fail, instead of the current unconditional `Ok(false)`.

### Proof of Concept
1. Complete a normal signup end-to-end on an orb running this build (`src/plans/mod.rs::do_signup`).
2. Regardless of what the biometric pipeline computes (occlusion, image quality, iris code anomalies, etc.), `self.detect_fraud(...)` at `src/plans/mod.rs:563-564` always evaluates to `false` because `Report::fraud_detected()` in `src/plans/fraud_check.rs:110-114` iterates over an always-empty `fraud_checks()` array.
3. `signup_reason` is therefore always `SignupReason::Normal` (never `Fraud`) for any completed pipeline, and the signup is processed as legitimate by `enroll_user`/`personal_custody_package`, with no possibility of an on-device fraud flag ever being raised.

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
