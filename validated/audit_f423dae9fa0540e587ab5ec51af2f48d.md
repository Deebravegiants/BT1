### Title
Missing cross-frame identity continuity check allows binding two different physical subjects' irises/face into a single `Capture` - ([File: src/plans/biometric_capture/mod.rs])

### Summary
`biometric_capture::Plan` fills `left_ir`, `right_ir`, `left_rgb`, `right_rgb`, and `self_custody_candidate_rgb` independently, gated only by per-frame `estimate.score >= IRIS_SCORE_MIN` and a time-based `valid_capture_after` cooldown. There is no check anywhere in the capture state machine, `into_capture`, `is_success`, or the downstream `detect_fraud` stub that the frames populating these slots originate from the same physical person.

### Finding Description
`Plan::handle_ir_net` and `Plan::handle_rgb_net` write into `left_ir`/`right_ir`/`left_rgb`/`right_rgb` purely based on `target_left_eye` (which objective is currently active) and per-frame quality thresholds [1](#0-0) , [2](#0-1) . `handle_face_identifier` independently overwrites `self_custody_candidate_rgb` whenever a higher-scoring valid face frame is seen [3](#0-2) . Objectives simply alternate `target_left_eye` and there is a `delay_between_eye_captures` cooldown between sides [4](#0-3) , [5](#0-4) , giving an attacker a window to change the presented subject/eye between objectives within the same ~45s capture session.

`into_capture` and `is_success` only check presence of the five slots, with no embedding/identity comparison across `eye_left`, `eye_right`, and `face_self_custody_candidate` [6](#0-5) , [7](#0-6) . Downstream, `detect_fraud` in this codebase is a no-op stub that always returns `false`, and the fraud-checks module explicitly documents `N_FRAUD_CHECKS: usize = 0` with the comment "FOSS: WE HAVE DELETED ALL FRAUD CHECKS" [8](#0-7) , [9](#0-8) . The `face_identifier` pipeline computes embeddings/fraud checks per frame but they are consumed through this stubbed engine, so no cross-identity/continuity signal (e.g., "multiple faces", face-vs-iris identity consistency) is enforced in this repository's reachable code path.

### Impact Explanation
If exploitable end-to-end, this would let an attacker bind left/right iris data (and a face image) from two different physical subjects into a single `Capture`/PCP tied to one `user_id`, corrupting the biometric record uploaded via `enroll_user`/`personal_custody_package` for that signup. This matches "wrong-identity binding" impact category.

### Likelihood Explanation
The precondition requires physically manipulating the scene presented to the Orb's cameras during the objective window and knowing the internal eye-alternation/objective timing, which is attacker-controllable per the threat model (own signup session, scene control). However, this repository's fraud/liveness enforcement (multi-face detection, spoof/contact-lens/liveness checks referenced by `contact_lens_model_config`) is a deliberately stripped FOSS artifact (`N_FRAUD_CHECKS = 0`, explicit "we manually deleted all fraud checks" comment) rather than a logic bug introduced by this code. The capture-phase slot-assignment gap itself is real and reproducible in this repo, but whether it is independently exploitable in Worldcoin's production system depends on fraud/liveness/uniqueness enforcement that lives outside this redacted FOSS build and cannot be validated here.

### Recommendation
Add an explicit same-subject continuity check in `biometric_capture::Plan` (or in `biometric_pipeline`) that compares face-identifier embeddings/eye crops captured during the left-eye objective against those captured during the right-eye objective (and the self-custody candidate) before accepting the `Capture` as valid, rejecting or restarting the signup if they diverge beyond a similarity threshold.

### Proof of Concept
Integration test plan: drive `Plan::handle_ir_net`/`handle_rgb_net`/`handle_face_identifier` with synthetic `EstimateOutput`/frames representing "subject A" during the left-eye objective and "subject B" during the right-eye objective, both scoring above `IRIS_SCORE_MIN`; call `run_post` → `into_capture`; assert that `is_success()` returns `true` and a `Capture` is produced even though `eye_left` and `eye_right` (and `face_self_custody_candidate`) are tagged as originating from different synthetic identities, demonstrating the absence of a same-subject continuity assertion in `into_capture`/`is_success` [6](#0-5) .

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

**File:** src/plans/biometric_capture/mod.rs (L276-286)
```rust
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
```

**File:** src/plans/biometric_capture/mod.rs (L301-317)
```rust
            if output.is_valid.map_or(false, |v| v) {
                let highest = self
                    .self_custody_candidate_rgb
                    .as_ref()
                    .map_or(0.0, |p| p.estimate.score.unwrap_or_default());
                if output.score.is_some_and(|s| s > highest) {
                    tracing::info!(
                        "New face self-custody frame captured with score: {:?}",
                        output.score
                    );
                    self.self_custody_candidate_rgb = Some(FrameInfoSelfCustodyCandidate::new(
                        output,
                        frame.expect("frame must be set for FaceIdentifier::IsValidImage"),
                    ));
                    self.face_ir = self.last_face_ir.take();
                    self.thermal = self.last_thermal.take();
                }
```

**File:** src/plans/biometric_capture/mod.rs (L392-404)
```rust
        for (target_left_eye, only_rgb_net_frames) in
            [(target_left_eye, true), (!target_left_eye, false)]
        {
            for &(ir_led_wavelength, ir_led_duration) in wavelengths {
                objectives.push_back(Objective {
                    target_left_eye,
                    ir_led_wavelength,
                    ir_led_duration,
                    only_rgb_net_frames,
                });
            }
        }
        let total_objectives = objectives.len();
```

**File:** src/plans/biometric_capture/mod.rs (L499-500)
```rust
        self.valid_capture_after = Instant::now() + self.delay_between_eye_captures;
        Ok(false)
```

**File:** src/plans/biometric_capture/mod.rs (L557-600)
```rust
    fn into_capture(self) -> Option<Capture> {
        let FrameInfoIr { estimate: left_ir_net_estimate, frame: left_ir_frame, .. } =
            self.left_ir?;
        let FrameInfoRgb { estimate: left_rgb_net_estimate, frame: left_rgb_frame, .. } =
            self.left_rgb?;
        let FrameInfoIr { estimate: right_ir_net_estimate, frame: right_ir_frame, .. } =
            self.right_ir?;
        let FrameInfoRgb { estimate: right_rgb_net_estimate, frame: right_rgb_frame, .. } =
            self.right_rgb?;
        let FrameInfoSelfCustodyCandidate {
            estimate: face_identifier_output,
            frame: self_custody_candidate_rgb_frame,
            ..
        } = self.self_custody_candidate_rgb?;
        let eye_left = EyeCapture {
            ir_frame: left_ir_frame,
            ir_frame_940nm: None,
            ir_frame_740nm: None,
            ir_net_estimate: left_ir_net_estimate,
            rgb_frame: left_rgb_frame,
            rgb_net_estimate: left_rgb_net_estimate,
        };
        let eye_right = EyeCapture {
            ir_frame: right_ir_frame,
            ir_frame_940nm: None,
            ir_frame_740nm: None,
            ir_net_estimate: right_ir_net_estimate,
            rgb_frame: right_rgb_frame,
            rgb_net_estimate: right_rgb_net_estimate,
        };
        Some(Capture {
            eye_left,
            eye_right,
            face_ir: self.face_ir,
            thermal: self.thermal,
            latitude: self.latitude,
            longitude: self.longitude,
            face_self_custody_candidate: SelfCustodyCandidate {
                rgb_frame: self_custody_candidate_rgb_frame,
                rgb_net_eye_landmarks: face_identifier_output.rgb_net_eye_landmarks,
                rgb_net_bbox: face_identifier_output.rgb_net_bbox,
            },
        })
    }
```

**File:** src/plans/biometric_capture/mod.rs (L731-737)
```rust
    fn is_success(&self) -> bool {
        self.left_ir.is_some()
            && self.right_ir.is_some()
            && self.left_rgb.is_some()
            && self.right_rgb.is_some()
            && self.self_custody_candidate_rgb.is_some()
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

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
```
