I found the strongest analog: the biometric capture pipeline latches a single "sharpest frame" (`left_ir`/`right_ir` slot) the instant a frame crosses the `IRIS_SCORE_MIN` threshold, without any requirement that validity persist or be re-checked at the time the frame is actually used for enrollment. This mirrors the flashloan bug's core defect: a transient crossing of a threshold check gets latched into persistent state that is later relied upon without revalidation.

### Title
Biometric capture latches a transient threshold-crossing IR frame as the permanent enrollment sample without revalidation - (File: `src/plans/biometric_capture/mod.rs`)

### Summary
`Plan::handle_ir_net` in `src/plans/biometric_capture/mod.rs` computes `valid_capture` from a single momentary `estimate.score >= IRIS_SCORE_MIN` check and, once true, unconditionally overwrites the `left_ir`/`right_ir` slot with that one frame [1](#0-0) . There is no requirement that the passing condition be sustained, debounced, or re-validated before the frame is locked in as the sample that flows into `biometric_pipeline` and ultimately `enroll_user`. This is structurally the same class of bug as the Curve report: a boolean/threshold gate is evaluated once on a momentarily-manipulable signal, and the resulting state (here, "this is the enrollment frame") persists and is consumed later without re-checking that the condition still holds.

### Finding Description
The relevant threshold constants are `IRIS_SCORE_MIN` (`1.70`) and `IRIS_BRIGHTNESS_RANGE` [2](#0-1) . `valid_capture` is computed per IR-Net estimate output as:
```
let valid_capture = estimate.score >= IRIS_SCORE_MIN
    && (!orb.ir_auto_exposure.is_enabled() || IRIS_BRIGHTNESS_RANGE.contains(&frame.mean()))
    && self.valid_capture_after <= Instant::now();
``` [3](#0-2) 
As soon as this fires once, the corresponding `left_ir`/`right_ir` slot is replaced with that single `FrameInfoIr` (score + frame), and it stays there as the candidate sample for that eye for the remainder of the capture loop unless a later frame also crosses the threshold and overwrites it again [4](#0-3) . The `score` itself is computed by `calculate_selection_score`, which is a simple deterministic function of `sharpness`, `valid_for_identification`, and `status` [5](#0-4) . Nothing downstream re-verifies that the eye/iris presented at the moment the frame was captured is the same one still present at the physical sensor when the pipeline (`biometric_pipeline::Plan`) later consumes `capture.eye_left`/`capture.eye_right` to compute the iris code that is submitted for enrollment [6](#0-5) . The only mitigating checks are the perceived-side match and, separately, the occlusion hysteresis in `update_occlusion`, but neither of these constitutes a re-validation of "is this still a legitimately captured live human iris" for the specific latched frame at consumption time — they only gate UI/side-selection at the moment the frame arrived [7](#0-6) .

Compounding the effect: this build has all backend/orb-side biometric fraud checks explicitly deleted — `N_FRAUD_CHECKS = 0` and `detect_fraud` always returns `Ok(false)` — so there is no secondary layer that would catch a spoofed or substituted iris sample after the momentary threshold-crossing latch [8](#0-7) [9](#0-8) .

### Impact Explanation
If an attacker can produce a single frame that momentarily satisfies `score >= IRIS_SCORE_MIN` and the brightness range (e.g., a fleeting reflection, a printed/replayed iris image, or exploiting IR-Net's per-frame scoring noise) that frame is irrevocably latched as *the* enrollment sample for that eye, and the underlying live-capture assumption is never re-checked before it is signed and submitted via `enroll_user`/`signup_post::request`. Combined with `N_FRAUD_CHECKS = 0`, a momentary, non-representative capture event becomes the permanent biometric record for a World ID signup, which can misattribute identity/enrollment to fraudulent biometric material.

### Likelihood Explanation
This requires only unprivileged, physical-proximity access to the Orb during a normal signup attempt (no operator/hardware backdoor, no malicious peer) — exactly the "unprivileged user" analog class requested. The threshold-latch-without-revalidation pattern is identical in structure to the confirmed Curve finding (momentary crossing of a defined numeric threshold causing a state transition that is not re-verified before being relied upon), making it a reasonable analog rather than a stretch.

### Recommendation
Require the `valid_capture` condition to be sustained over a minimum debounce window (similar to the existing `OCCLUSION_INDICATOR_MIN_TIME_INTERVAL` hysteresis pattern already used for occlusion) before latching a frame into `left_ir`/`right_ir`, and/or re-validate the final latched frame's score/brightness/liveness signals immediately before it is handed to `biometric_pipeline`/`enroll_user`, rather than trusting a single momentary crossing event.

### Proof of Concept
1. During biometric capture, present a target eye such that at least one IR frame instantaneously satisfies `estimate.score >= IRIS_SCORE_MIN` and `IRIS_BRIGHTNESS_RANGE.contains(&frame.mean())` — this can be a very brief glare/alignment artifact rather than a stable genuine capture.
2. `handle_ir_net` immediately sets `self.left_ir` (or `right_ir`) to this single frame (`src/plans/biometric_capture/mod.rs:244-259`).
3. Immediately obstruct/replace the presented eye (e.g., swap to a different subject or artifact) for the rest of the capture window; because no further sustained re-validation of the latched slot occurs, if no better-scoring frame later overwrites the slot, this momentary frame survives to `run_post`/`Capture` and flows into `biometric_pipeline::Plan::new` and `enroll_user::Plan::run` unchanged [10](#0-9) .
4. With `detect_fraud` hardcoded to `Ok(false)` in this build, no fraud check exists to catch the discrepancy before the enrollment request is signed and submitted [11](#0-10) .

### Citations

**File:** src/plans/biometric_capture/mod.rs (L238-259)
```rust
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

**File:** src/plans/biometric_capture/mod.rs (L666-690)
```rust
    // TODO: include the occlusion 90 and make it request the threshold occlusion from the python directly
    fn update_occlusion(&mut self, orb: &mut Orb, estimate: &EstimateOutput) {
        let dt = self.occlusion_center_led_timer.get_dt().unwrap_or(0.0);
        let EstimateOutput { mut occlusion_30, sharpness, .. } = *estimate;
        if occlusion_30.is_nan() || sharpness.is_nan() || sharpness < IRIS_SHARPNESS_MIN {
            occlusion_30 = THRESHOLD_OCCLUSION_30 * 1.05;
        }
        let occlusion_30_low_pass =
            self.occlusion_30_filter.add(occlusion_30, dt, OCCLUSION_CENTER_LED_LOW_PASS_FILTER_RC);
        // Apply hysteresis and a minimum pulse time.
        let occlusion_detected =
            if let Some(occlusion_indicator_on_time) = self.occlusion_indicator_on_time {
                occlusion_30_low_pass < THRESHOLD_OCCLUSION_30 * 1.025
                    || occlusion_indicator_on_time.elapsed() < OCCLUSION_INDICATOR_MIN_TIME_INTERVAL
            } else {
                occlusion_30_low_pass < THRESHOLD_OCCLUSION_30 * 0.975
            };
        if occlusion_detected {
            self.occlusion_indicator_on_time.get_or_insert_with(Instant::now);
            orb.ui.biometric_capture_occlusion(true);
        } else {
            orb.ui.biometric_capture_occlusion(false);
            self.occlusion_indicator_on_time = None;
        }
    }
```

**File:** src/consts.rs (L221-230)
```rust
/// Minimum iris sharpness score to initiate scan.
pub const IRIS_SHARPNESS_MIN: f64 = 1.00; // TODO: put back 0.68

/// Minimum iris sharpness score for sign up.
pub const IRIS_SCORE_MIN: f64 = 1.70; // TODO: put back 0.68

/// Mean brightness range for sign up. Note: This is also handled by IRNet,
/// which doesn't currently provide a sharpness score for images unless they
/// have an in-range brightness.
pub const IRIS_BRIGHTNESS_RANGE: RangeInclusive<u8> = 80..=180;
```

**File:** src/agents/python/ir_net.rs (L305-308)
```rust
#[cfg(not(feature = "integration_testing"))]
fn calculate_selection_score(sharpness: f64, valid_for_identification: bool, status: i64) -> f64 {
    if status != 0 || !valid_for_identification || sharpness.is_nan() { -1.0 } else { sharpness }
}
```

**File:** src/plans/biometric_pipeline/mod.rs (L228-269)
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
            eye_landmarks_left: capture
                .eye_left
                .rgb_net_estimate
                .primary()
                .map(|prediction| (prediction.landmarks.left_eye, prediction.landmarks.right_eye))
                .expect("prediction should be guaranteed by capture phase"),
            eye_landmarks_right: capture
                .eye_right
                .rgb_net_estimate
                .primary()
                .map(|prediction| (prediction.landmarks.left_eye, prediction.landmarks.right_eye))
                .expect("prediction should be guaranteed by capture phase"),
            eye_landmarks_self_custody_candidate: capture
                .face_self_custody_candidate
                .rgb_net_eye_landmarks,
        })
    }
```

**File:** src/plans/fraud_check.rs (L10-12)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;
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
