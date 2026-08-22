### Title
Presentation-attack (spoof) acceptance in `handle_rgb_net` due to purely geometric/quality accept criterion, compounded by disabled fraud checks - (File: src/plans/biometric_capture/mod.rs, src/plans/biometric_capture/multi_wavelength.rs)

### Summary
`handle_rgb_net` (delegated to by the `multi_wavelength.rs` extension's `handle_rgb_net`) accepts an RGB-Net frame purely based on bounding-box coordinate validity, with no liveness signal at all. Downstream, the biometric pipeline's fraud-check stage (`detect_fraud` in `src/plans/mod.rs`) has been explicitly stripped ("FOSS: WE HAVE DELETED ALL FRAUD CHECKS"), meaning nothing in the reachable code path independently verifies liveness before enrollment.

### Finding Description
The `multi_wavelength.rs::handle_rgb_net` function is a thin dispatcher: in `State::Normal` it forwards directly to `biometric_capture::Plan::handle_rgb_net`, and in `State::ExtraWavelength` it does nothing (`Ok(BrokerFlow::Continue)`) [1](#0-0) . The actual accept logic lives in `biometric_capture::Plan::handle_rgb_net`:

```
if let rgb_net::Output::Estimate(estimate) = output.value {
    if let Some(prediction) = estimate.primary() {
        if prediction.bbox.coordinates.is_correct() {
            ...
            *slot = Some(FrameInfoRgb::new(estimate, frame));
        }
    }
}
``` [2](#0-1) 

The only gate is `Rectangle::is_correct()`, which merely checks that bbox coordinates fall in `[0.0, 1.0]` [3](#0-2) . `EstimatePredictionOutput` exposes no liveness-related field — only `bbox` (score/coordinates) and 2D `landmarks` (eye/mouth/nose points) used for `user_distance()` and `is_face_detected()` [4](#0-3) [5](#0-4) . None of these properties (bbox position, 2D landmark geometry) require the presented subject to be a live 3D human — a sufficiently sharp printed photo or screen display with correctly proportioned facial geometry, held at the right distance, would satisfy them.

Separately, the IR-Net path (`handle_ir_net`) does gate on `score`, `sharpness`, brightness range, and `perceived_side`, but these are also image-quality/geometry metrics, not liveness proofs (no pupil-response-to-light check is enforced here despite `pupil_contraction.rs` existing as an extension, and multi-wavelength capture at 940nm/740nm records extra frames but does not itself gate acceptance based on reflectance differences) [6](#0-5) .

Crucially, the downstream fraud-detection stage that would normally catch spoofing has been entirely removed: `detect_fraud` in `src/plans/mod.rs` unconditionally returns `Ok(false)` with the comment "FOSS: WE HAVE DELETED ALL FRAUD CHECKS" [7](#0-6) . This means the RGB-Net acceptance in `handle_rgb_net`, combined with IR-Net's quality-only gate, is the only remaining barrier before `enroll_user` is invoked [8](#0-7) .

### Impact Explanation
An attacker presenting a high-resolution printed or displayed face/iris image with matched IR reflectance can pass the `handle_rgb_net` bbox-correctness gate and the IR-Net sharpness/brightness/score gate, since none of these signals require liveness. Combined with the disabled fraud checks, a non-live artifact could proceed through `biometric_capture` → `biometric_pipeline` → `enroll_user`, resulting in enrollment of a non-live subject or identity spoofing — a direct match to the "signup of a non-live/spoofed identity" bounty impact category.

### Likelihood Explanation
Feasibility depends on real-world artifact fidelity (a physical print/display reproducing IR reflectance and geometry closely enough to pass `IRIS_SCORE_MIN`/`IRIS_SHARPNESS_MIN`/brightness-range and RGB bbox thresholds), which is a nontrivial but well-documented category of presentation attack in biometric literature, and repeatable since the criteria are static thresholds with no randomized challenge-response (e.g., no forced blink, no verified pupil constriction gating acceptance, no depth/liveness signal fused into the RGB-Net accept path). The removal of fraud checks (`detect_fraud` always `Ok(false)`) further increases likelihood since it removes what should be the last line of defense.

### Recommendation
Do not rely on `handle_rgb_net`/`handle_ir_net` signal-quality thresholds as a liveness proxy. Reinstate or newly implement genuine fraud/liveness checks in `detect_fraud` (currently stripped to a no-op) — e.g., verified pupil-contraction response, cross-wavelength reflectance ratio checks using the captured 940nm/740nm frames in `multi_wavelength.rs` (currently only stored, never validated), and/or 3D depth consistency — and gate `enroll_user` on those checks succeeding, not merely on frame sharpness/bbox geometry.

### Proof of Concept
Integration test plan:
1. Construct a synthetic `rgb_net::EstimateOutput` with a primary prediction whose `bbox.coordinates` are within `[0,1]` and plausible `landmarks`, derived from a still photo (no motion/liveness signal), and feed it through `biometric_capture::Plan::handle_rgb_net`.
2. Assert that the frame is accepted into `self.left_rgb`/`self.right_rgb` (`slot.is_some()`), demonstrating no liveness rejection occurs.
3. Complete a simulated `biometric_capture::Plan::run` with matching IR-Net estimates crafted with `score >= IRIS_SCORE_MIN`, `sharpness >= IRIS_SHARPNESS_MIN`, and brightness within `IRIS_BRIGHTNESS_RANGE`, all derived from static artifact simulation.
4. Trace through `plans::mod::detect_fraud`, asserting it returns `Ok(false)` unconditionally regardless of pipeline content, confirming no downstream liveness/fraud rejection exists [9](#0-8) .
5. Expected (failing) assertion for a secure system: capture/enrollment should be rejected for the artifact-derived frames; current code allows it to proceed to `enroll_user`.

### Citations

**File:** src/plans/biometric_capture/multi_wavelength.rs (L92-102)
```rust
    fn handle_rgb_net(
        &mut self,
        orb: &mut Orb,
        output: port::Output<rgb_net::Model>,
        frame: Option<camera::rgb::Frame>,
    ) -> Result<BrokerFlow> {
        match &self.state {
            State::Normal => self.biometric_capture.handle_rgb_net(orb, output, frame),
            State::ExtraWavelength { .. } => Ok(BrokerFlow::Continue),
        }
    }
```

**File:** src/plans/biometric_capture/mod.rs (L236-259)
```rust
                self.update_ux(orb, estimate.sharpness);

                let frame = frame.expect("frame must be set for an estimate output");
                let valid_capture = estimate.score >= IRIS_SCORE_MIN
                    && (!orb.ir_auto_exposure.is_enabled()
                        || IRIS_BRIGHTNESS_RANGE.contains(&frame.mean()))
                    && self.valid_capture_after <= Instant::now();

                if valid_capture {
                    let slot =
                        if self.target_left_eye { &mut self.left_ir } else { &mut self.right_ir };
                    if slot.is_none() {
                        dd_incr!(
                            "main.count.signup.during.biometric_capture.\
                             first_side_sharp_iris_detected",
                            &format!(
                                "side:{}",
                                if self.target_left_eye { "left" } else { "right" }
                            )
                        );
                    }
                    tracing::debug!("Found sharp iris: {}", estimate.score);
                    *slot = Some(FrameInfoIr::new(estimate, frame));
                }
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

**File:** src/agents/python/rgb_net.rs (L59-101)
```rust
/// RGB-Net estimate output.
#[derive(Clone, Debug, Default, Archive, Serialize, Deserialize, SerdeSerialize, JsonSchema)]
pub struct EstimateOutput {
    /// Current version number.
    pub rgbnet_version: String,
    /// RGB-Net predictions.
    pub predictions: Vec<EstimatePredictionOutput>,
}

/// RGB-Net estimation for a person in frame.
#[derive(Clone, Debug, Archive, Serialize, Deserialize, SerdeSerialize, JsonSchema)]
pub struct EstimatePredictionOutput {
    /// Bounding box prediction.
    pub bbox: EstimatePredictionBboxOutput,
    /// Landmarks prediction.
    pub landmarks: EstimatePredictionLandmarksOutput,
}

/// RGB-Net bounding box prediction for a person.
#[derive(Clone, Debug, Archive, Serialize, Deserialize, SerdeSerialize, JsonSchema)]
pub struct EstimatePredictionBboxOutput {
    /// Bounding box coordinates.
    pub coordinates: Rectangle,
    /// Whether the prediction is the primary prediction in the prediction set.
    pub is_primary: bool,
    /// Prediction score.
    pub score: f64,
}

/// RGB-Net landmarks prediction for a person.
#[derive(Clone, Debug, Archive, Serialize, Deserialize, SerdeSerialize, JsonSchema)]
pub struct EstimatePredictionLandmarksOutput {
    /// Left eye coordinates.
    pub left_eye: Point,
    /// Left mouth corner coordinates.
    pub left_mouth: Point,
    /// Nose coordinates.
    pub nose: Point,
    /// Right eye coordinates.
    pub right_eye: Point,
    /// Right mouth corner coordinates.
    pub right_mouth: Point,
}
```

**File:** src/agents/python/rgb_net.rs (L266-286)
```rust
impl EstimatePredictionOutput {
    /// Estimates user distance.
    #[must_use]
    pub fn user_distance(&self) -> f64 {
        // TODO(valff) this value got old and is no longer precise, should be re-measured
        const ALPHA_RGB_CAMERA: f64 = 40.0;
        let delta_x = (self.landmarks.left_eye.x - self.landmarks.right_eye.x).abs();
        let delta_y = (self.landmarks.left_eye.y - self.landmarks.right_eye.y).abs();
        let iris_distance_in_percent = (delta_x.powi(2) + delta_y.powi(2)).sqrt();
        ALPHA_RGB_CAMERA / iris_distance_in_percent
    }

    /// Returns `true` if both eyes are detected.
    #[must_use]
    pub fn is_face_detected(&self) -> bool {
        !self.landmarks.left_eye.x.is_nan()
            && !self.landmarks.left_eye.y.is_nan()
            && !self.landmarks.right_eye.x.is_nan()
            && !self.landmarks.right_eye.y.is_nan()
    }
}
```

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

**File:** src/plans/mod.rs (L1408-1435)
```rust
    async fn enroll_user(
        &mut self,
        orb: &mut Orb,
        debug_report: &mut debug_report::Builder,
        capture: &biometric_capture::Capture,
        pipeline: Option<&biometric_pipeline::Pipeline>,
        signup_reason: SignupReason,
    ) -> enroll_user::Status {
        orb.set_phase("User enrollment").await;
        let t = Instant::now();
        let status = Box::pin(
            enroll_user::Plan {
                signup_id: debug_report.signup_id.clone(),
                operator_qr_code: debug_report.operator_qr_code.clone(),
                user_qr_code: debug_report.user_qr_code.clone(),
                s3_region_str: self.s3_region_str.clone(),
                capture,
                pipeline,
                signup_reason,
            }
            .run(orb),
        )
        .await;
        dd_timing!("main.time.signup.user_enrollment", t);

        debug_report.enrollment_status(status.clone());
        status
    }
```
