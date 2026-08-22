### Title
Personal Custody Package upload is not gated on fraud/failure status, causing biometric templates to be disclosed to the backend even for signups later marked `Fraud` or `Failure` - (File: `src/plans/mod.rs`)

### Summary
The reported bug describes `Ignite::releaseLockedTokens` paying `QI` rewards to a registration before its `failed` outcome is fully accounted for, because the reward-granting branch executes unconditionally while the failure state is only checked afterward. `orb-core`'s signup pipeline has the same structural flaw: `MasterPlan::do_signup` computes `signup_reason` (`Normal`/`Fraud`/`Failure`) from `detect_fraud`/pipeline result, but then calls `build_pcp` and uploads the resulting Personal Custody Package (PCP) — containing iris codes, normalized iris images, and face embeddings — to the backend *before* the enrollment/fraud outcome is finalized and reported back.

### Finding Description
In `MasterPlan::do_signup`, `signup_reason` is computed first: [1](#0-0) 

`signup_reason` is then passed into `self.build_pcp(...)`, which unconditionally builds the iris/face biometric package for any reason (`Normal`, `Fraud`, or `Failure`) — the reason is only embedded as a salted, hashed metadata field (`signup_reason_salt`) inside `info.json`, not used to prevent the build or upload: [2](#0-1) [3](#0-2) 

The packages are then uploaded via `upload_pcp_tier_0` and, for `pcp_version >= 3`, further uploaded as tier1/tier2 to the data uploader — again with no dependency on `signup_reason`: [4](#0-3) 

Only *after* this upload has already completed does the code determine `success` and report the outcome via `report_signup_reason`, which records `SignupStatus::Fraud` or `SignupStatus::OrbFailure` in the debug report: [5](#0-4) 

This is the same ordering bug as the report: the sensitive/valuable action (in Ignite, releasing `QI` rewards; here, uploading biometric identity data to the backend) is performed before the failure/fraud determination is enforced, so a "failed" outcome does not retroactively prevent the action that already occurred.

### Impact Explanation
Because `build_pcp`/`upload_pcp_tier_0` execute regardless of `signup_reason`, a signup that is subsequently classified as `Fraud` (e.g., detected as a fraud attempt at the orb) or `Failure` (pipeline/internal error) still has its iris codes, iris images, and face embeddings encrypted and uploaded to the backend's custody storage. The biometric templates for a rejected/fraudulent signup are disclosed and persisted server-side exactly as if the signup had succeeded; only a metadata tag distinguishes the two cases after the fact. This is a biometric data disclosure/retention issue: data that should arguably never leave the device (or at least never reach durable backend storage) for a failed/fraudulent enrollment is unconditionally uploaded.

### Likelihood Explanation
This triggers on every signup that reaches the biometric pipeline stage and is subsequently flagged as `Fraud` or `Failure` — no special access or malicious actor is required; it is a straightforward consequence of the code's control flow ordering. Any signup where fraud detection or pipeline failure occurs after image/iris capture will hit this path.

### Recommendation
Gate `build_pcp`/PCP upload on the finalized fraud/failure determination: skip building and uploading the PCP entirely (or upload only non-biometric metadata) when `signup_reason` is `Fraud` or `Failure`, mirroring the mitigation recommended in the analog report (resetting/short-circuiting on failure before the payout/upload occurs, rather than after).

### Proof of Concept
Not directly executable without the full Orb hardware/pipeline stack, but the logical trace is:
1. A signup proceeds through `biometric_capture` and `biometric_pipeline` successfully (pipeline is `Some`).
2. `detect_fraud` returns `true`, setting `signup_reason = SignupReason::Fraud` at `src/plans/mod.rs:563-571`.
3. Despite this, execution continues into `build_pcp` and `upload_pcp_tier_0`/tier1/tier2 uploads at `src/plans/mod.rs:574-637`, uploading the user's iris/face biometric data to the backend.
4. Only afterward is `report_signup_reason` called, marking the signup as `SignupStatus::Fraud` in the debug report — after the biometric data has already left the device and reached the backend.

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

**File:** src/plans/mod.rs (L574-598)
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
```

**File:** src/plans/mod.rs (L599-637)
```rust
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

**File:** src/plans/mod.rs (L639-683)
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

    fn report_signup_reason(
        success: bool,
        signup_reason: SignupReason,
        debug_report: &mut debug_report::Builder,
    ) {
        if signup_reason == SignupReason::Failure {
            tracing::info!("User enrollment failed due to a failure in the pipeline");
            debug_report.signup_orb_failure();
        } else if signup_reason == SignupReason::Fraud {
            tracing::info!("User enrollment failed due to fraud");
            debug_report.signup_fraud();
        } else if success {
            debug_report.signup_successful();
            dd_incr!("main.count.signup.result.success.successful_signup");
        } else {
            tracing::info!("User enrollment failed");
            debug_report.signup_server_failure();
        }
    }
```

**File:** src/plans/personal_custody_package.rs (L463-486)
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
```
