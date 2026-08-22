### Title
Biometric capture slots overwrite the previously captured iris/eye frame unconditionally instead of keeping the best-quality one, degrading enrolled biometric data - (File: `src/plans/biometric_capture/mod.rs`)

### Summary
`Plan::handle_ir_net` and `Plan::handle_rgb_net` in the biometric capture state machine store the eye/iris frame that will ultimately be used for enrollment/identification in `self.left_ir`, `self.right_ir`, `self.left_rgb`, and `self.right_rgb`. These slots are meant to hold the best (sharpest/highest-quality) frame captured for each eye, but the code unconditionally replaces the slot on every frame that merely clears the minimum quality threshold, with no comparison against the quality of the frame already stored.

### Finding Description
In `handle_ir_net`, any frame with `estimate.score >= IRIS_SCORE_MIN` (plus brightness/timing checks) immediately overwrites the eye slot regardless of whether it is better than what is already stored: [1](#0-0) 

The same unconditional-overwrite pattern appears in `handle_rgb_net`, where any frame with a correctly-shaped bounding box replaces the stored RGB frame with no quality comparison at all: [2](#0-1) 

This is the same bug class as the reported `syncFeeCheckpoint()` issue: a value that is supposed to be monotonically updated to the *best* observation so far is instead reset unconditionally to the *latest* observation, which can be worse than a previous one. The codebase itself demonstrates the correct pattern immediately below, in `handle_face_identifier`, which explicitly tracks the highest score seen (`highest`) and only replaces the stored self-custody candidate when the new score is strictly greater: [3](#0-2) 

The inconsistency between the two nearby handlers (`handle_ir_net`/`handle_rgb_net` vs `handle_face_identifier`) in the same `impl OrbPlan for Plan` block shows the intended invariant ("keep the best capture") was implemented correctly for the self-custody candidate but omitted for the primary iris/eye capture slots that feed into the final `Capture` struct used for signup: [4](#0-3) 

Because multiple IR-Net/RGB-Net frames can be emitted and processed before the polling loop in `poll_extra` detects both slots are filled and moves on to the next objective, several qualifying frames may arrive in sequence, and only the last one to arrive — not the best one — ends up stored and eventually used downstream: [5](#0-4) 

### Impact Explanation
The `Capture` produced by `into_capture()` — containing the enrolled iris/eye images and estimates — is the biometric data used for signup identity binding and later iris matching. Because the stored per-eye slot is not guaranteed to hold the highest-quality/sharpest frame that satisfied the minimum threshold, borderline-quality iris captures (just above `IRIS_SCORE_MIN`) can silently replace better ones captured earlier in the same objective. This weakens the assurance that the biometric sample enrolled/matched during signup is the best available capture, degrading the effective quality bar used for liveness/fraud-resistant identity binding, even though a stricter "best-of" invariant is clearly intended (as shown by the correct implementation for the self-custody candidate a few lines below).

### Likelihood Explanation
This triggers under normal, unprivileged user operation any time more than one IR or RGB frame clears the minimum quality threshold during a single capture objective — a very common occurrence since capture runs at multiple FPS over the `delay_between_eye_captures` window before the objective completes. No malicious action or special privileges are required.

### Recommendation
Mirror the pattern already used in `handle_face_identifier`: track the best score seen so far for `left_ir`/`right_ir` (and analogously for `left_rgb`/`right_rgb`) and only overwrite the slot when the new estimate's score is strictly greater than the currently stored one, e.g.:
```rust
let current_best = slot.as_ref().map_or(f64::MIN, |f| f.estimate.score);
if estimate.score > current_best {
    *slot = Some(FrameInfoIr::new(estimate, frame));
}
```
apply the equivalent comparison for the RGB slots in `handle_rgb_net`.

### Proof of Concept
1. During a capture objective for the left eye, IR-Net emits an estimate with `score = 0.95` (well above `IRIS_SCORE_MIN`); `handle_ir_net` stores it in `self.left_ir`.
2. Shortly after, a lower quality but still-qualifying frame with `score = 0.71` (still `>= IRIS_SCORE_MIN`) arrives before `poll_extra` detects completion; `handle_ir_net` unconditionally overwrites `self.left_ir` with the worse frame.
3. The objective completes with the degraded 0.71-score frame stored, which becomes part of the final `Capture` returned by `into_capture()` and used for the user's signup/enrollment, even though a sharper 0.95-score frame had already been captured.

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

**File:** src/plans/biometric_capture/mod.rs (L343-371)
```rust
    fn poll_extra(&mut self, orb: &mut Orb, cx: &mut Context<'_>) -> Result<BrokerFlow> {
        while let Poll::Ready(output) = orb.main_mcu.rx_mut().next_broadcast().poll_unpin(cx) {
            if let mcu::main::Output::Gps(message) = output? {
                self.track_gps(message);
            }
        }

        let (rgb, ir) = if self.target_left_eye {
            (&self.left_rgb, &self.left_ir)
        } else {
            (&self.right_rgb, &self.right_ir)
        };

        // TODO: Maybe we can refactor the following into "objectives termination conditions"? When we switch objectives
        // we can call a function to check if we have completed the objective.

        // Check if we have both the iris and the face.
        if let (Some(_rgb), Some(_ir)) = (rgb, ir) {
            if !self.is_last_objective() {
                // We have completed scanning one side. It's ok for us to move forward even if we don't have the
                // self-custody frame, as still have 1 more eye to capture.
                return Ok(BrokerFlow::Break);
            }
            // We are now in the last objective and we have completed scanning both sides. We Just need to make sure
            // we have an self-custody frame before we completely exit the biometric capture phase.
            if self.self_custody_candidate_rgb.is_some() {
                return Ok(BrokerFlow::Break);
            }
        }
```

**File:** src/plans/biometric_capture/mod.rs (L557-586)
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
```
