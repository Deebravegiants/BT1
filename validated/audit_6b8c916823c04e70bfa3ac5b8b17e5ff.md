### Title
Biometric pipeline accepts captured frames with no liveness/replay-resistance binding, allowing pre-recorded video to be enrolled as a live signup - (File: src/plans/biometric_pipeline/mod.rs)

### Summary
`Plan::new` in `src/plans/biometric_pipeline/mod.rs` builds the biometric pipeline plan purely from the frames/bboxes/landmarks already selected by the capture phase, with no session-unique, unpredictable stimulus or freshness check tying the frames to a live subject. Upstream capture logic (`src/plans/biometric_capture/mod.rs`) only gates frames on perceptual quality (sharpness, distance, occlusion) rather than any challenge a recording could not anticipate, and the only project-level fraud-check hook (`detect_fraud` in `src/plans/mod.rs`) is a stub that unconditionally returns `false`.

### Finding Description
`Plan::new` (`src/plans/biometric_pipeline/mod.rs:228-269`) takes a `&Capture` and copies the `ir_frame`/`rgb_frame` pairs, bounding boxes, and eye landmarks already chosen during capture directly into the pipeline plan, with no validation of freshness, no nonce, and no correlation to an orb-emitted unpredictable stimulus: [1](#0-0) 

Tracing back to where these frames are selected, `handle_ir_net`/`handle_rgb_net` in `src/plans/biometric_capture/mod.rs` accept a frame as "valid" purely based on IR-Net score, brightness range, and elapsed time since capture start — none of which a high-quality recorded video played back at the sensor would fail: [2](#0-1) 

A search of the whole repository for any liveness/challenge/nonce/randomization primitive (`liveness`, `challenge`, `nonce`, `randomiz`) returns no hits outside the audit-instructions file itself, confirming no per-session unpredictable stimulus exists anywhere between capture and pipeline construction. The only other fraud-detection hook in the signup flow, `detect_fraud` in `src/plans/mod.rs`, is explicitly stubbed out: [3](#0-2) 

Because neither the capture-time frame-selection logic nor `biometric_pipeline::Plan::new` nor the downstream fraud-check step introduces any session-bound, unpredictable challenge (e.g., randomized LED/mirror sequence timing that must be echoed back in pupil/reflection response, a random on-screen prompt, etc.), a sufficiently good pre-recorded IR+RGB video of a target person's eyes/face, played back to the sensors during an attacker's own signup session, can satisfy every existing gate (sharpness score, brightness range, distance range, occlusion, landmark detection) and flow straight into `biometric_pipeline::Plan::new` → `run` → `enroll_user`, resulting in enrollment bound to the recorded person's biometrics under the attacker's own signup/QR session.

### Impact Explanation
This allows an unprivileged attacker to complete a valid signup using another person's recorded biometrics (iris code, face bundle) instead of the attacker's own live presence, which is a direct wrong-identity-binding / liveness bypass impact — "Signup completed using another person's recorded biometrics," matching the stated Immunefi impact category.

### Likelihood Explanation
No privileged access, hardware tampering, or key leakage is required — only presenting recorded footage to the orb's cameras during a normal, attacker-initiated signup session, which is squarely within the described attacker capabilities ("the scene shown to the cameras"). Feasibility depends on recording/display quality passing the existing perceptual gates (sharpness/brightness/distance), which is a realistic bar for modern high-resolution playback devices, and the attack is repeatable across sessions since no per-session state prevents reuse of the same recording.

### Recommendation
Introduce a genuine liveness/anti-spoofing binding before frames are accepted into `biometric_pipeline::Plan::new`: e.g., issue a per-session unpredictable stimulus (randomized LED wavelength/intensity sequence or mirror movement pattern) and require the captured IR reflection/pupillary response to correlate with that specific, freshly-generated challenge, rejecting captures that don't exhibit the expected session-unique response. Re-enable and implement real fraud checks in `detect_fraud` rather than leaving it a stub that always returns `false`.

### Proof of Concept
Integration test plan:
1. Construct a `Capture` populated with frames sourced from a pre-recorded/looped IR+RGB sequence (simulating screen/video replay) that satisfies existing thresholds (`IRIS_SCORE_MIN`, `IRIS_BRIGHTNESS_RANGE`, valid bbox/landmarks).
2. Call `biometric_pipeline::Plan::new(&capture, signup_id)` and run the pipeline against mocked agents that just echo the model outputs.
3. Assert the pipeline succeeds and produces a `Pipeline` result (i.e., no freshness/liveness rejection occurs), demonstrating a replayed recording is indistinguishable from a live capture at this stage.
4. As a corroborating check, assert that `detect_fraud` always returns `false` regardless of pipeline content, confirming no downstream fraud gate would catch the replay either.

### Citations

**File:** src/plans/biometric_pipeline/mod.rs (L228-252)
```rust
    pub fn new(capture: &Capture, signup_id: SignupId) -> Result<Self> {
        Ok(Self {
            timeout: Box::pin(time::sleep(MODEL_TIMEOUT)),
            signup_id,
            model_output: None,
            eye_left: capture.eye_left.ir_frame.clone(),
            eye_right: capture.eye_right.ir_frame.clone(),
            face_left: capture.eye_left.rgb_frame.clone(),
            face_right: capture.eye_right.rgb_frame.clone(),
            face_self_custody_candidate: capture.face_self_custody_candidate.rgb_frame.clone(),
            face_bbox_left: capture
                .eye_left
                .rgb_net_estimate
                .primary()
                .expect("prediction should be guaranteed by capture phase")
                .bbox
                .coordinates,
            face_bbox_right: capture
                .eye_right
                .rgb_net_estimate
                .primary()
                .expect("prediction should be guaranteed by capture phase")
                .bbox
                .coordinates,
            face_bbox_self_custody_candidate: capture.face_self_custody_candidate.rgb_net_bbox,
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
