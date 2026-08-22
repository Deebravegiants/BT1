### Title
Distance-in-range status relies on unauthenticated eye-landmark geometry with no independent occlusion/liveness gate - ([File: src/agents/distance.rs])

### Summary
`distance::Agent::run` derives `Status::InRange` purely from `EstimatePredictionOutput::user_distance()`, which is computed from the raw Euclidean distance between `landmarks.left_eye` and `landmarks.right_eye` [1](#0-0) , without ever calling `is_face_detected()` or any occlusion/liveness signal before emitting the status [2](#0-1) . Since near-coincident (but non-NaN) eye coordinates make `iris_distance_in_percent` small, `ALPHA_RGB_CAMERA / iris_distance_in_percent` can be driven to any desired finite value, including one that lands inside `IR_FOCUS_RANGE`, purely from crafted 2D landmark geometry.

### Finding Description
`user_distance()` at [1](#0-0)  computes distance solely from the pixel-space separation between two eye landmark points; there is no check that these landmarks correspond to a genuine, unoccluded face — `is_face_detected()` only checks that the coordinates are not NaN [3](#0-2) , and critically **that function is never called from `distance.rs`**. The consuming loop at [2](#0-1)  takes `rgb_net_estimate.primary()`, maps it directly through `user_distance`, and sets `Status::InRange` if the result falls in `focus_range`, with no gating on face detection, occlusion, or liveness.

Independently, and more significantly, the fraud-check subsystem that is supposed to catch occlusion (`EyesOcclusion`, `FaceOcclusion`, masks, etc.) has been reduced to a no-op in this codebase: `N_FRAUD_CHECKS` is hard-coded to `0` and `fraud_checks()`, `enabled_checks_from_config()`, and `feedback_messages()` all return empty arrays [4](#0-3) . The code comment explicitly states "we manually deleted all fraud checks" for this FOSS build [5](#0-4) . `FraudChecks::run` unconditionally returns an empty `Report {}` [6](#0-5) , so `fraud_detected()`/`fraud_detected_with_config()` can never flag occlusion regardless of what the model observes.

Given this, an attacker presenting a partially occluded face (or print) that produces two distinct, non-NaN eye landmark coordinates at a geometrically-crafted separation can force `user_distance()` into `IR_FOCUS_RANGE`, and the downstream fraud-check layer that would otherwise be expected to reject occlusion has no enabled checks to catch it in this build.

### Impact Explanation
This allows a presentation with degraded/occluded facial signal to be reported as "in range" for biometric capture purposes and to pass through the distance/UI feedback loop (`ui.biometric_capture_distance(true)`), advancing the signup flow toward IR/iris capture despite the RGB signal not representing a genuine, unoccluded live face. Combined with the fact that fraud checks (including `EyesOcclusion`/`FaceOcclusion`) are entirely disabled in this build, this constitutes a liveness/fraud-check bypass reachable purely through the presented scene, matching a "liveness/fraud bypass" bounty category.

### Likelihood Explanation
Feasible without privileged access: the attacker only needs to control the physical/visual scene shown to the RGB camera during their own signup session (e.g., a photo, mask, or partial occlusion engineered so RGB-Net still emits two eye landmark points at a controlled separation). Reproducible: `user_distance()` is a deterministic function of the two eye points, and `focus_range.contains(&user_distance)` in `distance.rs` is the only gate; no other check in this loop constrains face genuineness. However, this component alone only affects a distance/UI status feedback signal, not final biometric acceptance — the broader impact depends on the fact that this repository's fraud-check layer that should independently reject occlusion has been stripped to zero checks in `src/plans/fraud_check.rs`.

### Recommendation
- Gate `Status::InRange` in `distance::Agent::run` on `EstimatePredictionOutput::is_face_detected()` (and ideally a proper occlusion/liveness signal from `agents::python::occlusion`), not solely on the numeric distance falling in range.
- Strengthen `is_face_detected()` to reject geometrically degenerate landmark configurations (e.g., minimum inter-eye distance threshold, bounding-box consistency checks between eyes/nose/mouth), not just NaN checks.
- Restore/enable real fraud checks in `src/plans/fraud_check.rs` (currently `N_FRAUD_CHECKS == 0` with all check arrays empty) so occlusion-based signals (`EyesOcclusion`, `FaceOcclusion`, `Mask`) are enforced independently of the distance estimation pipeline before authorizing capture/signup progression.

### Proof of Concept
Unit test plan for `src/agents/python/rgb_net.rs` / `src/agents/distance.rs`:
1. Construct an `EstimatePredictionLandmarksOutput` with `left_eye = Point { x: 0.50, y: 0.50 }` and `right_eye = Point { x: 0.5001, y: 0.50 }` (near-coincident, non-NaN) and arbitrary valid nose/mouth points.
2. Assert `is_face_detected()` returns `true` (demonstrating the NaN-only check is insufficient).
3. Call `user_distance()` and confirm the returned value can be tuned by varying the tiny delta to land inside `IR_FOCUS_RANGE` from `src/consts.rs`.
4. Feed this `EstimatePredictionOutput` as `rgb_net_estimate.primary()` into `distance::Agent::run`'s input channel and assert that `Status::InRange` is emitted with no corresponding occlusion/liveness confirmation, since `FraudChecks::run` (in `src/plans/fraud_check.rs`) returns an empty `Report` regardless of input, i.e., `Report::fraud_detected()` is always `false`.

Note: I was unable to fully trace how `distance::Status::InRange` output is consumed downstream in `src/plans/biometric_capture/mod.rs` (no direct references to `distance::Status`/`Status::InRange` were found there despite many occlusion-related matches), so the exact downstream authorization consequence of this specific status value could not be fully confirmed from the indexed content; a full-codebase Devin session would be needed to trace the precise capture-authorization wiring.

### Citations

**File:** src/agents/python/rgb_net.rs (L269-276)
```rust
    pub fn user_distance(&self) -> f64 {
        // TODO(valff) this value got old and is no longer precise, should be re-measured
        const ALPHA_RGB_CAMERA: f64 = 40.0;
        let delta_x = (self.landmarks.left_eye.x - self.landmarks.right_eye.x).abs();
        let delta_y = (self.landmarks.left_eye.y - self.landmarks.right_eye.y).abs();
        let iris_distance_in_percent = (delta_x.powi(2) + delta_y.powi(2)).sqrt();
        ALPHA_RGB_CAMERA / iris_distance_in_percent
    }
```

**File:** src/agents/python/rgb_net.rs (L278-285)
```rust
    /// Returns `true` if both eyes are detected.
    #[must_use]
    pub fn is_face_detected(&self) -> bool {
        !self.landmarks.left_eye.x.is_nan()
            && !self.landmarks.left_eye.y.is_nan()
            && !self.landmarks.right_eye.x.is_nan()
            && !self.landmarks.right_eye.y.is_nan()
    }
```

**File:** src/agents/distance.rs (L103-119)
```rust
                        Input::RgbNetEstimate(rgb_net_estimate) => {
                            if rgb_net_first_distance_date.is_none() {
                                rgb_net_first_distance_date = Some(SystemTime::now());
                            }
                            let Some(user_distance) = rgb_net_estimate
                                .primary()
                                .map(python::rgb_net::EstimatePredictionOutput::user_distance)
                            else {
                                continue;
                            };
                            log.user_distance.push(user_distance);
                            status = if focus_range.contains(&user_distance) {
                                focus_range = IR_FOCUS_RANGE;
                                user_came_in_range = true;
                                rgb_net_first_distance_date = Some(SystemTime::now());
                                self.ui.biometric_capture_distance(true);
                                Status::InRange
```

**File:** src/plans/fraud_check.rs (L10-82)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;

/// Convenience wrapper struct for the Fraud Check Engine's configuration coming from the backend.
#[cfg_attr(test, derive(Default))]
#[derive(
    Archive, Serialize, Deserialize, SerdeDeserialize, SerdeSerialize, Debug, Clone, JsonSchema,
)]
#[serde(rename_all = "PascalCase")]
#[allow(clippy::struct_excessive_bools)]
pub struct BackendConfig {}

// Helper function to deserialize a Duration from a u64 representing milliseconds
#[allow(dead_code)]
fn deserialize_duration_from_millis<'de, D>(deserializer: D) -> Result<Duration, D::Error>
where
    D: serde::Deserializer<'de>,
{
    let millis = <u64 as SerdeDeserialize>::deserialize(deserializer)?;
    Ok(Duration::from_millis(millis))
}

/// The results of the fraud checks.
#[allow(clippy::struct_excessive_bools)]
#[derive(Debug, Default, SerdeSerialize, JsonSchema, Clone)]
pub struct Report {}

/// User feedback message types in case of failed pipeline.
/// This is not an exhaustive list of the true failure modes, the true
/// failure modes are more low level. This list doesn't include the actual
/// fraud based failure modes.
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

**File:** src/plans/fraud_check.rs (L148-152)
```rust
    /// Run all fraud checks.
    #[must_use]
    pub fn run(&mut self) -> Report {
        Report {}
    }
```
