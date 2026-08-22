### Title
`MasterPlan::detect_fraud` unconditionally returns `Ok(false)`, disabling all fraud/duplicate-biometric detection - ([File: src/plans/mod.rs])

### Summary
`MasterPlan::detect_fraud` in `src/plans/mod.rs` has had its entire body replaced with a comment (`// FOSS: WE HAVE DELETED ALL FRAUD CHECKS`) and now hard-codes `Ok(false)` for both the "no pipeline" branch and the normal branch. This means fraud detection can never return `true`, regardless of the biometric pipeline content, so `SignupReason::Fraud` can never be triggered from this code path. The underlying `fraud_check::Report` engine (`src/plans/fraud_check.rs`) is likewise gutted, with `N_FRAUD_CHECKS` set to `0` and `fraud_checks()` returning an empty array, so even the "fail-closed on missing data" logic in `fraud_checks_strict` operates over zero checks and trivially yields no fraud.

### Finding Description
`detect_fraud` at `src/plans/mod.rs:1392-1406` takes an `Option<&biometric_pipeline::Pipeline>` produced from the attacker-controlled biometric capture/pipeline for the signup session: [1](#0-0) 

- If `pipeline` is `None` (e.g., pipeline failed), it returns `Ok(false)` — i.e., "no fraud detected" — instead of failing closed.
- If `pipeline` is `Some`, the function does nothing with its contents (the fraud-check body was deleted) and unconditionally returns `Ok(false)`.

This directly violates the fail-closed invariant: missing or erroring biometric/fraud signals must never be treated as "no fraud." An attacker who presents a duplicate biometric, a spoofed/replayed scene, or any other fraudulent physical presentation to the cameras during their own signup session will have that biometric processed into a `Pipeline`, passed into `detect_fraud`, and always receive `false` back — because the function does not inspect the pipeline content at all.

Supporting this, the underlying check engine `fraud_check::Report` (`src/plans/fraud_check.rs:10-13,64-114`) has been reduced to zero checks: `N_FRAUD_CHECKS = 0`, `fraud_checks()` returns `[]`, and `fraud_detected()`/`fraud_detected_with_config()` iterate over an empty array, so they can never return true either. There is no other gate downstream — nothing recomputes fraud verdicts from the pipeline independently of `detect_fraud`'s return value in `src/plans/mod.rs`.

### Impact Explanation
This completely disables all fraud/duplicate-detection enforcement on the orb for every signup. Any attacker able to present a physical scene to the cameras (their own signup session, no privileged access required) can force `fraud_detected == false` unconditionally, causing every signup to be treated as `SignupReason::Normal` and enrolled/uploaded as legitimate. This matches the "liveness/fraud bypass" impact category for Worldcoin/Orb bounty scope — it enables systematic enrollment of fraudulent or duplicate biometrics that the fraud engine exists specifically to catch, with no operator or hardware compromise needed.

### Likelihood Explanation
Likelihood is very high / certain. No special preconditions are required beyond initiating a normal signup and presenting a fraudulent/duplicate scene to the cameras — the code path executes on every signup unconditionally, and the return value is hard-coded, not input-dependent, so the bypass is 100% reproducible on every attempt.

### Recommendation
Restore real fraud-check logic in `detect_fraud` that inspects `pipeline` (e.g., duplicate iris-code matching, face-identifier fraud checks, occlusion/liveness signals already computed into the pipeline, such as `pipeline.face_identifier_fraud_checks`) and returns `true` when any check fails or data is missing. Change the `None` branch to fail closed (`Ok(true)` or propagate an error) rather than `Ok(false)`. Reinstate the deleted checks in `fraud_check::Report`/`FraudChecks::run` in `src/plans/fraud_check.rs` so `fraud_checks_strict` operates over a non-empty, meaningful check set, restoring the "missing data ⇒ fraud" fail-closed semantics.

### Proof of Concept
Unit test in `src/plans/mod.rs` (or a test module with access to `MasterPlan`):
```rust
#[tokio::test]
async fn detect_fraud_flags_duplicate_biometric() {
    // Construct a `biometric_pipeline::Pipeline` representing an obviously
    // fraudulent/duplicate biometric (e.g., face_identifier_fraud_checks
    // populated with a known-duplicate match result).
    let fraudulent_pipeline = build_pipeline_with_duplicate_match();

    let mut plan = MasterPlan::default_for_test();
    let mut orb = Orb::mock();
    let mut debug_report = debug_report::Builder::default();

    let result = plan
        .detect_fraud(&mut orb, &mut debug_report, Some(&fraudulent_pipeline))
        .await
        .unwrap();

    // Expected (invariant-preserving) behavior: fraud is detected.
    assert!(result, "detect_fraud must return true for a duplicate/fraudulent biometric");
}
```
Running this against the current code fails the assertion because `detect_fraud` unconditionally returns `Ok(false)` at `src/plans/mod.rs:1405`, regardless of `fraudulent_pipeline`'s contents — demonstrating the always-false invariant violation.

### Citations

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
