### Title
Unauthenticated identity swap in multi-wavelength IR frames during `AUTO_EXPOSURE_WAIT_TIME` window - (File: src/plans/biometric_capture/multi_wavelength.rs)

### Summary
During `Plan::perform_multi_wavelength`, the `State::ExtraWavelength` branch of `handle_ir_eye_camera` stores whatever raw IR frame arrives after the fixed `AUTO_EXPOSURE_WAIT_TIME` (400ms) sleep, without any of the identity/quality checks (`ir_net` perceived-side check, IRIS_SCORE_MIN, sharpness, occlusion) that gate the primary `left_ir`/`right_ir` capture in `biometric_capture::Plan`. This lets the 940nm/740nm auxiliary frames be captured from a different physical subject than the one whose 850nm iris frame was accepted, yet both are merged unconditionally into the same `EyeCapture` in `Plan::run` (`capture.eye_left.ir_frame_940nm = self.left_940nm`, etc.).

### Finding Description
In the primary capture (`src/plans/biometric_capture/mod.rs`, `handle_ir_net`), a frame is only accepted into `left_ir`/`right_ir` after `ir_net` reports `perceived_side` matching the target eye, `estimate.score >= IRIS_SCORE_MIN`, brightness in range, and sharpness/occlusion filtering (lines 217-267). This is the only mechanism binding "who is captured" to "which frame is stored."

During `perform_multi_wavelength` (`src/plans/biometric_capture/multi_wavelength.rs:139-169`), `orb.disable_ir_net()` is called and the state machine switches to `State::ExtraWavelength`. In this state, `handle_ir_net` and `handle_rgb_net` are both short-circuited to `Ok(BrokerFlow::Continue)` with no processing (lines 86-90, 98-101), and `handle_ir_eye_camera` unconditionally stores `output.value` into `left_940nm`/`right_940nm`/`left_740nm`/`right_740nm` (lines 67-76) — there is no side check, no score check, no liveness/occlusion check, and no re-verification that the subject is the same person as the one who produced `left_ir`/`right_ir`. The only gating condition is a fixed 400ms sleep timer (`AUTO_EXPOSURE_WAIT_TIME`) before the state is exited (`poll_extra`, lines 104-115).

Because eye/gaze tracking (`orb.disable_eye_pid_controller()`) and `ir_net` inference are disabled for this window, the orb has no software means to detect that the presented eye/person changed mid-window. Whatever frame the IR camera reports right at (or slightly after) the 400ms mark is accepted uncritically, then in `Plan::run` (multi_wavelength.rs:129-136) it is merged directly into the `Capture` struct's `eye_left`/`eye_right`, alongside the `ir_frame` that was validated during `Normal` state — with no cross-check that both frames represent the same identity/session.

### Impact Explanation
The concrete impact is scoped strictly to data provenance/binding within a single signup package: the `EyeCapture.ir_frame_940nm`/`ir_frame_740nm` fields can end up containing IR imagery of a person other than the one whose `ir_frame` (validated 850nm iris) and RGB/face-identifier frames were captured and who is being enrolled. Since these auxiliary wavelength frames are bundled into the same `Capture`/signup package that gets uploaded (per `image_notary`/`personal_custody_package` machinery), this is a cross-identity data-binding defect within a signup: fraud/liveness analyses or downstream consumers that assume all frames of a `Capture` belong to one physical person could be fed mismatched-identity IR data. This does not, by itself, forge a valid signup for an unauthorized person or bypass the primary iris-uniqueness/liveness gate (those are governed by `left_ir`/`right_ir` and `self_custody_candidate_rgb`, which remain validated), so the impact is limited to the auxiliary-wavelength data slice.

### Likelihood Explanation
Requires no special access — an unprivileged user completing their own signup session could deliberately step away and let another person's eye be presented in the ~400-1500ms 940nm window and ~200-400ms 740nm window, since none of the automatic checks (`ir_net`, `rgb_net`, eye-tracker/mirror PID) run during that window to detect or reject the swap. It is fully repeatable every signup because the disabling of `ir_net`/`rgb_net`/eye-pid-controller and blind frame storage in `ExtraWavelength` is unconditional plan logic, not a rare race condition.

### Recommendation
Re-enable a lightweight identity/quality check during the `ExtraWavelength` window (e.g., keep `ir_net` active to confirm `perceived_side` and minimal sharpness/occlusion before accepting a 940nm/740nm frame), or compare the accepted extra-wavelength frame against the reference iris frame's pupil/iris geometry before storing it. At minimum, do not disable `orb.disable_eye_pid_controller()`/gaze tracking during this window so gross positional changes can be flagged, and add a post-hoc consistency check in `Plan::run` before merging `left_940nm`/`right_940nm` into `Capture`.

### Proof of Concept
Integration test plan (extending `src/plans/integration_testing.rs` harness used elsewhere for `biometric_capture`):
1. Drive `multi_wavelength::Plan::run` with a synthetic `Orb`/camera feed where the primary 850nm capture window emits IR frames tagged "subject A" satisfying `ir_net` side/score checks, so `left_ir`/`right_ir` get accepted for subject A.
2. During the `AUTO_EXPOSURE_WAIT_TIME` window for `IrLed::L940` (and separately for `L740`), feed IR frames tagged "subject B" (different embedded marker) into `handle_ir_eye_camera`.
3. Run to completion and assert on the resulting `Output.capture`:
   - `capture.eye_left.ir_frame` (subject A marker) is retained.
   - `capture.eye_left.ir_frame_940nm` / `ir_frame_740nm` contain subject B's marker — demonstrating no rejection or identity-consistency enforcement occurred, i.e., `capture.eye_left.ir_frame_940nm` and `capture.eye_left.ir_frame` do not correspond to the same physical capture session, contradicting the implicit invariant that all fields of one `EyeCapture` originate from one subject. [1](#0-0) [2](#0-1) [3](#0-2)

### Citations

**File:** src/plans/biometric_capture/multi_wavelength.rs (L60-78)
```rust
    fn handle_ir_eye_camera(
        &mut self,
        orb: &mut Orb,
        output: port::Output<camera::ir::Sensor>,
    ) -> Result<BrokerFlow> {
        match &self.state {
            State::Normal => self.biometric_capture.handle_ir_eye_camera(orb, output),
            State::ExtraWavelength { target_left_eye, target_740nm, .. } => {
                let slot = match (target_left_eye, target_740nm) {
                    (true, true) => &mut self.left_740nm,
                    (true, false) => &mut self.left_940nm,
                    (false, true) => &mut self.right_740nm,
                    (false, false) => &mut self.right_940nm,
                };
                *slot = Some(output.value);
                Ok(BrokerFlow::Continue)
            }
        }
    }
```

**File:** src/plans/biometric_capture/multi_wavelength.rs (L118-169)
```rust
impl Plan {
    /// Runs the biometric capture plan with multi-wavelength extension.
    pub async fn run(mut self, orb: &mut Orb) -> Result<Output> {
        self.biometric_capture.run_pre(orb).await?;
        loop {
            orb.run(&mut self).await?;
            self.perform_multi_wavelength(orb).await?;
            if self.biometric_capture.run_check(orb).await? {
                break;
            }
        }
        let mut output = self.biometric_capture.run_post(orb, None).await?;
        if let Some(capture) = &mut output.capture {
            capture.eye_left.ir_frame_940nm = self.left_940nm;
            capture.eye_left.ir_frame_740nm = self.left_740nm;
            capture.eye_right.ir_frame_940nm = self.right_940nm;
            capture.eye_right.ir_frame_740nm = self.right_740nm;
        }
        Ok(output)
    }

    async fn perform_multi_wavelength(&mut self, orb: &mut Orb) -> Result<()> {
        orb.disable_ir_net();
        orb.disable_ir_auto_focus();
        orb.disable_eye_pid_controller();

        tracing::info!("Multi-wavelength extension: capturing 940nm");
        orb.set_ir_wavelength(IrLed::L940).await?;
        orb.set_ir_duration(1500)?;
        self.state = State::ExtraWavelength {
            timer: Box::pin(time::sleep(AUTO_EXPOSURE_WAIT_TIME)),
            target_left_eye: self.biometric_capture.target_left_eye,
            target_740nm: false,
        };
        orb.run(self).await?;

        tracing::info!("Multi-wavelength extension: capturing 740nm");
        orb.set_ir_wavelength(IrLed::L740).await?;
        orb.set_ir_duration(200)?;
        self.state = State::ExtraWavelength {
            timer: Box::pin(time::sleep(AUTO_EXPOSURE_WAIT_TIME)),
            target_left_eye: self.biometric_capture.target_left_eye,
            target_740nm: true,
        };
        orb.run(self).await?;

        orb.enable_ir_net().await?;
        orb.enable_ir_auto_focus()?;
        orb.enable_eye_pid_controller()?;
        self.state = State::Normal;
        Ok(())
    }
```

**File:** src/plans/biometric_capture/mod.rs (L217-267)
```rust
    fn handle_ir_net(
        &mut self,
        orb: &mut Orb,
        output: port::Output<ir_net::Model>,
        frame: Option<camera::ir::Frame>,
    ) -> Result<BrokerFlow> {
        match output.value {
            ir_net::Output::Estimate(estimate) => {
                self.update_occlusion(orb, &estimate);
                if let Some(perceived_side) = estimate.perceived_side {
                    if perceived_side != i32::from(!self.target_left_eye) {
                        tracing::debug!("Skipping frame due to target and perceived side mismatch");
                        return Ok(BrokerFlow::Continue);
                    }
                } else {
                    tracing::debug!("IRNet perceived_side=None, skipping frame");
                    return Ok(BrokerFlow::Continue);
                }

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
            }
            ir_net::Output::Version(_) => {}
            ir_net::Output::Error => {
                tracing::error!("IR-Net failed during biometric capture phase");
            }
            ir_net::Output::Warmup => unreachable!("IR-Net::Warmup not part biometric capture"),
        }
        Ok(BrokerFlow::Continue)
```
