### Title
Biometric capture accepts frame sequences with no session-unique liveness challenge, allowing recorded/replayed biometrics to pass as live capture - (File: `src/plans/biometric_capture/mod.rs`)

### Summary
`Plan` in `src/plans/biometric_capture/mod.rs` accepts IR/RGB frames purely based on static, content-only heuristics (sharpness score, brightness range, occlusion low-pass filter, bounding-box correctness) with no session-unique, unpredictable stimulus that a pre-recorded frame sequence could not anticipate. Combined with the fact that the only "liveness"-style gate, `face_identifier::is_valid`, is a stubbed FOSS implementation that unconditionally returns `is_valid: Some(true)`, `score: Some(1.0)`, a replayed/recorded sequence timed to satisfy the sharpness/brightness/occlusion thresholds is accepted as a live capture.

### Finding Description
`Plan::handle_ir_net` accepts a frame into `left_ir`/`right_ir` when `estimate.score >= IRIS_SCORE_MIN`, the IR mean is in `IRIS_BRIGHTNESS_RANGE`, and `self.valid_capture_after <= Instant::now()` [1](#0-0) . `Plan::handle_rgb_net` accepts a frame purely if the estimated bbox `is_correct()` [2](#0-1) . None of these checks embed a per-session random/unpredictable value (e.g., a challenge pattern, timing nonce, randomized LED sequence the frames must respond to) — they are all static, content-only quality/geometry thresholds that a suitably prepared recording, screen playback, or pre-rendered IR video timed to the objective's wavelength/duration schedule could satisfy.

The `target_left_eye` boolean is randomized per-Plan (`let target_left_eye: bool = random();`) [3](#0-2) , but this only controls which eye is scanned first; it is not a stimulus the presented scene must react to and is not bound into any accepted-frame's provenance.

The one place that could function as an anti-spoof gate — `face_identifier::Environment::is_valid`, used to select the self-custody RGB candidate in `Plan::handle_face_identifier` — is a stub in this FOSS build that always returns `is_valid: Some(true), score: Some(1.0)` regardless of input [4](#0-3) . Downstream, `Plan::detect_fraud` in `src/plans/mod.rs` is explicitly emptied out: `// FOSS: WE HAVE DELETED ALL FRAUD CHECKS` followed by `Ok(false)` [5](#0-4) , and `fraud_check::Report`'s check arrays (`DATADOG_TAGS`, `fraud_checks()`, `enabled_checks_from_config()`, `feedback_messages()`) are all hard-coded empty (`N_FRAUD_CHECKS` implied 0) [6](#0-5) . So no software-side liveness/fraud verification exists downstream of `Plan` either, once a capture is produced.

### Impact Explanation
If an attacker can present a pre-recorded/replayed sequence (photo, screen playback, or recorded IR/RGB stream of a victim) to the Orb's cameras in a way that satisfies sharpness, brightness range, occlusion, and bbox thresholds for both eyes and the self-custody candidate, `Plan::is_success` will be true and a `Capture` bound to the victim's biometrics is produced and carried into enrollment (`enroll_user::Plan`) with the attacker's own QR-code/session, yielding signup completion using another person's recorded biometrics. This matches the Immunefi impact category "Signup completed using another person's recorded biometrics."

### Likelihood Explanation
This applies to an unprivileged attacker's own signup session and only requires control over "the scene shown to the cameras," which is explicitly in-scope per the rules. Feasibility depends on defeating the ML-based sharpness/occlusion/quality checks with playback material — a nontrivial but plausible attack surface for high-resolution eye recordings/prosthetics, especially since (in this codebase) the only content-based anti-spoof gate (`face_identifier::is_valid`) is stubbed to always pass, and all downstream fraud checks are empty. There is no session-bound cryptographic or physical challenge that would categorically block this regardless of playback quality.

### Recommendation
Introduce a per-session, unpredictable liveness challenge that the presented subject must react to in a way a static recording cannot anticipate (e.g., randomized LED/IR wavelength or intensity sequence with pupil-response verification, randomized gaze/mirror-sweep target requiring dynamic tracking, or a challenge embedded in captured frame metadata/timing that is verified before `into_capture()` is allowed to succeed). Bind the accepted `Capture` cryptographically/temporally to the specific challenge issued for that `Plan` instance so a captured/replayed sequence from a different session cannot be reused. Restore/implement real fraud and liveness checks in `Plan::detect_fraud` and `face_identifier::is_valid` rather than the current stubs.

### Proof of Concept
Integration test outline (to be run against `biometric_capture::Plan`):
1. Instantiate `Plan::new` with a fixed wavelength list and no signup extension.
2. Feed a pre-recorded, looped/stitched frame sequence (captured once from a legitimate subject, or synthetic frames meeting `IRIS_SCORE_MIN`, `IRIS_BRIGHTNESS_RANGE`, and RGB bbox `is_correct()`) through `handle_ir_net`/`handle_rgb_net`/`handle_face_identifier` twice, in two separate `Plan` instances (simulating a live session and a later replay of the exact same recorded sequence with no per-session variation).
3. Assert that both `Plan` instances complete with `is_success() == true` and produce a `Capture`, i.e., there is no check that rejects the second (replayed) session despite it containing byte-identical/timed-replayed frame data with no session-unique challenge response.
4. Expected (failing) assertion for a fixed implementation: the second `run_check`/`into_capture` call should fail freshness/liveness validation and return `None`, which the current code does not do.

### Citations

**File:** src/plans/biometric_capture/mod.rs (L239-259)
```rust
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

**File:** src/plans/biometric_capture/mod.rs (L390-390)
```rust
        let target_left_eye: bool = random();
```

**File:** src/agents/python/face_identifier/mod.rs (L265-282)
```rust
    /// Check if the RGB face image meets our quality standards.
    #[allow(unused_variables)]
    pub fn is_valid(
        &self,
        py: Python,
        frame: Array3<u8>,
        rgb_net_eye_landmarks: (rgb_net::Point, rgb_net::Point),
        rgb_net_bbox: rgb_net::Rectangle,
    ) -> Result<IsValidOutput> {
        Ok(IsValidOutput {
            error: None,
            inference_backend: Some("orb-core-base".into()),
            is_valid: Some(true),
            score: Some(1.0),
            rgb_net_eye_landmarks,
            rgb_net_bbox,
        })
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
