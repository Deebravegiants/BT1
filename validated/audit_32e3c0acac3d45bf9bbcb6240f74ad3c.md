### Title
Fraud detection is fully disabled (N_FRAUD_CHECKS=0), causing `Report::fraud_detected()` to vacuously return `false` and allowing biometric fraud/liveness conditions to be signed as normal signups - ([File: src/plans/fraud_check.rs])

### Summary
`N_FRAUD_CHECKS` is hardcoded to `0`, so `Report::fraud_checks()`, `fraud_checks_strict()`, and `enabled_checks_from_config()` all return empty arrays. Consequently `Report::fraud_detected()` (`.iter().any(...)` over `[]`) and `fraud_detected_with_config()` always evaluate to "no fraud detected" regardless of the actual biometric pipeline outcome. `FraudChecks::run()` also ignores the `pipeline` argument entirely (stored only as `PhantomData`) and unconditionally returns `Report {}`.

### Finding Description
The relevant code: [1](#0-0) 
defines `N_FRAUD_CHECKS: usize = 0` with the comment "FOSS: This is set to 0 because we manually deleted all fraud checks." [2](#0-1) 
shows `fraud_checks()`, `fraud_checks_strict()`, and `enabled_checks_from_config()` all return `[]` because the array size is fixed at compile time to `N_FRAUD_CHECKS`. [3](#0-2) 
`fraud_detected()` calls `.any(|&v| v)` on an empty slice, which is vacuously `false` — this is independent of any actual occlusion, contact-lens, motion-blur, or other biometric fraud signal present in the `Pipeline`. [4](#0-3) 
`FraudChecks::new()` takes a `&'a biometric_pipeline::Pipeline` reference but stores it only as `PhantomData<&'a ()>`, never inspecting it, and `run()` unconditionally constructs and returns an empty `Report {}`. This means whatever the pipeline actually observed (motion blur, occlusion, contact lens, face-identifier fraud signals) is discarded before it ever reaches the fraud-report logic — the doc comment's own stated invariant "If fraud data are missing, we assume fraud is detected" is bypassed structurally because there is no fraud-check slot to be "missing" in the first place; the array is zero-length by construction, not by a runtime missing-data case.

Given the described call sequence (`run_signup_flow -> biometric_pipeline -> detect_fraud -> enroll_user with SignupReason::Normal -> build_pcp -> secure_element::sign`), if `detect_fraud` in `src/plans/mod.rs` treats a `false` return from `fraud_detected()`/`fraud_checks_strict()` as "no fraud, continue as Normal," then any borderline or outright fraudulent capture that isn't rejected upstream by `biometric_pipeline` itself (e.g., partial occlusion or contact-lens detection that produces `Ok(...)` results rather than a hard pipeline error) proceeds straight to `SignupReason::Normal`, `enroll_user`, `build_pcp`, and a valid `secure_element::sign` signature.

Note: I was not able to fully retrieve/verify the exact body of `detect_fraud` in `src/plans/mod.rs` (grep results were truncated in this session), so I cannot confirm with certainty how `detect_fraud` consumes `Report::fraud_detected()` beyond the report's own claim that it "always returns `Ok(false)` whenever pipeline is `Some`." However, the core mechanism verified directly in `fraud_check.rs` — that fraud checking is entirely and permanently disabled via `N_FRAUD_CHECKS = 0`, and that `FraudChecks::run` ignores the pipeline's contents — is confirmed in the code and is sufficient on its own to establish that no fraud signal can ever flow from the biometric pipeline into a rejection decision through this component.

### Impact Explanation
Because fraud detection is a no-op by construction, any signup that reaches this stage (i.e., `biometric_pipeline` returns `Some(pipeline)`, meaning the capture pipeline did not hard-fail) is fraud-cleared regardless of underlying biometric evidence like occlusion, contact lenses, or fraud-classifier failures. This matches the "liveness/fraud bypass" impact category: a fraudulent or non-live capture can obtain a validly Orb-signed custody package (PCP), undermining the core anti-spoofing/anti-fraud guarantee of the signup pipeline.

### Likelihood Explanation
The precondition is that `biometric_pipeline` produces `Some(pipeline)` (i.e., does not hard-fail on its own independent of fraud_check.rs). Given `FraudChecks` never inspects pipeline content, any signup session that clears the biometric pipeline's own gating is unconditionally fraud-cleared by this component 100% of the time — this is deterministic and does not depend on race conditions, timing, or privileged access. It is fully reachable by an unprivileged attacker running a normal signup session.

### Recommendation
Re-enable actual fraud checks in `FraudChecks::run` and increase `N_FRAUD_CHECKS` to reflect real check count, ensuring `fraud_checks()` inspects the actual `biometric_pipeline::Pipeline` fields (occlusion, contact lens, face-identifier fraud, motion blur, etc.) and produces `Some(bool)` per check. Ensure `fraud_checks_strict()`'s fail-closed semantics (`unwrap_or(true)`) are exercised against non-empty, populated check results, not a compile-time-empty array.

### Proof of Concept
Unit test (`fraud-check.rs`):
```rust
#[test]
fn fraud_detected_is_always_false_regardless_of_input() {
    let report = Report {};
    assert!(!report.fraud_detected());
}
```
This demonstrates `fraud_detected()` is invariant to any input because `N_FRAUD_CHECKS == 0`.

Integration test plan (requires access to `biometric_pipeline::Pipeline` construction, not fully verifiable in this session):
1. Construct a `Pipeline` with an occlusion result of `Err(...)` or a `face_identifier_fraud_checks` field set to `Err(...)`.
2. Call `FraudChecks::new(&pipeline).run()`.
3. Assert the resulting `Report::fraud_detected()` still returns `false`.
4. Trace through `detect_fraud` in `src/plans/mod.rs` (not fully retrieved in this session — should be independently verified) to confirm it returns `Ok(false)`, leading to `SignupReason::Normal`, `enroll_user`, `build_pcp`, and `secure_element::sign` succeeding despite the failing biometric signal.

### Citations

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
```

**File:** src/plans/fraud_check.rs (L64-78)
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
