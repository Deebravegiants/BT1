### Title
Presentation-attack acceptance via geometry/quality-only `Output::Estimate` gating with fraud checks deleted - (File: src/agents/python/rgb_net.rs)

### Summary
`Output::Estimate` in `rgb_net.rs` only carries bounding-box coordinates, landmark points, and a detection `score` — no liveness signal (depth, pupil dynamics, thermal cross-check, texture/3-D analysis) — and the only gate applied to it (`Rectangle::is_correct`, `is_primary`) is a pure geometry/quality check. In this build the downstream fraud-detection stage that would otherwise supply the missing liveness proof is explicitly stubbed out to always pass, so a static, IR-reflectant printed/displayed artifact that satisfies bbox/landmark geometry is accepted as a live subject.

### Finding Description
`Output::Estimate(EstimateOutput)` wraps `EstimatePredictionOutput { bbox, landmarks }` with a `score: f64` and boolean `is_primary` flag <cite repo="AYontt/orb-core--006" path="src/agents/python/rgb_net.rs" start="59="75" /> and its only self-validation helper is `Rectangle::is_correct`, which merely checks the box falls inside `[0.0, 1.0]` [1](#0-0) . None of these fields encode any liveness-specific property (no depth, pupil reflex, texture spectrum, or motion parallax).

`handle_rgb_net` in the biometric-capture plan accepts a frame purely based on `prediction.bbox.coordinates.is_correct()` for the primary prediction, storing the frame as a valid capture candidate with no additional liveness gate: [2](#0-1) .

The IR-Net path (`handle_ir_net`) is similarly gated only by `score >= IRIS_SCORE_MIN` and a brightness range, i.e., signal quality, not liveness: [3](#0-2) .

Crucially, the stage that historically supplied real anti-spoof / liveness enforcement — the fraud-check engine — has been reduced to a no-op in this codebase: `N_FRAUD_CHECKS` is hard-coded to `0` with the comment "FOSS: This is set to 0 because we manually deleted all fraud checks" [4](#0-3) , `Report::fraud_checks()` returns an empty array [5](#0-4) , and `Plan::detect_fraud` in the master signup plan unconditionally returns `Ok(false)` with the comment "FOSS: WE HAVE DELETED ALL FRAUD CHECKS" [6](#0-5) .

As a result, the full accept chain for a captured face/iris — RGB-Net geometry check → IR-Net score/brightness check → (no-op) fraud detection → enrollment — never requires proof that the subject is a live human. An attacker presenting a high-resolution printed photo or IR-matched screen replay of an iris/face, positioned and illuminated to satisfy the bbox/score/brightness thresholds, passes every check `Output` and its consumers enforce.

### Impact Explanation
This allows enrollment or verification of a non-live subject using a static artifact (identity spoofing / presentation attack), matching the Worldcoin/Orb bounty impact category of biometric liveness/fraud bypass leading to unauthorized signup or wrong-identity binding. Because `detect_fraud` always returns `false`, no downstream fraud gate exists to catch this in the current build.

### Likelihood Explanation
High feasibility for an unprivileged attacker: no operator access, tampering, or credentials are needed — only a physical artifact placed in front of the Orb during a self-initiated signup. All required Rectangle/score/brightness thresholds are attainable with commodity print/display and IR-reflectant material, and the check is fully reproducible per capture attempt.

### Recommendation
Reinstate/implement liveness-specific checks (e.g., depth/3-D structure, pupil reflex to IR flash, thermal cross-check, texture/moiré detection) as a hard gate in `handle_rgb_net`/`handle_ir_net` or in a real fraud-check engine, and ensure `detect_fraud` in `src/plans/mod.rs` performs actual checks instead of unconditionally returning `false`. `Output`'s accepted fields should not be treated as sufficient proof of liveness on their own.

### Proof of Concept
Add an integration test that constructs an `rgb_net::EstimateOutput` / `ir_net::EstimateOutput` with plausible bbox/landmark/score/brightness values (as would be produced from a printed-photo replay frame) and feeds it through `biometric_capture::Plan::handle_rgb_net`/`handle_ir_net` followed by `Plan::detect_fraud`, asserting that `detect_fraud` returns `true` (fraud detected) for artifact-derived captures. Currently this assertion fails because `detect_fraud` always returns `Ok(false)` [7](#0-6) , demonstrating the acceptance of a non-live subject.

### Citations

**File:** src/agents/python/rgb_net.rs (L288-294)
```rust
impl Rectangle {
    /// Returns `true` if the coordinates fall in the `[0.0; 1.0]` range.
    #[must_use]
    pub fn is_correct(&self) -> bool {
        self.start_x >= 0.0 && self.end_x <= 1.0 && self.start_y >= 0.0 && self.end_y <= 1.0
    }
}
```

**File:** src/plans/biometric_capture/mod.rs (L238-243)
```rust
                let frame = frame.expect("frame must be set for an estimate output");
                let valid_capture = estimate.score >= IRIS_SCORE_MIN
                    && (!orb.ir_auto_exposure.is_enabled()
                        || IRIS_BRIGHTNESS_RANGE.contains(&frame.mean()))
                    && self.valid_capture_after <= Instant::now();

```

**File:** src/plans/biometric_capture/mod.rs (L270-287)
```rust
    fn handle_rgb_net(
        &mut self,
        _orb: &mut Orb,
        output: port::Output<rgb_net::Model>,
        frame: Option<camera::rgb::Frame>,
    ) -> Result<BrokerFlow> {
        if let rgb_net::Output::Estimate(estimate) = output.value {
            if let Some(prediction) = estimate.primary() {
                if prediction.bbox.coordinates.is_correct() {
                    let frame = frame.expect("frame must be set for an estimate output");
                    let slot =
                        if self.target_left_eye { &mut self.left_rgb } else { &mut self.right_rgb };
                    *slot = Some(FrameInfoRgb::new(estimate, frame));
                }
            }
        }
        Ok(BrokerFlow::Continue)
    }
```

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
```

**File:** src/plans/fraud_check.rs (L64-69)
```rust
impl Report {
    const DATADOG_TAGS: [&'static str; N_FRAUD_CHECKS] = [];

    fn fraud_checks(&self) -> [Option<bool>; N_FRAUD_CHECKS] {
        []
    }
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
