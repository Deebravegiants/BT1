### Title
Occlusion-detection results are never transmitted to the backend and are never enforced locally, allowing an occluded/fraudulent capture to be laundered as clean - ([File: src/plans/biometric_pipeline/mod.rs], [File: src/backend/signup_post.rs])

### Summary
`format_pipeline` in `src/backend/signup_post.rs` builds the `CodesV2` struct sent to `/api/v2/signups/{signup_id}` using only `pipeline.v2` (iris code/mask/versions); the `occlusion: Result<occlusion::EstimateOutput, PyError>` field of `Pipeline` is never read by `format_pipeline` or included in the "codes" JSON. Additionally, the only local consumer of the pipeline-stage occlusion result, `detect_fraud` in `src/plans/mod.rs`, has had its fraud logic entirely removed ("FOSS: WE HAVE DELETED ALL FRAUD CHECKS") and unconditionally returns `Ok(false)`.

### Finding Description
`EstimateOutput` from `src/agents/python/occlusion.rs:60-74` carries `occlusion`, `eye_glasses_probability`, `eye_glasses_occlusion`, `face_mask_probability`, `face_mask_occlusion`, and `bbox`. This is computed post-capture as part of `biometric_pipeline::Plan::run` and stored on `Pipeline::occlusion` [1](#0-0) , populated from `mega_agent_one::Output::Occlusion(...)` in the pipeline event loop [2](#0-1) .

Once computed, this value is only:
1. Logged for observability, and its error variant (not the value itself) is recorded on the debug report: [3](#0-2) .
2. Passed into `detect_fraud`, which discards `pipeline` entirely and always returns `Ok(false)` because "WE HAVE DELETED ALL FRAUD CHECKS": [4](#0-3) .

`format_pipeline`, the function that builds the JSON actually POSTed to the backend via `signup_post::request`, only reads `pipeline.v2.eye_left`/`eye_right` (iris code, mask, versions) and never touches `pipeline.occlusion`: [5](#0-4) . The `codes` form field built from this is the only place `pipeline` data reaches the backend request: [6](#0-5) .

A separate, unrelated occlusion signal exists during live capture (`update_occlusion` in `src/plans/biometric_capture/mod.rs`), but that is IR-Net-based, real-time UI-feedback-only (drives an on-Orb light indicator so the user removes an obstruction), and is not connected to the post-capture RGB `occlusion` agent result or to any fraud decision: [7](#0-6) .

Net effect: regardless of what the RGB-based occlusion model detects (glasses, mask, generic occlusion), the value neither gates local signup approval (fraud checks are stubbed out to always pass) nor is conveyed to the backend in the `codes` JSON, so the backend has no way to observe or veto based on this signal for a given `signup_id`.

### Impact Explanation
This matches a fraud/liveness-signal-bypass class of impact: biometric data relevant to fraud/occlusion detection is computed by the Orb but is silently dropped before reaching backend authorization, and the on-device fraud gate that could have compensated for this is intentionally disabled in this codebase (`detect_fraud` always returns `false`). An attacker attempting a signup with an occluded/obstructed presentation (mask, glasses inducing false "clean" iris capture, etc.) cannot be flagged or rejected via this specific channel, either by the Orb or by the backend, because the signal is discarded at both layers.

However, note the important caveat: this is not an attacker-triggered omission — it is unconditional, uniform behavior of the shipped code for every signup, and the fraud-check stub is explicitly labeled as an intentional FOSS-build removal ("FOSS: WE HAVE DELETED ALL FRAUD CHECKS"), not a logic bug reachable only through a crafted attacker input. It is a structural absence of enforcement rather than a bypass of an existing check.

### Likelihood Explanation
The condition is always true — there is no crafted QR code, scene manipulation, or session state needed; it is the default, unconditional behavior of `format_pipeline` and `detect_fraud` for 100% of signups in this build. Reproducibility is total and independent of attacker skill.

### Recommendation
If occlusion-derived signals are meant to be enforceable, either (a) reintroduce real fraud-check logic in `detect_fraud` that consults `pipeline.occlusion` and rejects/flags signups exceeding occlusion thresholds, and/or (b) include occlusion-derived fields in `CodesV2`/`format_pipeline` so the backend can independently audit or gate on them per `signup_id`.

### Proof of Concept
```rust
// tests in src/backend/signup_post.rs
#[test]
fn occlusion_signal_is_dropped_from_codes_json() {
    let mut pipeline = Pipeline::default_with_ok();
    pipeline.occlusion = Ok(occlusion::EstimateOutput {
        occlusion: true,
        eye_glasses_probability: 0.99,
        eye_glasses_occlusion: true,
        face_mask_probability: 0.95,
        face_mask_occlusion: true,
        bbox: Rectangle::default(),
    });

    let codes = format_pipeline(&pipeline);
    let json = serde_json::to_string(&codes).unwrap();

    // Occlusion fields never appear anywhere in the JSON sent to the backend.
    assert!(!json.contains("occlusion"));
    assert!(!json.contains("eye_glasses"));
    assert!(!json.contains("face_mask"));
}
```
Combined with `detect_fraud` always returning `Ok(false)` (`src/plans/mod.rs:1390-1406`), this demonstrates that no occlusion-derived value reaches, or is checkable by, the backend for that `signup_id`, and no local gate exists either.

### Citations

**File:** src/plans/biometric_pipeline/mod.rs (L56-66)
```rust
/// Biometric pipeline output.
#[derive(Clone, Debug)]
pub struct Pipeline {
    /// Pipeline v2 output.
    pub v2: PipelineV2,
    /// Occlusion detection estimate output.
    pub occlusion: Result<occlusion::EstimateOutput, PyError>,
    /// Face identifier model output for the fraud checks.
    pub face_identifier_fraud_checks: Result<face_identifier::FraudChecks, PyError>,
    /// Face identifier model output for the self-custody bundle.
    pub face_identifier_bundle: Result<face_identifier::Bundle, PyError>,
```

**File:** src/plans/biometric_pipeline/mod.rs (L343-349)
```rust
                        mega_agent_one::Output::Occlusion(occlusion::Output::Estimate(output)) => {
                            occlusion = Some(Ok(output));
                            progress += OCCLUSION_PROGRESS;
                        }
                        mega_agent_one::Output::Occlusion(occlusion::Output::Error(error)) => {
                            occlusion = Some(Err(error));
                        }
```

**File:** src/plans/mod.rs (L1358-1359)
```rust
        debug_report.occlusion_error(pipeline.occlusion.clone().err());
        tracing::info!("Occlusion Detection result: {:?}", pipeline.occlusion);
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

**File:** src/backend/signup_post.rs (L122-133)
```rust
    let codes = pipeline.map_or(String::new(), |p| {
        serde_json::to_string_pretty(&format_pipeline(p)).expect("always a valid JSON")
    });
    let mut form = Form::new()
        .text("softwareVersion", &*ORB_OS_VERSION)
        .text("orbId", ORB_ID.as_str())
        .text("distributorId", operator_qr_code.user_id.clone())
        .text("userId", user_qr_code.user_id.clone())
        .text("region", s3_region.to_owned())
        .text("signature", signature.map_or(String::default(), Clone::clone))
        .text("codes", codes)
        .text("reason", signup_reason.to_screaming_snake_case().to_string());
```

**File:** src/backend/signup_post.rs (L163-180)
```rust
/// Serializes pipeline outputs into backend format.
#[must_use]
pub fn format_pipeline(pipeline: &Pipeline) -> Vec<CodesV2> {
    vec![CodesV2 {
        left: format_eye_pipeline(&pipeline.v2.eye_left),
        right: format_eye_pipeline(&pipeline.v2.eye_right),
        ir_net: pipeline.v2.ir_net_version.clone(),
        iris: pipeline.v2.iris_version.clone(),
    }]
}

fn format_eye_pipeline(eye: &EyePipeline) -> Vec<IrisData> {
    vec![IrisData {
        code: eye.iris_code.clone(),
        mask: eye.mask_code.clone(),
        code_version: eye.iris_code_version.clone(),
    }]
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
