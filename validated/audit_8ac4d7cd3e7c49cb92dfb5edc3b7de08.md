This confirms the analog: the PCP (`info.json`'s `signup_reason` field) is permanently baked into the uploaded, encrypted, self-custody biometric package based on `signup_reason` computed from local `detect_fraud()` — and this upload to the backend happens **before** the authoritative backend health check (`enroll_user` → `signup_post`/`signup_poll`) confirms the actual outcome. The local `signup_reason` used for tagging is never corrected retroactively if the backend's independent adjudication disagrees.

### Title
Signup reason and biometric custody package are committed/tagged before backend enrollment verification completes, mirroring pre-health-check accounting - (File: src/plans/mod.rs)

### Summary
In `do_signup`, the Orb computes a client-side `signup_reason` (`Normal`/`Fraud`/`Failure`) from local `detect_fraud()` results and immediately uses it to build and permanently upload the encrypted Personal Custody Package (PCP) — including the salted-hash `signup_reason` field baked into `info.json` — to the backend, before the actual authoritative enrollment verification (`enroll_user`, which performs the real `signup_post`/`signup_poll` backend health check) ever runs and returns the final outcome.

### Finding Description
The order of operations in `do_signup` is:
1. `fraud_detected = self.detect_fraud(...)` and `signup_reason` are computed purely from local, Orb-side checks [1](#0-0) .
2. `build_pcp(...)` is called with this `signup_reason`, and the resulting tier0/tier1/tier2 packages — including `signup_reason` embedded and salted-hashed into `info.json` — are uploaded to the backend via `upload_pcp_tier_0` and `data_uploader` [2](#0-1) , with the reason value flowing into the package builder [3](#0-2) .
3. Only *after* this data has already been committed/uploaded does the code call the actual backend verification (`enroll_user`, which wraps `signup_post::request` + `signup_poll::request`) that determines the true, authoritative success/failure of the signup [4](#0-3) .

This is structurally the same bug class as the reported finding: a value ("fee"/"signup_reason") is recorded and committed to persistent storage based on a preliminary, non-authoritative check, before the real validation/health check (the backend's own fraud/duplicate detection during `signup_post`/`signup_poll`) completes. Just as the fee amount in the report is never corrected once the position health check invalidates it, the `signup_reason` baked into the uploaded PCP is never revised or retracted if the backend's own health check (`enroll_user`) later disagrees — e.g., it detects a duplicate or fraud that the Orb's local `detect_fraud` missed, or vice versa. The encrypted PCP tagged `"NORMAL"` has already left the Orb and reached backend storage by that point [5](#0-4) .

Additionally, for `user_centric_signup` flows, the final `success` determination bypasses the backend health check (`enroll_user`) entirely and is derived solely from the same preliminary local `signup_reason`, meaning the "recorded" (uploaded, tagged) state and the "reported success" state are both keyed off unverified local fraud detection [4](#0-3) . Note also that `detect_fraud` currently always returns `Ok(false)` in this build (`// FOSS: WE HAVE DELETED ALL FRAUD CHECKS`), meaning `signup_reason` is essentially always `Normal` client-side regardless of true risk [6](#0-5) .

### Impact Explanation
Biometric identity data (encrypted iris/face templates) can be uploaded and permanently tagged/labeled as a "Normal" signup in backend storage before the authoritative backend-side check (duplicate/fraud detection via `signup_post`/`signup_poll`) has run or concluded. If that backend check later rejects the signup (as fraud, duplicate, or otherwise invalid), the already-uploaded PCP retains its stale `"NORMAL"` tag and cannot be corrected after the fact — creating a mismatch between the local commitment (already-stored, misattributed metadata) and the true validation outcome, analogous to the fee-recording/health-check ordering flaw described in the report. This can result in misattributed signup metadata persisting in backend storage even for signups that are ultimately determined to be fraudulent or duplicated.

### Likelihood Explanation
Reachable by any unprivileged user going through a normal signup flow — no special privileges required beyond scanning a QR code and completing biometric capture. The ordering issue triggers on every signup where `build_pcp`/upload happens (which is virtually all signups), so the misattribution window exists on every attempt, though whether it results in an actually-detectable mismatch depends on the backend later disagreeing with the Orb's local (currently disabled) fraud determination.

### Recommendation
Defer building and uploading the PCP's `signup_reason`-tagged tier data until after the authoritative backend health check (`enroll_user`) has returned a final result, or ensure the uploaded package/metadata can be retroactively corrected/re-tagged (or the upload deferred/held) if the backend's own fraud/duplicate check disagrees with the Orb's local `detect_fraud` conclusion. At minimum, treat the backend's `enroll_user` result as authoritative and reconcile/correct any already-uploaded `signup_reason` metadata rather than leaving it as a one-shot, uncorrected commitment.

### Proof of Concept
1. A user completes biometric capture on the Orb; `detect_fraud` returns `false` locally (it is a no-op in this build), so `signup_reason = SignupReason::Normal` [1](#0-0) .
2. `build_pcp` bakes `"NORMAL"` into `info.json`'s salted-hash `signup_reason` field and the resulting encrypted PCP tiers are uploaded to the backend via `upload_pcp_tier_0`/`data_uploader` [3](#0-2) [5](#0-4) .
3. Only afterward does `enroll_user` invoke the real backend verification (`signup_post`/`signup_poll`), which may determine the signup is a duplicate, fraudulent, or otherwise invalid [7](#0-6) .
4. The already-uploaded PCP, permanently tagged `"NORMAL"`, is never retracted or corrected regardless of this later, authoritative result.

### Citations

**File:** src/plans/mod.rs (L563-571)
```rust
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

**File:** src/plans/mod.rs (L580-636)
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
```

**File:** src/plans/mod.rs (L639-656)
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

**File:** src/plans/personal_custody_package.rs (L459-486)
```rust
    fn make_info_json(&self, hashes: &mut BTreeMap<String, Digest>) -> Result<Vec<u8>> {
        fn salted_sha256(value: impl AsRef<str>, salt: impl AsRef<str>) -> Digest {
            digest(&SHA256, format!("{}{}", value.as_ref(), salt.as_ref()).as_ref())
        }
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

**File:** src/plans/enroll_user.rs (L146-176)
```rust
                        match response {
                            Ok(signup_poll::Response {
                                success: true,
                                error: None,
                                status: signup_poll::Status::Completed,
                            }) => {
                                tracing::info!("SIGNUP SUCCESS");
                                dd_incr!("main.count.http.user_enrollment.success.success_unique");
                                dd_incr!("main.count.http.user_enrollment.success.success");
                                return Status::Success;
                            }
                            Ok(signup_poll::Response {
                                success: false,
                                error: None,
                                status: signup_poll::Status::Completed,
                            }) => {
                                // This includes the following cases:
                                //   1. Backend duplicates
                                //   2. Backend legacy signup requests
                                //   3. Backend inflight matches
                                //   4. Backend detected fraud
                                //   5. Orb agent, internal, capture or pipeline failures
                                //   6. Orb detected fraud
                                tracing::info!("SIGNUP FAIL");
                                dd_incr!("main.count.http.user_enrollment.success.failed");
                                dd_incr!(
                                    "main.count.signup.result.failure.user_enrollment",
                                    "type:failure"
                                );
                                return Status::SignupVerificationNotSuccessful;
                            }
```
