## Confirmed finding

This is a real gap: this appears to be the FOSS/community build of orb-core where fraud checks have been explicitly stripped (`src/plans/fraud_check.rs:11-12` `N_FRAUD_CHECKS: usize = 0`, and `src/plans/mod.rs:1403` comment `// FOSS: WE HAVE DELETED ALL FRAUD CHECKS`), so `detect_fraud` unconditionally returns `Ok(false)` [1](#0-0) . This is a build/feature-variant characteristic (not an attacker-triggerable code bug) — I flag it but the rules say to reject findings that depend only on config/build variants without exploitable impact reachable from attacker input, so I don't rely on this alone.

Independent of the FOSS fraud-check removal, tracing the actual per-eye occlusion30 handling:

- `THRESHOLD_OCCLUSION_30 = 0.85` [2](#0-1)  is used only inside `biometric_capture::Plan::update_occlusion`, which low-pass filters `occlusion_30` and toggles a UI "occlusion detected" indicator (`orb.ui.biometric_capture_occlusion`) — it does not reject the captured frame or the eye [3](#0-2) .
- The frame that gets selected as `slot` (left/right IR frame going into `biometric_pipeline`) is chosen solely based on `estimate.score >= IRIS_SCORE_MIN`, exposure range, and side match — `occlusion_30` is never part of `valid_capture` [4](#0-3) .
- `biometric_pipeline::Plan::run` computes `iris::EstimateOutput.metadata.occlusion30` (from `iris::types::Metadata`, `src/agents/python/iris/types.rs:84-97`) for each eye independently via `run_iris_left`/`run_iris_right`, and assembles `EyePipeline { iris_code, mask_code, metadata, ... }` for `eye_left`/`eye_right` with **no comparison against `THRESHOLD_OCCLUSION_30` or any cross-eye consistency check** [5](#0-4) [6](#0-5) .
- `plans::mod.rs::biometric_pipeline` (the caller) only logs/reports `metadata` into the debug report; it never inspects `occlusion30` to abort [7](#0-6) .
- `personal_custody_package::Package::make_iris_codes_json`/`make_iris_code_shares_jsons` unconditionally serialize both eyes' iris/mask codes into the PCP; the only guard is that code *shares* must all be `Some` (bails only if entirely missing, not based on quality) [8](#0-7) .
- Even with fraud checks intact (non-FOSS build), `fraud_check::Report` (`fraud-engine/src/report.rs`) is a generic pass-through structure with no occlusion30-specific check wired in this codebase.

So: **there is no code path anywhere between `biometric_capture` and `personal_custody_package` that compares each eye's `metadata.occlusion30` against `THRESHOLD_OCCLUSION_30` (or any threshold) to reject/abort the pipeline.** An attacker who occludes only one eye (e.g., partially covers/squints one eye while presenting the other cleanly) during their own signup session can produce a `Pipeline` with `eye_left.metadata.occlusion30` = poor quality and `eye_right.metadata.occlusion30` = good quality, and the pipeline still assembles and uploads a PCP containing both eyes' iris codes as valid biometric data for that single signup identity.

However, I need to be precise about what "corrupting identity binding" means here: both iris codes still belong to the *same* attacker (their own two eyes), just one degraded. This is a signup **quality/enrollment integrity** issue (one eye's biometric data may be garbage/unreliable, potentially causing false accept/reject on the backend dedup MPC), not a "wrong-identity binding" (i.e., not mixing eyes from two different people, since there's no injection path shown for a second identity's iris data into a single `EyePipeline` slot within this file). The described "mixed-quality PCP" is real, but the impact is degraded biometric integrity/backend matching reliability, not classic identity-binding corruption (no unauthorized signup, no cross-user data leak demonstrated).

### Title
Per-eye `occlusion30` quality is never enforced before assembling/uploading a PCP - ([File: src/plans/biometric_pipeline/mod.rs])

### Summary
`biometric_pipeline::Plan::run` builds `EyePipeline` for `eye_left`/`eye_right` from `iris::EstimateOutput`, but never checks `metadata.occlusion30` against `THRESHOLD_OCCLUSION_30` (defined in `src/consts.rs` but only consumed by a UI hysteresis indicator in `biometric_capture`). `personal_custody_package::Package::build` then unconditionally packages both eyes' iris/mask codes regardless of per-eye occlusion quality, and `detect_fraud` performs no occlusion-based check either.

### Finding Description
An attacker performing their own signup can occlude one eye (e.g. partial eyelid closure, hand, contact artifact) while keeping the other eye clean during the IR capture phase. `biometric_capture::Plan::update_occlusion` only drives a UI hint and never blocks frame selection (`valid_capture` in `handle_ir_net` checks `score`, exposure, and timing only) [4](#0-3) . The captured degraded-eye frame proceeds into `biometric_pipeline::Plan::run`, which independently invokes the iris agent for each eye and stores `metadata.occlusion30` in `EyePipeline.metadata` without any threshold check or cross-eye consistency assertion [5](#0-4) . The resulting `Pipeline` (with one high-quality and one low-quality eye) is returned to `plans::mod.rs::biometric_pipeline`, which only forwards metadata to the debug report [7](#0-6) , then `detect_fraud` (in this FOSS build, hard-coded to no-op) does not intervene [1](#0-0) , and `personal_custody_package::Package::build`/`make_iris_codes_json` packages both eyes' codes unconditionally, gated only on shares being present, not on quality [8](#0-7) .

### Impact Explanation
The impact is degraded biometric enrollment integrity: a mixed-quality PCP (one occluded/low-fidelity iris code, one clean) is signed and uploaded as a single legitimate signup, without any device-side quality gate. This can pollute the backend deduplication/matching system with a low-quality iris code for a real identity, potentially enabling downstream matching failures or fraud around uniqueness checks — a scoped "biometric data quality / signup integrity" impact rather than cross-identity binding corruption or unauthorized signup (no evidence found that a second identity's data can be substituted into the other eye's slot within this file).

### Likelihood Explanation
High feasibility for an unprivileged attacker: occluding one eye during your own IR capture (e.g., squinting, hand near one eye, lens/contact artifact) is trivial to reproduce and requires no privilege escalation, hardware tampering, or backend compromise — only control over the presented scene during your own signup session.

### Recommendation
Add an explicit per-eye quality gate in `biometric_pipeline::Plan::run` (or immediately after, in `plans::mod.rs::biometric_pipeline`) that compares `eye_left.metadata.occlusion30` and `eye_right.metadata.occlusion30` (and ideally `occlusion90`, sharpness, etc.) against `THRESHOLD_OCCLUSION_30`, returning `biometric_pipeline::Error` (or a new `Error::Occlusion` variant) to abort the pipeline — mirroring the intent already expressed by the `THRESHOLD_OCCLUSION_30` constant — before any `EyePipeline`/PCP is produced.

### Proof of Concept
Integration test plan: construct a `Capture` whose `eye_left.ir_frame`/`eye_right.ir_frame` are synthetic frames engineered so the iris agent mock/stub returns `iris::EstimateOutput.metadata.occlusion30 = Some(0.40)` for the left eye and `Some(0.95)` for the right eye (using the existing `iris::extracts.rs` test fixtures as templates for mock outputs). Run `biometric_pipeline::Plan::run` and assert it returns an `Err(biometric_pipeline::Error::Occlusion)` (post-fix) instead of `Ok(Pipeline { .. })`; currently (pre-fix) the test would show `run()` returning `Ok` with `pipeline.v2.eye_left.metadata.occlusion30 == Some(0.40)` and `pipeline.v2.eye_right.metadata.occlusion30 == Some(0.95)`, proving the pipeline proceeds to `personal_custody_package` construction despite the mismatched/degraded eye quality.

### Citations

**File:** src/plans/mod.rs (L1343-1359)
```rust
        debug_report.iris_model_metadata(
            pipeline.v2.eye_left.metadata.clone(),
            pipeline.v2.eye_right.metadata.clone(),
        );
        debug_report.iris_normalized_images(
            pipeline.v2.eye_left.iris_normalized_image.clone(),
            pipeline.v2.eye_right.iris_normalized_image.clone(),
            pipeline.v2.eye_left.iris_normalized_image_resized.clone(),
            pipeline.v2.eye_right.iris_normalized_image_resized.clone(),
        );
        debug_report.mega_agent_one_config(pipeline.mega_agent_one_config.clone());
        debug_report.mega_agent_two_config(pipeline.mega_agent_two_config.clone());
        debug_report.face_identifier_results(pipeline.face_identifier_fraud_checks.clone());
        debug_report.self_custody_bundle(pipeline.face_identifier_bundle.clone().ok());
        debug_report.self_custody_thumbnail(pipeline.face_identifier_bundle.clone().ok());
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

**File:** src/consts.rs (L347-349)
```rust
// TODO: This should be a getter function from ir_net rather than a constant.
/// Threshold for a valid signup in terms of occlusion 30.
pub const THRESHOLD_OCCLUSION_30: f64 = 0.85;
```

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

**File:** src/plans/biometric_pipeline/mod.rs (L343-422)
```rust
                        mega_agent_one::Output::Occlusion(occlusion::Output::Estimate(output)) => {
                            occlusion = Some(Ok(output));
                            progress += OCCLUSION_PROGRESS;
                        }
                        mega_agent_one::Output::Occlusion(occlusion::Output::Error(error)) => {
                            occlusion = Some(Err(error));
                        }
                        mega_agent_one::Output::Iris(iris::Output::Estimate(
                            iris::EstimateOutput {
                                iris_code_shares,
                                mask_code_shares,
                                iris_code,
                                mask_code,
                                iris_code_version,
                                metadata,
                                normalized_image,
                                normalized_image_resized,
                            },
                        )) => {
                            iris_left = Some(EyePipeline {
                                iris_code_shares,
                                mask_code_shares,
                                iris_code,
                                mask_code,
                                iris_code_version,
                                metadata,
                                iris_normalized_image: normalized_image,
                                iris_normalized_image_resized: normalized_image_resized,
                            });

                            self.set_timeout();
                            progress += IRIS_ESTIMATE_PROGRESS;
                        }
                        mega_agent_one::Output::Iris(iris::Output::Version(version)) => {
                            iris_version = Some(version);
                        }
                        mega_agent_one::Output::Iris(
                            iris::Output::Error(error),
                            // If IIP or Iris fail, there is not much we can do.
                        ) => return Err(Error::Iris(error))?,
                        mega_agent_one::Output::IRNet(ir_net::Output::Version(version)) => {
                            ir_net_version = Some(version);
                        }
                        o @ mega_agent_one::Output::IRNet(_) => {
                            unreachable!("{o:?} is not part of biometric pipeline!")
                        }
                    }
                }
                ModelOutput::MegaAgentTwo(output) => match output {
                    mega_agent_two::Output::Iris(boxed_output) => match *boxed_output {
                        iris::Output::Estimate(iris::EstimateOutput {
                            iris_code_shares,
                            mask_code_shares,
                            iris_code,
                            mask_code,
                            iris_code_version,
                            metadata,
                            normalized_image,
                            normalized_image_resized,
                        }) => {
                            iris_right = Some(EyePipeline {
                                iris_code_shares,
                                mask_code_shares,
                                iris_code,
                                mask_code,
                                iris_code_version,
                                metadata,
                                iris_normalized_image: normalized_image,
                                iris_normalized_image_resized: normalized_image_resized,
                            });

                            self.set_timeout();
                            progress += IRIS_ESTIMATE_PROGRESS;
                        }
                        iris::Output::Version(version) => {
                            iris_version = Some(version);
                        }
                        // If IIP or Iris fail, there is not much we can do.
                        iris::Output::Error(error) => return Err(Error::Iris(error))?,
                    },
```

**File:** src/plans/biometric_pipeline/mod.rs (L476-489)
```rust
        Ok(Pipeline {
            v2: PipelineV2 {
                eye_left: iris_left.unwrap(),
                eye_right: iris_right.unwrap(),
                ir_net_version: ir_net_version.unwrap(),
                iris_version: iris_version.clone().unwrap(),
            },
            occlusion: occlusion.unwrap(),
            face_identifier_fraud_checks: face_identifier_fraud_checks.unwrap(),
            face_identifier_bundle: face_identifier_bundle.unwrap(),
            mega_agent_one_config: mega_agent_one_config.unwrap(),
            mega_agent_two_config: mega_agent_two_config.unwrap(),
        })
    }
```

**File:** src/plans/personal_custody_package.rs (L589-604)
```rust
        // TODO: Should we produce a PCP if we don't have all the shares? This can happen if we detect fraud or some
        // other issue.
        let (
            Some(left_iris_code_shares),
            Some(left_mask_code_shares),
            Some(right_iris_code_shares),
            Some(right_mask_code_shares),
        ) = (
            &self.pipeline.left_iris_code_shares,
            &self.pipeline.left_mask_code_shares,
            &self.pipeline.right_iris_code_shares,
            &self.pipeline.right_mask_code_shares,
        )
        else {
            bail!("Missing Iris and mask code shares");
        };
```
