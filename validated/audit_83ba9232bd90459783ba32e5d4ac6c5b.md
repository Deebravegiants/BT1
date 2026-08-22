### Title
Biometric Data (Personal Custody Package) Is Uploaded and Retained Even When Enrollment Ultimately Fails or Reverts, With No Compensating Delete/Redaction Mechanism - (File: `src/plans/mod.rs`, `src/plans/enroll_user.rs`)

### Summary
`MasterPlan::do_signup` uploads the user's encrypted biometric Personal Custody Package (PCP, tier0/tier1/tier2 — raw iris images, normalized iris codes, face embeddings, secure-element-signed hashes) to the backend/S3 *before* the final enrollment decision is known, and this upload is never retried or reverted afterward. This mirrors the reported paymaster bug class: an earlier "execution phase" (here, the irreversible upload of sensitive biometric data) commits state, while the later "validation/settlement phase" (`enroll_user::Plan::run`, i.e. `signup_post`/`signup_poll`) can independently fail or revert (network error, signature calculation error, server error, retries exhausted) without any mechanism to undo or reclaim what was already committed in the earlier phase.

### Finding Description
In `do_signup` (`src/plans/mod.rs`), the sequence is:
1. `biometric_pipeline` runs and `detect_fraud` determines `signup_reason`. [1](#0-0) 
2. `build_pcp` builds the tier0/tier1/tier2 packages (containing raw IR images, normalized iris/mask data, Hyrax commitments, face embeddings, and secure-element-signed hashes) via `personal_custody_package::Plan`. [2](#0-1) 
3. `upload_pcp_tier_0` is awaited, and — independently — tier1/tier2 are pushed into `orb.data_uploader`'s queue for asynchronous upload, all of this happening *before* the enrollment/verification call is made. [3](#0-2) 
4. Only afterward does the code call `self.enroll_user(...)`, which wraps `enroll_user::Plan::run`, performing the actual `signup_post`/`signup_poll` request/response cycle that determines whether the signup is ultimately accepted. [4](#0-3) 

`enroll_user::Plan::run` can fail in numerous ways after biometric data has already left the device: signature calculation errors, network/client errors, server errors, exhausted retries, or `SignupVerificationNotSuccessful` (backend duplicate/fraud/inflight match detection). [5](#0-4) [6](#0-5) [7](#0-6) 

None of these failure paths trigger any deletion, retraction, or invalidation request for the already-uploaded PCP tier0/tier1/tier2 data. The upload (`data_uploader::wait_queues` and `send`) is fire-and-forget relative to the enrollment outcome — exactly analogous to the paymaster's "temporarily holds funds"/"mode 1" case where an action taken in an earlier phase (execution/pre-payment) is not undone or reconciled when the later phase (postOp/settlement) reverts. The code even contains an acknowledged edge case around missing iris/mask shares "if we detect fraud or some other issue," showing the PCP-building path is exercised in fraud/failure scenarios too. [8](#0-7) 

### Impact Explanation
Because encrypted biometric data (iris images, normalized iris/mask codes, face thumbnails/embeddings) is durably transmitted to backend storage before the enrollment/verification transaction concludes, a failed, rejected, or fraud-flagged signup still results in retained biometric data at the backend with no built-in mechanism on the orb side to request deletion or to mark it for erasure. This is a biometric-data retention/disclosure concern: data belonging to a user whose signup was never validated (network failure, signature failure, server error, or detected fraud/duplicate) persists exactly as if the signup had succeeded, absent any explicit backend-side purge tied to the failure status.

### Likelihood Explanation
This occurs on any of the enumerated non-`Success` `enroll_user::Status` outcomes (`SignatureCalculationError`, `ServerError`, `Error`, `SignupVerificationNotSuccessful`, retry exhaustion), which are reachable through ordinary network flakiness, backend-side duplicate/fraud detection, or signature failures — none of which are rare or require a malicious actor. The upload-before-verification ordering is unconditional in `do_signup`, so likelihood of hitting this state is directly tied to the (non-trivial) real-world failure rate of `signup_post`/`signup_poll`.

### Recommendation
Reorder the flow so the biometric PCP data is only durably persisted after enrollment success is confirmed, or, if upload-before-confirmation is required for performance/UX reasons, implement a compensating action: on any non-`Success` `enroll_user::Status`, issue an explicit deletion/invalidation request for the already-uploaded PCP tier0/tier1/tier2 objects (analogous to the report's recommended `withdrawERC20()`-style redemption path), and track upload state so it can be reconciled/cleaned up once the terminal enrollment status is known.

### Proof of Concept
1. Start a signup; `build_pcp` and `upload_pcp_tier_0` execute and succeed in uploading tier0 (and, for `pcp_version >= 3`, tier1/tier2) biometric data. [3](#0-2) 
2. Simulate a downstream failure in `enroll_user::Plan::run`, e.g. a `reqwest` client error on `signup_post`, or `POLL_STATUS_COUNT` polls elapsing without a terminal `Completed` status, or a `SignatureCalculationError`. [9](#0-8) 
3. Observe that `do_signup` simply returns `Ok(result)` with `success = false`; no call is made to remove, revoke, or invalidate the PCP data already sent via `upload_pcp_tier_0` / `data_uploader` queue in step 1. [4](#0-3) 
4. The user's raw/encrypted biometric package remains stored on the backend despite the signup never being validated/completed — the "stuck"/uncompensated state described in the source report, applied to biometric retention instead of ERC20 tokens.

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

**File:** src/plans/mod.rs (L599-636)
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

**File:** src/plans/enroll_user.rs (L72-88)
```rust
    pub async fn run(self, orb: &mut Orb) -> Status {
        let user_qr_code = self.user_qr_code.clone();
        let signature = if let Some(p) = self.pipeline.cloned() {
            match task::spawn_blocking(move || make_signature(&user_qr_code, &p)).await {
                Ok(Ok(signature)) => Some(signature),
                Ok(Err(err)) => {
                    tracing::error!("Failed to calculate signature: {err:?}");
                    return Status::SignatureCalculationError;
                }
                Err(err) => {
                    tracing::error!("Failed to calculate signature: {err:?}");
                    return Status::SignatureCalculationError;
                }
            }
        } else {
            None
        };
```

**File:** src/plans/enroll_user.rs (L157-176)
```rust
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

**File:** src/plans/enroll_user.rs (L255-286)
```rust
                Err(err) => {
                    tracing::error!("SIGNUP ERROR: {:?}", err);
                    dd_incr!(
                        "main.count.http.user_enrollment.error.network_error",
                        "error_type:normal"
                    );
                    if let Some(err_downcast) = err.downcast_ref::<reqwest::Error>() {
                        if let Some(status) = err_downcast.status() {
                            if status.is_client_error() {
                                dd_incr!(
                                    "main.count.signup.result.failure.user_enrollment",
                                    "type:network_error",
                                    "subtype:signup_request"
                                );
                                log_decoding_error(&err);
                                return Status::Error;
                            }
                        }
                    }
                    if i == RETRIES_COUNT - 1 {
                        dd_incr!(
                            "main.count.signup.result.failure.user_enrollment",
                            "type:network_error",
                            "subtype:signup_request"
                        );
                        log_decoding_error(&err);
                    }
                }
            }
        }
        dd_incr!("main.count.signup.result.failure.user_enrollment", "type:max_retry_exceeded");
        Status::Error
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
