Based on my investigation, this is a valid finding. The critical evidence is that `detect_fraud` in this FOSS build explicitly has all fraud checks deleted and unconditionally returns `false`, and there is no code anywhere in `biometric_capture` or `biometric_pipeline` that cross-verifies the left-eye face identity against the right-eye face identity.

### Title
Missing same-person identity-continuity check between left/right eye captures allows mixed-identity iris code pair binding - ([File: src/plans/biometric_capture/mod.rs, src/plans/biometric_pipeline/mod.rs, src/plans/mod.rs])

### Summary
`biometric_capture::Plan` captures the left eye and right eye as two sequential, independently-gated objectives (`target_left_eye` toggled between objectives) with only a timing delay (`delay_between_eye_captures`) between them, and no biometric identity-continuity check binds the person present for `eye_left` to the person present for `eye_right`. `biometric_pipeline::Plan::run` then independently routes `mega_agent_one::Output::Iris` into `iris_left` and `mega_agent_two::Output::Iris` into `iris_right` via `self.model_output.take()` inside the `run_with_fence` loop, with no cross-check that both eyes' iris codes originate from the same physiological subject. Compounding this, `detect_fraud` in `src/plans/mod.rs` has had "ALL FRAUD CHECKS" deleted and always returns `false`, so no downstream check could catch this either.

### Finding Description
In `src/plans/biometric_capture/mod.rs`, the capture plan uses a queue of `Objective`s alternating `target_left_eye`, and `set_next_objective`/`run_check` (lines 485-501) simply advances to the next objective once IR+RGB frames are captured for the current side, applying only `self.valid_capture_after = Instant::now() + self.delay_between_eye_captures` [1](#0-0)  as a temporal gate — there is no facial-embedding or iris-embedding comparison between the two sides. `handle_ir_net` only checks `perceived_side` and sharpness/score thresholds for the currently targeted eye [2](#0-1) ; it never compares the captured face/iris against whichever face/iris was captured for the other eye.

In `src/plans/biometric_pipeline/mod.rs`, `Plan::run` drives a `run_with_fence` loop that calls `self.model_output.take().unwrap()` and independently assigns `mega_agent_one::Output::Iris(...)` to `iris_left` and `mega_agent_two::Output::Iris(...)` to `iris_right` [3](#0-2) . These two agent outputs are processed from `self.eye_left`/`self.eye_right` IR frames that were captured by `biometric_capture::Plan` — whatever frames ended up in those slots become `iris_left`/`iris_right` with no per-signup identity binding check (e.g. no `face_identifier` cross-comparison of `frame_left` vs `frame_right` embeddings is used to gate iris code acceptance). The final `Pipeline` is built directly from `iris_left.unwrap()`/`iris_right.unwrap()` [4](#0-3) .

The `face_identifier` agent does compute embeddings for `frame_left`, `frame_right`, and `frame_self_custody_candidate` via `Input::Estimate` [5](#0-4) , but its output `FraudChecks`/`Bundle` is only used for self-custody thumbnail/embedding bundling, not fed back into gating whether `iris_left`/`iris_right` should be accepted as belonging to the same person. Even if it did produce a same-person signal, `detect_fraud` in `src/plans/mod.rs` unconditionally returns `Ok(false)` with the comment "FOSS: WE HAVE DELETED ALL FRAUD CHECKS" [6](#0-5) , so no fraud-based fail-closed path exists downstream of the pipeline to catch a cross-identity capture.

An unprivileged attacker (person X) starts a signup, completes the left-eye objective, then during the mandatory `delay_between_eye_captures` window and the right-eye capture objective, has person Y physically take their place at the Orb. As long as Y's iris/face score passes the same sharpness/quality/liveness thresholds used for X, `right_ir`/`right_rgb` will be populated from Y's frames with no comparison to X's captured left-eye/left-face data, producing a `Capture` with `eye_left` from X and `eye_right` from Y, which flows unmodified into `EyePipeline.eye_left`/`eye_right` of `Pipeline` and ultimately into the uploaded personal custody package (`left_iris_code`/`right_iris_code` in `build_pcp`, `src/plans/mod.rs` lines 1735-1751).

### Impact Explanation
This produces a biometric signup package where the left iris code cryptographically/data-wise belongs to a different physical person than the right iris code, breaking the core identity-binding invariant of a World ID signup (one iris-pair, one person). This corresponds to a "wrong-identity binding" / biometric integrity impact category in the Worldcoin/Orb bounty program — it could be used to test whether backend-side de-duplication logic can be confused by a hybrid code pair, or to probe uniqueness-check bypass strategies, though the ultimate exploitability depends on backend behavior not visible in this repo.

### Likelihood Explanation
Preconditions require only an unprivileged attacker able to physically substitute a second person in front of the Orb cameras between the left-eye and right-eye capture objectives during their own signup — no special access, no hardware tampering, no credentials. The capture flow's per-eye gating (`target_left_eye`, `valid_capture_after` delay) is independent per side and offers no cross-eye continuity check, making this readily repeatable across signup attempts, contingent on person Y also being able to pass the individual per-eye liveness/sharpness gates.

### Recommendation
Add a same-person continuity check between `eye_left` and `eye_right` captures before finalizing `Capture`/`Pipeline`: compare `face_identifier` embeddings (or a dedicated face-embedding-similarity check) between `frame_left` and `frame_right` (and ideally `frame_self_custody_candidate`) and fail the biometric pipeline (return `Err`/fail-closed) if similarity falls below a strict threshold. This check should be enforced in `biometric_pipeline::Plan::run` (or in `detect_fraud`) rather than only relying on independent per-eye quality gates in `biometric_capture`.

### Proof of Concept
Add an integration test in `src/plans/biometric_pipeline/mod.rs` tests module that constructs two synthetic `iris::EstimateOutput` values (`metadata.eye_side` = "left" vs "right", and embedded distinguishing markers simulating two different subjects, e.g. differing `iris_code`/`iris_code_shares` patterns representing distinct identities), injects them via `mega_agent_one::Output::Iris` and `mega_agent_two::Output::Iris` respectively into a mocked `run_with_fence`/`Plan::run` cycle, and asserts:
1. Currently: `Plan::run` returns `Ok(Pipeline)` regardless of whether the two `EstimateOutput`s represent different subjects (demonstrating the missing check).
2. Expected after fix: introduce a same-person check (e.g., using `face_identifier` embedding cosine similarity between `frame_left`/`frame_right`) and assert `Plan::run` returns `Err(Error::...)` (a new fail-closed variant) when the check fails, and `Ok(Pipeline)` only when the two eye captures are confirmed to originate from the same continuity of capture.

### Citations

**File:** src/plans/biometric_capture/mod.rs (L216-260)
```rust
impl OrbPlan for Plan {
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
```

**File:** src/plans/biometric_capture/mod.rs (L485-501)
```rust
    pub(crate) async fn run_check(&mut self, orb: &mut Orb) -> Result<bool> {
        if let Some(mirror_offset) = orb.mirror_offset {
            self.mirror_offsets.push(mirror_offset);
        }
        if self.timed_out {
            tracing::info!("Biometric capture timeout");
            return Ok(true);
        }
        if !self.set_next_objective(orb).await? {
            dd_incr!("main.count.signup.during.biometric_capture.both_eye_captured");
            tracing::info!("All objectives achieved");
            orb.ui.biometric_capture_progress(1.1);
            return Ok(true);
        }
        self.valid_capture_after = Instant::now() + self.delay_between_eye_captures;
        Ok(false)
    }
```

**File:** src/plans/biometric_pipeline/mod.rs (L350-416)
```rust
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
```

**File:** src/plans/biometric_pipeline/mod.rs (L476-482)
```rust
        Ok(Pipeline {
            v2: PipelineV2 {
                eye_left: iris_left.unwrap(),
                eye_right: iris_right.unwrap(),
                ir_net_version: ir_net_version.unwrap(),
                iris_version: iris_version.clone().unwrap(),
            },
```

**File:** src/agents/python/face_identifier/mod.rs (L47-70)
```rust
pub enum Input {
    /// Face identifier similarity score.
    Estimate {
        /// The signup id of this signup attempt.
        signup_id: String,
        /// Left face RGB frame.
        frame_left: camera::rgb::Frame,
        /// Right face RGB frame.
        frame_right: camera::rgb::Frame,
        /// The face RGB frame validated by the face model during biometric capture.
        frame_self_custody_candidate: camera::rgb::Frame,
        /// The eye landmarks of the left face RGB frame.
        eyes_landmarks_left: (rgb_net::Point, rgb_net::Point),
        /// The eye landmarks of the right face RGB frame.
        eyes_landmarks_right: (rgb_net::Point, rgb_net::Point),
        /// The face RGB frame eye landmarks, validated by the face model during biometric capture.
        eyes_landmarks_self_custody_candidate: (rgb_net::Point, rgb_net::Point),
        /// The bbox of the left face RGB frame.
        bbox_left: rgb_net::Rectangle,
        /// The bbox of the right face RGB frame.
        bbox_right: rgb_net::Rectangle,
        /// The bbox of the self-custody face RGB frame.
        bbox_self_custody_candidate: rgb_net::Rectangle,
    },
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
