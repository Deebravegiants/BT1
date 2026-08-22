### Title
Occlusion detection result is computed but never enforced to block enrollment - (File: src/plans/mod.rs)

### Finding Description
`biometric_pipeline::Plan::run` computes an occlusion estimate via `occlusion::Environment::occlusion_estimate` (`src/agents/python/occlusion.rs:130-174`), which returns `EstimateOutput { occlusion, eye_glasses_occlusion, face_mask_occlusion, .. }`. The pipeline stores this in `Pipeline.occlusion: Result<occlusion::EstimateOutput, PyError>` [1](#0-0) , populated from the `mega_agent_one::Output::Occlusion(occlusion::Output::Estimate(output))` branch which unconditionally sets `occlusion = Some(Ok(output))` regardless of the boolean flags inside it [2](#0-1) .

In `src/plans/mod.rs`, after the pipeline completes, the only consumer of `pipeline.occlusion` is:
```
debug_report.occlusion_error(pipeline.occlusion.clone().err());
tracing::info!("Occlusion Detection result: {:?}", pipeline.occlusion);
``` [3](#0-2) 

`occlusion_error` only extracts the `Err` (PyError) variant for debug logging — it discards the `Ok` value entirely, meaning `EstimateOutput.occlusion == true` (or `face_mask_occlusion == true` / `eye_glasses_occlusion == true`) is never inspected. I searched `src/plans/fraud_check.rs` and `src/plans/biometric_capture/mod.rs` for occlusion usage but found no gating logic that reads `pipeline.occlusion`'s boolean fields to reject or halt the signup flow — those files reference "occlusion" only in unrelated contexts (e.g., naming/other checks), not as an enforcement gate on the `Ok(EstimateOutput{occlusion:true,...})` result. The `Pipeline` is then returned as `Some(pipeline)` and consumed further downstream (enrollment/signup) without any branch that inspects `occlusion`, `eye_glasses_occlusion`, or `face_mask_occlusion` to stop the signup.

### Impact Explanation
If confirmed, occlusion (mask/glasses) detection would be purely cosmetic/telemetry — an attacker wearing an occluding mask or glasses that still produces a plausible IR/RGB capture (passing capture-phase checks) could proceed through the full biometric pipeline and reach enrollment/signup success, since the boolean occlusion flags are never used as a gate. This would correspond to a liveness/anti-spoofing bypass class of impact for Worldcoin/Orb (compromised biometric integrity of enrolled iris code under an occluded/masked presentation).

### Likelihood Explanation
Feasibility depends entirely on whether the upstream capture phase (`src/plans/biometric_capture/mod.rs`, which has 34 occlusion-related references) already gates/rejects occluded frames before the biometric_pipeline stage runs. I was not able to fully confirm within this session whether `biometric_capture` independently blocks capture based on occlusion output — the grep for occlusion in `biometric_capture/mod.rs` returned matches but I could not read the file contents this session to determine if those references constitute an enforcement gate (a capture-time occlusion check) that would make this pipeline-stage non-check redundant/non-exploitable. This is a critical unresolved point: if `biometric_capture` already halts/retries on detected occlusion before biometric_pipeline is invoked, then the missing check in `src/plans/mod.rs` may be dead code for security purposes since occluded captures would never reach the pipeline with `occlusion:true`. Without confirming that gap, I cannot assert this is a reachable, exploitable bypass with full confidence.

### Recommendation
Explicitly verify (via a background Devin session with full file access) whether `biometric_capture::Plan` enforces occlusion rejection before invoking `biometric_pipeline`. If no such gate exists, add an explicit check in `src/plans/mod.rs` right after line 1358, e.g., if `pipeline.occlusion` is `Ok(estimate)` and `estimate.occlusion` (or `estimate.face_mask_occlusion` / `estimate.eye_glasses_occlusion`) is `true`, abort the signup flow (return early, mark failure, and prevent `enroll_user`/`signup_post::request` from being reached), rather than only feeding the error into `debug_report`.

### Proof of Concept
Integration test plan: construct `biometric_pipeline::Pipeline` via `Pipeline::default_with_ok()` and override `occlusion` to `Ok(occlusion::EstimateOutput { occlusion: true, face_mask_occlusion: true, ..Default::default() })`. Feed this into the signup master `Plan` (or the specific function in `src/plans/mod.rs` that calls `debug_report.occlusion_error` and proceeds to fraud checks/enrollment). Assert that signup does NOT proceed to `Status::Success` / `enroll_user::Plan::run` is not invoked. This test would first require confirming (or bypassing, if absent) any capture-phase occlusion gate in `biometric_capture::Plan` so that an occluded pipeline result is actually reachable — a step I could not fully verify in this session due to iteration limits.

### Citations

**File:** src/plans/biometric_pipeline/mod.rs (L58-66)
```rust
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
