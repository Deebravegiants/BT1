This confirms the analog. The `user_centric_signup` flag comes from `orb_qr_link::UserData` embedded in the user's QR-code-linked backend payload, which is cryptographically verified via `user_data.verify(user_data_hash)` against the QR code's `user_data_hash`. This means the flag itself is authenticated, but its consequence — skipping the backend's authoritative signup verification — creates the same class of premature-attribution flaw described in the report.

## Finding

### Title
Local success attribution bypasses backend uniqueness/fraud verification for user-centric signups - (File: src/plans/mod.rs)

### Summary
In `MasterPlan::do_signup`, when a signup is `user_centric_signup` (and `ignore_user_centric_signups` is not set), the Orb never calls `signup_post`/`signup_poll` against the backend to obtain the authoritative uniqueness/duplicate/fraud verdict. Instead it locally derives `enroll_user::Status::Success` purely from the on-device `signup_reason`, exactly mirroring the reported PCV bug pattern: an entity's "verified/owned" state is set from a local heuristic/proxy instead of the atomic, authoritative confirmation event.

### Finding Description
`do_signup` computes `signup_reason` from the biometric pipeline result and `detect_fraud`: [1](#0-0) 

In this FOSS build, `detect_fraud` is a stub that always returns `Ok(false)` because "WE HAVE DELETED ALL FRAUD CHECKS": [2](#0-1) 

Personal Custody Package (biometric) data is uploaded to the backend regardless of path: [3](#0-2) 

Then, the enrollment result is decided: [4](#0-3) 

When `user_centric_signup` is true, the branch at lines 639-645 sets `enroll_user::Status::Success` directly from `signup_reason == SignupReason::Normal`, completely bypassing `enroll_user::Plan::run`, which is the code path that actually calls `signup_post::request` (POST to `/api/v2/signups/{id}`) and polls `signup_poll::request` for the backend's real verdict — including duplicate-iris detection ("Backend duplicates", "Backend inflight matches", "Backend detected fraud"): [5](#0-4) 

`user_centric_signup` is set from `orb_qr_link::UserData` returned by `backend::user_status::do_request`, and is validated only via a QR-code hash check (`user_data.verify(user_data_hash)`), not tied to any backend-side confirmation that the *app* (rather than the orb) will perform the uniqueness verification for this specific signup: [6](#0-5) [7](#0-6) 

This is structurally identical to the reported bug class: a resource/state ("verified, enrolled signup" — analogous to "protocol-owned FEI") is attributed based on a local proxy computed before/without the authoritative atomic check (the backend's `signup_post`/`signup_poll` duplicate/fraud verdict, analogous to the FEI mint/burn happening in the same transaction as the deposit/withdraw). The debug report and UI ("SignupSuccess") reflect this locally-asserted success, and the `after_signup` flow marks the signup as completed and successful without the backend-authoritative confirmation step, and the biometric PCP data has already been uploaded to the backend under this signup ID/user ID before this local success determination.

### Impact Explanation
If the on-device signup can be pushed through this branch (`user_centric_signup == true`, fraud checks deleted/stubbed, `ignore_user_centric_signups == false`), a signup is marked as `Success`/enrolled locally, feedback is shown to the user (`orb.ui.signup_success()`), and `SignupEnded{success: true}` is relayed — all without ever obtaining the backend's authoritative confirmation that this iris/face biometric is unique (not a duplicate enrollment) or free of backend-side fraud signals. This is a misattributed-signup / cross-signup state bleed risk: a duplicate or fraudulent signup could be locally recorded and reported as a successful, verified, unique enrollment despite the true uniqueness-verification transaction with the backend never taking place for that path.

### Likelihood Explanation
Reaching this path requires only that the QR-code-linked backend user data field `user_centric_signup` be `true`, which is an authenticated-but-normal field of the app-supplied data (not a privileged operator/hardware condition), combined with the deleted/stubbed local fraud engine (`N_FRAUD_CHECKS = 0` in this FOSS build) always returning "no fraud detected." No privileged access or hardware tampering is required beyond a standard signup flow with a QR code presenting `user_centric_signup: true`.

### Recommendation
Do not allow local `signup_reason == Normal` to be treated as final enrollment success for `user_centric_signup` flows. Require an explicit, authoritative backend confirmation (equivalent to `signup_post`/`signup_poll`, or a dedicated backend endpoint acknowledging that the app-side flow completed the uniqueness/fraud check) before setting `enroll_user::Status::Success` and before marking `signup_status` as `Success` in the debug report, mirroring the recommendation in the source report: keep the "state considered final/attributed" determination tied to the same authoritative transaction that performs the uniqueness/fraud verification, rather than a local proxy.

### Proof of Concept
1. Provide a QR code whose linked backend user data (`orb_qr_link::UserData`) sets `user_centric_signup: true` (as already exercised by the `skip-user-qr-validation` test helper, which constructs exactly such data: `user_centric_signup: true`). [8](#0-7) 
2. Complete a biometric capture and pipeline run so that `pipeline.is_some()`; since `detect_fraud` always returns `Ok(false)` in this build, `signup_reason` becomes `SignupReason::Normal`.
3. `do_signup` reaches the `user_centric_signup` branch and sets `enrollment_status = enroll_user::Status::Success` and `success = true` without ever invoking `enroll_user::Plan::run` (i.e., without any `signup_post`/`signup_poll` round trip to the backend). [4](#0-3) 
4. The signup is reported as `SignupStatus::Success` and UI shows `signup_success()`, even though no backend-side duplicate/fraud verdict for this specific enrollment was ever obtained by the Orb.

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

**File:** src/backend/user_status.rs (L100-107)
```rust
    let authenticated_app_data = Some(orb_qr_link::UserData {
        identity_commitment: "test".to_string(),
        self_custody_public_key: BASE64.encode(public_key.as_ref()),
        data_policy: orb_qr_link::DataPolicy::OptOut,
        pcp_version: 2,
        user_centric_signup: true,
        orb_relay_app_id: Some(format!("test-skip-user-qr-validation-{}", ORB_ID.to_string())),
    });
```

**File:** src/backend/user_status.rs (L163-179)
```rust
    if let (Some(backend_keys), Some(user_data)) = (backend_keys, authenticated_app_data) {
        tracing::info!("User QR-data: {user_data:?}");

        #[cfg(not(feature = "skip-user-qr-validation"))]
        {
            let Some(user_data_hash) = &qr_code.user_data_hash else {
                tracing::error!(
                    "image_self_custody is provided by backend, but got no user_data_hash from \
                     QR-code"
                );
                return Ok(None);
            };
            if !user_data.verify(user_data_hash) {
                tracing::error!("user_data verification failure");
                return Ok(None);
            }
        }
```

**File:** src/backend/user_status.rs (L203-212)
```rust
        let orb_qr_link::UserData {
            identity_commitment,
            self_custody_public_key: user_public_key,
            #[cfg(feature = "internal-data-acquisition")]
            data_policy,
            pcp_version,
            user_centric_signup,
            orb_relay_app_id,
            ..
        } = user_data;
```
