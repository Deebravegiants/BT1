Based on the investigation, I found a concrete analog: the personal-custody-package (biometric data) upload path in `MasterPlan::do_signup` builds and uploads the encrypted iris/face biometric package to the backend **before** the enrollment/verification step checks whether the signup should actually be accepted, and does so even when the signup was already flagged as `Fraud` or `Failure`.

### Title
Biometric Data (PCP) Uploaded Regardless of Fraud/Failure Signup State Before Enrollment Gate - (File: src/plans/mod.rs)

### Summary
The yAxis report flags that a security-relevant guard (the "emergency exit" check) is applied inconsistently — a sensitive state-changing action (minting) is allowed to execute even though a higher-level protective state (emergency exit) should have blocked it, because the check was not enforced as a strict, universally-applied gate. The same "guard not applied before action" pattern exists in `orb-core`'s signup flow: after fraud detection determines `signup_reason` (`Fraud`/`Failure`/`Normal`), the biometric package (iris codes, face embeddings, normalized iris images) is still built and uploaded to the backend prior to, and independent of, the enrollment success gate.

### Finding Description
In `MasterPlan::do_signup` [1](#0-0) , `signup_reason` is computed as `Fraud`, `Failure`, or `Normal` based on `detect_fraud` and pipeline availability. Immediately afterward, regardless of `signup_reason`, the code proceeds to build the Personal Custody Package (PCP) via `build_pcp` and upload tier-0/1/2 packages to the backend: [2](#0-1) . The `signup_reason` value is passed into `build_pcp`/`personal_custody_package::Plan` only to be embedded as metadata in the uploaded package (`info.json`'s `signup_reason` field) [3](#0-2)  — it is not used as a gate to prevent the upload itself. The only checks that can prevent building/uploading the PCP are unrelated to fraud state: missing pipeline data (`data_error!` macro on missing face/iris fields) [4](#0-3)  or `self.skip_pipeline()` / extension config [5](#0-4) . The enrollment decision — the actual point where a `Fraud`/`Failure` signup is meant to be treated differently — happens only afterward, in `enroll_user`, and only affects the final `success` flag and telemetry [6](#0-5) , not whether biometric data was already transmitted.

This mirrors the report's root cause: a state that is supposed to gate an operation (emergency-exit ⇒ block minting; fraud/failure detection ⇒ block biometric data egress) is checked and recorded, but the guarding check is not converted into a hard precondition on the sensitive action. The sensitive action (data upload) proceeds unconditionally, with the protective signal merely logged/tagged rather than enforced.

### Impact Explanation
If a signup is locally flagged as fraudulent (or failed pipeline/internal error) prior to the PCP upload step, the orb still transmits the user's encrypted iris and face biometric package to the backend. While the tier data is encrypted (backend and self-custody keys), the `signup_reason` is merely a plaintext/salted-hash tag included for backend bookkeeping, not a precondition preventing transmission. This is analogous to "unauthorized/misattributed signup" and "biometric data disclosure" risk categories: biometric material tied to a fraud-flagged capture is still fully packaged and shipped off-device, increasing exposure and enabling downstream mismatches between local fraud determination and what data the backend possesses/retains.

### Likelihood Explanation
Likelihood is moderate: this occurs on every `Fraud` or `Failure`-classified signup (a normal operational branch, not a rare edge case), and the code path is unconditionally reached unless the pipeline itself returned `None`. Given `detect_fraud` in this FOSS build has been stripped of its checks (`Ok(false)` always) [7](#0-6) , the practical trigger today is primarily `SignupReason::Failure` (pipeline failures), but the architecture would behave identically once fraud checks are reinstated.

### Recommendation
Convert the fraud/failure signup-reason check into a hard precondition (a guard/modifier-equivalent) applied before `build_pcp`/`upload_pcp_tier_0` are invoked, so that biometric package construction and upload are skipped (or routed to a minimal/redacted metadata-only report) whenever `signup_reason != SignupReason::Normal`, rather than relying on the reason being embedded as descriptive metadata after the fact.

### Proof of Concept
1. Trigger a signup where `detect_fraud` (once reinstated) or pipeline failure sets `signup_reason` to `Fraud` or `Failure` at `src/plans/mod.rs:565-571`.
2. Observe execution continues unconditionally into `build_pcp` and `upload_pcp_tier_0`/`data_uploader::Input::Pcp` sends at `src/plans/mod.rs:574-636`, uploading the full iris/face biometric package.
3. Confirm `signup_reason` only appears as a hashed metadata field in `info.json` (`src/plans/personal_custody_package.rs:463-509`), with no branch anywhere in `build_pcp` or the upload calls that short-circuits based on `SignupReason::Fraud`/`Failure`.

### Citations

**File:** src/plans/mod.rs (L558-561)
```rust
        if self.skip_pipeline() || debug_report.signup_extension_config.is_some() {
            result.success = true;
            return Ok(result);
        }
```

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

**File:** src/plans/mod.rs (L639-663)
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
    }
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

**File:** src/plans/mod.rs (L1652-1691)
```rust
    ) -> Result<Option<PersonalCustodyPackages>> {
        macro_rules! data_error {
            ($field:literal) => {
                data_error!(
                    concat!("Image self-custody upload failed due to missing `", $field, "``"),
                    concat!("type:missing_", $field)
                )
            };
            ($message:expr, $dd_type:expr) => {
                tracing::error!($message);
                dd_incr!("main.count.signup.result.failure.upload_custody_images", $dd_type);
                notify_failed_signup(orb, None);
                return Ok(None);
            };
        }

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
```

**File:** src/plans/personal_custody_package.rs (L463-509)
```rust
        let Self { credentials, signup_id, signup_reason, .. } = self;
        let Credentials { operator_qr_code, user_qr_code_string, .. } = credentials;
        let signup_id_salt = gen_salt();
        let signup_reason_salt = gen_salt();
        let orb_id_salt = gen_salt();
        let operator_id_salt = gen_salt();
        let timestamp_salt = gen_salt();
        let qr_code_salt = gen_salt();
        let orb_id = ORB_ID.as_str();
        let timestamp = self
            .capture_start
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap_or_default()
            .as_secs()
            .to_string();
        let orb_public_key_certificate = BASE64.encode(&ORB_PUBLIC_KEY);
        let left_ir_image_id = self.identification_image_ids.left_ir.to_string();
        let right_ir_image_id = self.identification_image_ids.right_ir.to_string();
        let thumbnail_image_id = self.identification_image_ids.self_custody_candidate.to_string();
        let software_version = &**ORB_OS_VERSION;
        let orb_country = self.location_data.operator_team_operating_country.clone();
        hashes.insert("signup_id".to_owned(), salted_sha256(signup_id, &signup_id_salt));
        hashes
            .insert("signup_reason".to_owned(), salted_sha256(signup_reason, &signup_reason_salt));
        hashes.insert("orb_id".to_owned(), salted_sha256(orb_id, &orb_id_salt));
        hashes.insert(
            "operator_id".to_owned(),
            salted_sha256(&operator_qr_code.user_id, &operator_id_salt),
        );
        hashes.insert("timestamp".to_owned(), salted_sha256(&timestamp, &timestamp_salt));
        hashes.insert("qr_code".to_owned(), salted_sha256(user_qr_code_string, &qr_code_salt));
        let software_version_salt = {
            let salt = gen_salt();
            hashes.insert("software_version".to_owned(), salted_sha256(software_version, &salt));
            salt
        };
        let orb_country_salt = {
            let salt = gen_salt();
            hashes.insert("orb_country".to_owned(), salted_sha256(&orb_country, &salt));
            salt
        };

        let info = InfoJson {
            signup_id,
            signup_id_salt,
            signup_reason,
            signup_reason_salt,
```
