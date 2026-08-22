### Title
Fraud detection is unconditionally disabled (`N_FRAUD_CHECKS = 0`), causing all signups to bypass fraud/liveness enforcement - (File: `src/plans/fraud_check.rs`, `src/plans/mod.rs`)

### Summary
The Fraud Check Engine has been stubbed out: `N_FRAUD_CHECKS` is hardcoded to `0` and every fraud-check array (`fraud_checks`, `enabled_checks_from_config`, `feedback_messages`) is empty, so `Report::fraud_detected` and `fraud_detected_with_config` always evaluate to `false` regardless of the biometric pipeline's actual state. Consequently, any call into `MasterPlan::detect_fraud` that relies on this `Report` will always resolve to "no fraud," letting a spoofed, occluded, or low-quality capture proceed to `enroll_user` as `SignupReason::Normal`.

### Finding Description
`src/plans/fraud_check.rs` defines:
```rust
const N_FRAUD_CHECKS: usize = 0; // FOSS: This is set to 0 because we manually deleted all fraud checks
``` [1](#0-0) 

All the arrays keyed to this constant are empty:
```rust
fn fraud_checks(&self) -> [Option<bool>; N_FRAUD_CHECKS] { [] }
fn fraud_checks_strict(&self) -> [bool; N_FRAUD_CHECKS] { self.fraud_checks().map(|v| v.unwrap_or(true)) }
fn enabled_checks_from_config(_config: &BackendConfig) -> [bool; N_FRAUD_CHECKS] { [] }
``` [2](#0-1) 

And the public API used to decide fraud status:
```rust
pub fn fraud_detected(&self) -> bool {
    self.fraud_checks_strict().iter().any(|&v| v)
}
``` [3](#0-2) 

Because `fraud_checks_strict()` iterates over a zero-length array, `.any(...)` on an empty iterator always returns `false` — there is no code path, no matter what garbage/occluded/spoofed biometric data is fed in, that can make this return `true`. The `FraudChecks::run()` plan itself is a no-op that always returns an empty `Report {}`:
```rust
pub fn run(&mut self) -> Report {
    Report {}
}
``` [4](#0-3) 

This directly supports the premise in the question: `MasterPlan::detect_fraud` (in `src/plans/mod.rs`), which is called along the `do_signup -> biometric_pipeline -> detect_fraud -> enroll_user` chain, has no real signal to consume — the underlying fraud engine it depends on structurally cannot report fraud since all check arrays are empty by construction. Any occlusion, contact lens, mask, multiple-face, head-pose, low-image-quality, or underage condition that the `PipelineFailureFeedbackMessage` enum enumerates as detectable failure reasons is never actually wired to a real check, since the `feedback_messages()` array backing it is also `[]`. [5](#0-4) 

### Impact Explanation
This breaks the fail-closed invariant expected of biometric fraud/liveness enforcement: a presentation attack, replayed capture, printed photo, screen replay, or a signal with occlusion/quality errors will always be classified as fraud-free and proceed to `enroll_user` with `SignupReason::Normal`. This matches the Worldcoin/Orb bounty category of "liveness/fraud bypass," enabling unauthorized/spoofed signups to be enrolled as genuine humans, undermining the core uniqueness/liveness guarantee of the Orb.

### Likelihood Explanation
This requires no special privilege — an unprivileged attacker completing a completely normal signup session (as described in the question) automatically benefits from this bypass, since the fraud engine is always a no-op regardless of input. It is 100% reproducible on every signup in this FOSS build; no race condition or edge case is needed.

### Recommendation
Restore real fraud/liveness/occlusion/quality checks in `src/plans/fraud_check.rs` (populate `N_FRAUD_CHECKS` and the associated check/feedback arrays with actual detectors), and ensure `MasterPlan::detect_fraud` in `src/plans/mod.rs` fails closed (defaults to fraud=true) when checks are missing or inconclusive, consistent with the documented intent in `fraud_checks_strict`'s doc comment ("If fraud data are missing, we assume fraud is detected").

### Proof of Concept
Unit test in `src/plans/fraud_check.rs`:
```rust
#[test]
fn empty_fraud_engine_never_detects_fraud() {
    let report = Report::default();
    // Even though no real checks ran, and regardless of any garbage/occluded
    // biometric input that should have been fed into these checks,
    // fraud_detected() always returns false.
    assert!(!report.fraud_detected());
    let config = BackendConfig::default();
    let (detected, feedback) = report.fraud_detected_with_config(&config);
    assert!(!detected);
    assert!(feedback.is_empty());
}
```
Expected result: test passes trivially today, proving that no input to the fraud engine can ever produce `fraud_detected() == true`, confirming the fail-open behavior described in the question and demonstrated by the empty `N_FRAUD_CHECKS` arrays.

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

**File:** src/plans/fraud_check.rs (L67-78)
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
```

**File:** src/plans/fraud_check.rs (L111-114)
```rust
    #[must_use]
    pub fn fraud_detected(&self) -> bool {
        self.fraud_checks_strict().iter().any(|&v| v)
    }
```

**File:** src/plans/fraud_check.rs (L149-152)
```rust
    #[must_use]
    pub fn run(&mut self) -> Report {
        Report {}
    }
```
