### Title
Biometric Data (Personal Custody Package) Is Built and Uploaded to the Backend Even When Fraud Is Detected, Bypassing the Fraud-Detection Restriction - (File: src/plans/mod.rs)

### Summary
This is the same bug class as the Paladin `HolyPaladinToken` finding: a protective check (`emergency`/fraud state) correctly gates one code path but is not enforced on a second, parallel code path that mutates/uploads the same protected state. In `orb-core`, `MasterPlan::do_signup` computes `fraud_detected`/`signup_reason` from `detect_fraud()`, but the subsequent personal-custody-package (PCP) build and upload of the user's biometric templates (iris codes, normalized iris images, face embeddings) proceeds unconditionally, regardless of whether `signup_reason == SignupReason::Fraud`.

### Finding Description
In `do_signup`, after `detect_fraud()` runs, the result is only used to compute `signup_reason` for later reporting/UI/enrollment purposes: [1](#0-0) 

Regardless of `signup_reason`, the code unconditionally proceeds to build the PCP (containing normalized iris images/masks, iris codes, and face-identifier embeddings) and uploads tier 0/1/2 packages to the backend via `build_pcp` and `upload_pcp_tier_0`/`data_uploader`: [2](#0-1) 

`build_pcp` only aborts if pipeline fields are literally missing (`data_error!` macro on missing bundle/image data) — it does not check `signup_reason` to decide whether to build/upload the package at all: [3](#0-2) [4](#0-3) 

`signup_reason` is only threaded through as metadata (`FRAUD`/`NORMAL`/`FAILURE` string in the package's `info.json`), not as a gate on whether the upload proceeds: [5](#0-4) 

The actual restriction that should stop the flow — the fraud check — only affects the *enrollment* decision path (`enroll_user` / `signup_post::request`, which is told the `signup_reason`) and the local `success` flag for user-centric signups: [6](#0-5) 

But by the time that decision is made, the user's full biometric templates have already been packaged and pushed into `data_uploader`'s upload queue and are en route to (or already on) the backend, exactly analogous to how in the Paladin bug, `_updateUserRewards()` continued to execute via `_beforeTokenTransfer()` even after `emergency` was triggered, because the restriction was only enforced in one call path (`updateUserRewardState()`/stake-lock actions) and not in the other (token transfer).

### Impact Explanation
Biometric data (iris codes/images, face embeddings) for a signup that the orb's own on-device fraud detector flagged as fraudulent is nevertheless uploaded to the backend data-storage tier. This is a biometric-data-retention/disclosure concern: data belonging to a fraudulent or duplicate/failed signup is persisted server-side the same as legitimate signup data, undermining the intent of local fraud enforcement to prevent processing/propagation of that person's biometric data once fraud is flagged.

### Likelihood Explanation
This triggers deterministically any time `detect_fraud()` returns `true` for a signup that otherwise completed the biometric pipeline successfully — no attacker action beyond a normal signup attempt that trips a fraud heuristic is required, so likelihood of occurrence is high whenever fraud detection fires (which is its designed purpose).

### Recommendation
Gate the PCP build/upload path (`build_pcp` / `upload_pcp_tier_0` / `data_uploader::Input::Pcp` sends in `do_signup`) on `signup_reason != SignupReason::Fraud` (and on `SignupReason::Failure` as already effectively enforced by missing-data checks), mirroring the enrollment gate, so that a single, consistently-enforced check controls all code paths that persist or transmit biometric data for a signup.

### Proof of Concept
1. Configure/trigger a signup where the on-device fraud checks (`detect_fraud`, `src/plans/mod.rs:563-564`) return `true` (e.g., simulate a fraud-detected pipeline result).
2. Observe that `do_signup` still proceeds to call `build_pcp` with `signup_reason = SignupReason::Fraud` (`src/plans/mod.rs:580-587`), successfully builds tier0/1/2 packages, and unconditionally uploads them via `upload_pcp_tier_0` and `data_uploader::Input::Pcp` sends (`src/plans/mod.rs:599-636`).
3. Confirm the only place `signup_reason` prevents anything is downstream in enrollment success determination (`src/plans/mod.rs:639-662`), by which point the biometric package has already left the device.

### Citations

**File:** src/plans/mod.rs (L562-572)
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
        let user_id = qr_codes.user_qr_code.user_id.clone();
```

**File:** src/plans/mod.rs (L574-636)
```rust
        if let Ok(mut credentials) = qr_codes.try_into() {
            let personal_custody_package::Credentials { pcp_version, .. } = &mut credentials;
            if !pcp_v3 {
                *pcp_version = 2;
            }
            let pcp_version = *pcp_version;
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

**File:** src/plans/mod.rs (L1643-1652)
```rust
    #[allow(clippy::too_many_lines, clippy::too_many_arguments)]
    async fn build_pcp(
        &self,
        orb: &mut Orb,
        credentials: personal_custody_package::Credentials,
        capture: &biometric_capture::Capture,
        pipeline: Option<&biometric_pipeline::Pipeline>,
        debug_report: &debug_report::Builder,
        signup_reason: SignupReason,
    ) -> Result<Option<PersonalCustodyPackages>> {
```

**File:** src/plans/mod.rs (L1668-1701)
```rust
        let Some(face_identifier_bundle) =
            pipeline.as_ref().and_then(|p| p.face_identifier_bundle.as_ref().ok())
        else {
            data_error!("face_identifier_bundle");
        };
        if let Some(error) = &face_identifier_bundle.error {
            data_error!(
                "Face identifier bundle contains an error: {error:?}",
                "type:face_identifier_bundle_error"
            );
        }
        let Some(face_identifier_thumbnail) = &face_identifier_bundle.thumbnail else {
            data_error!("face_identifier_bundle.thumbnail");
        };
        let Some(face_identifier_thumbnail_image) = &face_identifier_thumbnail.image else {
            data_error!("face_identifier_bundle.thumbnail.image");
        };
        let Some(face_identifier_embeddings) = &face_identifier_bundle.embeddings else {
            data_error!("face_identifier_bundle.embeddings");
        };
        let Some(face_identifier_inference_backend) = &face_identifier_bundle.inference_backend
        else {
            data_error!("face_identifier_bundle.inference_backend");
        };
        let Some(left_normalized_iris_image) =
            pipeline.as_ref().and_then(|p| p.v2.eye_left.iris_normalized_image.as_ref())
        else {
            data_error!("v2.eye_left.iris_normalized_image");
        };
        let Some(right_normalized_iris_image) =
            pipeline.as_ref().and_then(|p| p.v2.eye_right.iris_normalized_image.as_ref())
        else {
            data_error!("v2.eye_right.iris_normalized_image");
        };
```

**File:** src/plans/personal_custody_package.rs (L211-242)
```rust
impl Plan {
    /// Runs the plan for building and uploading the personal custody package.
    pub async fn run(self) -> Result<PersonalCustodyPackages> {
        let Self {
            capture_start,
            signup_id,
            identification_image_ids,
            capture,
            pipeline,
            credentials,
            signup_reason,
            location_data,
        } = self;
        let pipeline_box = Box::new(pipeline);

        #[cfg(feature = "internal-pcp-export")]
        let signup_id2 = signup_id.clone();
        let packages = task::spawn_blocking(move || {
            let hyrax = (&*pipeline_box).into();
            Package {
                ts: UNIX_EPOCH.elapsed()?,
                capture_start,
                capture,
                identification_image_ids,
                pipeline: pipeline_box,
                hyrax,
                credentials,
                signup_id: signup_id.to_string(),
                signup_reason: signup_reason.to_screaming_snake_case(),
                location_data,
            }
            .build()
```
