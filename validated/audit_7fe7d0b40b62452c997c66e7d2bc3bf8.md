### Title
No pause/kill-switch on the biometric data upload pipeline after local fraud detection - ([File: src/plans/mod.rs])

### Summary
The reported issue concerns the absence of a pausing mechanism that could prevent state-changing operations from proceeding under specific conditions such as a security event. The closest concrete analog in `orb-core` is in the signup pipeline: once a signup passes biometric capture, the Orb always builds and uploads the Personal Custody Package (encrypted iris/face biometric data) to the backend, **regardless of whether local fraud detection flagged the signup**. There is no mechanism to pause/halt the upload once `fraud_detected` is `true`.

### Finding Description
In `do_signup`, the flow is: run the biometric pipeline, compute `fraud_detected`/`signup_reason`, then unconditionally call `build_pcp` and upload the resulting tier0/tier1/tier2 packages via `data_uploader`, with the `signup_reason` only used for tagging the request, not for gating the upload: [1](#0-0) [2](#0-1) 

The `signup_reason` (including `SignupReason::Fraud`) is only consumed later by `enroll_user`/`signup_post::request` to inform the *backend* of the reason, but the encrypted biometric package upload itself is not paused or aborted when fraud is locally detected: [3](#0-2) [4](#0-3) 

There is no equivalent of a "pause" primitive gating this specific data-exfiltration path the way `orb.ui.pause()`/`resume()` or the `image_uploader::Input::PauseUpload` command gate other subsystems: [5](#0-4) [6](#0-5) 

Additionally, in this FOSS build the fraud engine itself is stubbed out (`N_FRAUD_CHECKS = 0`, `detect_fraud` always returns `Ok(false)`), which means even the trigger condition for `SignupReason::Fraud` can never fire locally, compounding the lack of any effective halt mechanism: [7](#0-6) [8](#0-7) 

### Impact Explanation
Because the upload of the encrypted biometric package (iris codes, face embeddings/thumbnails) proceeds independent of the fraud outcome, and because there is no pause switch to interrupt this pipeline once a fraud condition is (or would be) detected, biometric data belonging to signups that are ultimately rejected as fraudulent is still transmitted and persisted to backend storage. This is a data-minimization/disclosure concern: sensitive biometric data continues to leave the device even for signups the system itself considers invalid.

### Likelihood Explanation
This triggers on every signup that reaches the pipeline stage and is subsequently flagged (or would be flagged, if fraud checks were enabled) as fraudulent — i.e., any adversarial or malformed signup attempt that passes biometric capture but fails fraud checks. Given the FOSS build always returns `fraud_detected = false`, the condition is currently unreachable in this exact build, but the architecture itself provides no pause/gating primitive should fraud checks be reinstated (as they are in the proprietary build), making this a structural gap rather than a one-off bug.

### Recommendation
Introduce an explicit gate/pause point before `build_pcp`/`data_uploader` calls that checks `signup_reason`/`fraud_detected` and skips or halts the PCP tier0/1/2 upload when fraud is detected, mirroring the existing pause patterns used elsewhere (`ui.pause()`, `image_uploader::Input::PauseUpload`). At minimum, the decision to upload biometric packages should be conditioned on the same fraud signal that determines `SignupReason`, rather than being unconditional.

### Proof of Concept
1. Enable a build where `detect_fraud` can return `true` (i.e., the proprietary fraud-check engine, not the FOSS stub).
2. Run a signup where biometric capture succeeds but the fraud engine flags the signup (`fraud_detected = true`, `signup_reason = SignupReason::Fraud`).
3. Observe that `do_signup` still calls `build_pcp` and uploads tier0/tier1/tier2 packages via `orb.data_uploader` at [9](#0-8)  before the `signup_reason` is used only for backend reporting in `enroll_user`.
4. Confirm no code path pauses/aborts the upload based on `fraud_detected`/`signup_reason` prior to this point.

### Citations

**File:** src/plans/mod.rs (L562-571)
```rust
        let pipeline = Box::pin(self.biometric_pipeline(orb, debug_report, &capture)).await?;
        let fraud_detected = !self.skip_fraud_checks()
            && self.detect_fraud(orb, debug_report, pipeline.as_ref()).await?;
        let signup_reason = if pipeline.is_none() {
            SignupReason::Failure
        } else if fraud_detected {
            SignupReason::Fraud
        } else {
            SignupReason::Normal
        };
```

**File:** src/plans/mod.rs (L580-637)
```rust
            let packages = match Box::pin(self.build_pcp(
                orb,
                credentials,
                &capture,
                pipeline.as_ref(),
                debug_report,
                signup_reason,
            ))
            .await
            {
                Ok(Some(p)) => p,
                Ok(None) => {
                    return Ok(result);
                }
                Err(e) => {
                    tracing::error!("{e}");
                    return Ok(result);
                }
            };
            data_uploader::wait_queues(orb.data_uploader.enabled().unwrap()).await?;
            if !self
                .upload_pcp_tier_0(
                    orb,
                    &result.signup_id,
                    &user_id,
                    packages.tier0,
                    packages.tier0_checksum,
                    if pcp_version >= 3 { Some(0) } else { None },
                )
                .await?
            {
                return Ok(result);
            }
            if pcp_version >= 3 {
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id: user_id.clone(),
                        data: packages.tier1,
                        checksum: packages.tier1_checksum.as_ref().to_vec(),
                        tier: 1,
                    })))
                    .await?;
                orb.data_uploader
                    .enabled()
                    .unwrap()
                    .send(port::Input::new(data_uploader::Input::Pcp(data_uploader::Pcp {
                        signup_id: result.signup_id.clone(),
                        user_id,
                        data: packages.tier2,
                        checksum: packages.tier2_checksum.as_ref().to_vec(),
                        tier: 2,
                    })))
                    .await?;
            }
        }
```

**File:** src/plans/mod.rs (L639-662)
```rust
        let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups
        {
            debug_report.enrollment_status(match signup_reason {
                SignupReason::Normal => enroll_user::Status::Success,
                _ => enroll_user::Status::Error,
            });
            signup_reason == SignupReason::Normal
        } else {
            Box::pin(self.enroll_user(
                orb,
                debug_report,
                &capture,
                pipeline.as_ref(),
                signup_reason,
            ))
            .await
            .is_success()
        };

        Self::report_signup_reason(success, signup_reason, debug_report);

        result.success =
            debug_report.enrollment_status.as_ref().map_or(false, enroll_user::Status::is_success);
        Ok(result)
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

**File:** src/backend/signup_post.rs (L72-82)
```rust
/// Every signup needs to be tagged with a reason for the backend to process it.
#[derive(Serialize, Debug, Default, Copy, Clone, PartialEq, Eq)]
pub enum SignupReason {
    /// Signup was successfully processed on the Orb.
    #[default]
    Normal,
    /// Signup failed due to some agent dying in the biometric pipeline or some internal error.
    Failure,
    /// Signup was detected as a fraud attempt at the orb (not to be confused with the backend fraud checks).
    Fraud,
}
```

**File:** src/agents/image_uploader.rs (L91-98)
```rust
            Input::StartUpload { image_upload_delay } => {
                let box_var: UploadImages = Box::pin(upload_all_signup_images(image_upload_delay));
                network_request.set(box_var.fuse());
            }
            Input::PauseUpload => {
                //Immediately drop any pending request.
                network_request.set(Fuse::terminated());
            }
```

**File:** src/plans/biometric_capture/focus_sweep.rs (L205-245)
```rust
    async fn perform_focus_sweep(&mut self, orb: &mut Orb) -> Result<()> {
        tracing::info!("Focus Sweep extension: Beginning sweep @{}", self.last_focus);
        let start_time = SystemTime::now();
        orb.ui.pause();
        orb.main_mcu.send(mcu::main::Input::TriggeringIrEyeCamera(false)).await?;
        orb.main_mcu.send(mcu::main::Input::FrameRate(SWEEP_FPS)).await?;
        orb.disable_ir_auto_focus();
        orb.disable_ir_net();
        orb.disable_rgb_net();
        orb.disable_mirror();
        orb.disable_distance();
        orb.disable_eye_tracker();
        orb.disable_eye_pid_controller();
        orb.enable_image_notary()?;
        orb.ir_eye_save_fps_override = Some(f32::INFINITY);
        let polynomial = make_polynomial(self.last_focus);
        tracing::info!("Focus Sweep polynomial: {polynomial:?}");
        orb.main_mcu
            .send(mcu::main::Input::IrEyeCameraFocusSweepValuesPolynomial(polynomial.clone()))
            .await?;
        orb.main_mcu.send(mcu::main::Input::PerformIrEyeCameraFocusSweep).await?;
        self.frame_counter = SWEEP_FRAMES;
        self.timeout = Box::pin(time::sleep(Duration::from_secs_f64(
            f64::from(SWEEP_FRAMES) / f64::from(SWEEP_FPS) * 1.1,
        )))
        .fuse();

        orb.run(self).await?;

        orb.ir_eye_save_fps_override = None;
        orb.enable_ir_auto_focus()?;
        orb.enable_ir_net().await?;
        orb.enable_rgb_net(true).await?;
        orb.enable_mirror()?;
        orb.enable_distance()?;
        orb.enable_eye_tracker()?;
        orb.enable_eye_pid_controller()?;
        orb.disable_image_notary();
        orb.main_mcu.send(mcu::main::Input::FrameRate(IR_CAMERA_FRAME_RATE)).await?;
        orb.main_mcu.send(mcu::main::Input::TriggeringIrEyeCamera(true)).await?;
        orb.ui.resume();
```

**File:** src/plans/fraud_check.rs (L10-21)
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
```
