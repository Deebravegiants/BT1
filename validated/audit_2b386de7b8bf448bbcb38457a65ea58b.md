### Title
Signup enrollment success is committed locally before the backend's authoritative fraud/duplicate check ever runs, front-running the "flag" analog - ([File: src/plans/mod.rs])

### Summary
In `orb-core`, the on-chain `flag()`/`onFlag()` gate that the external report is about maps to the backend's authoritative fraud/duplicate-detection round-trip performed by `enroll_user::Plan::run` (`signup_post::request` + `signup_poll::request`). For signups where `user_centric_signup` is true, `MasterPlan::do_signup` skips this backend round-trip entirely and instead derives the enrollment `success` value purely from the orb's own local `signup_reason`, which is itself computed from a client-side `detect_fraud()` call before the PCP tier-0/1/2 data has already been irreversibly uploaded to the backend.

### Finding Description
`do_signup` computes `signup_reason` locally from `detect_fraud()` and then, regardless of that outcome, immediately begins uploading the personal custody package (PCP) tiers to the backend via `data_uploader`: [1](#0-0) [2](#0-1) 

After the upload, the code decides whether the signup counts as successful. For the `user_centric_signup` branch, it never calls the backend's `enroll_user` flow (which is the actual authoritative check — server-side duplicate detection, "inflight matches", and backend fraud detection, gated behind polling `signup_poll`): [3](#0-2) 

Compare this to the non-`user_centric_signup` path, where `enroll_user::Plan::run` performs a real network round trip (`signup_post::request` then repeated `signup_poll::request` polling) and only returns `Status::Success` once the backend confirms no duplicate/fraud condition exists: [4](#0-3) 

The local `detect_fraud()` function that gates the `user_centric_signup` shortcut is a client-only check that runs *before* any server round trip and, in this build, is a no-op (`N_FRAUD_CHECKS = 0`, always returns `false`): [5](#0-4) [6](#0-5) 

This is structurally the same bug class as the `VoteKickPolicy` report: an authoritative gate (`onFlag`/backend fraud+duplicate check) is supposed to run and determine whether an action (`unstake`/enrollment `success`) is legitimate, but the action's outcome is instead finalized by a path that races ahead of — or entirely bypasses — that authoritative check. Here, biometric data upload and the "success" determination both complete without ever giving the backend's `signup_poll`-based fraud/duplicate detection a chance to reject the signup, exactly as `unstake()`/`forceUnstake()` can complete before `flag()`/`onFlag()` runs.

`user_centric_signup` itself is sourced from `authenticated_app_data` returned by the backend's `/status` endpoint and is nominally protected by a hash-verification step (`user_data.verify(user_data_hash)`), gated by `#[cfg(not(feature = "skip-user-qr-validation"))]`: [7](#0-6) 
This means in the default build this flag is intended to be attested by the backend and not directly attacker-forgeable client-side — I could not fully verify the cryptographic strength/scope of `verify()` in the time available (its implementation was not indexed), so I cannot conclusively state whether the flag can be manipulated by a malicious app/client. This is the main uncertainty in this finding.

### Impact Explanation
If `user_centric_signup` is true (whether by legitimate backend attestation or by any weakness in the `verify()` check), a signup can be marked `Success` in the debug report and PCP data already uploaded, without the backend's real fraud/duplicate-detection pipeline (`signup_post`/`signup_poll`, which normally catches "Backend duplicates", "Backend inflight matches", "Backend detected fraud") ever being consulted. This is analogous to a target evading slashing by unstaking before `flag()` — the "kick" mechanism for detecting bad signups (backend fraud/duplicate confirmation) never gets a chance to run before the data is durably persisted and the signup is reported as successful.

### Likelihood Explanation
Reachability depends entirely on the trustworthiness of the `user_centric_signup` flag, which is intended to be backend-attested and hash-verified against the QR code. Absent a break in that verification (not confirmed reachable by an unprivileged user in this review), this is a design choice that removes a fraud-detection checkpoint for a whole class of signups (app/self-serve signups) rather than a directly exploitable client-side race. This significantly limits confidence relative to the on-chain original, where any staker can literally race a transaction against `flag()`.

### Recommendation
Do not let `user_centric_signup` fully bypass the backend's authoritative post-signup confirmation (`signup_post`/`signup_poll`). At minimum, always perform the backend round trip (even in a lightweight/async form) before marking `debug_report`/`SignupResult::success` as true, so the backend's duplicate/fraud checks are always given the opportunity to reject a signup, mirroring how `flag()` should always have the opportunity to run against a stake before it's released.

### Proof of Concept
Not independently reproducible from static review alone: reaching this path requires the backend to return `authenticated_app_data.user_centric_signup = true` (or a bypass of `user_data.verify(user_data_hash)`), which I could not fully confirm is attacker-reachable without access to the `verify()` implementation and backend attestation scheme. The concrete code-path evidence is: `do_signup` at `src/plans/mod.rs:639-656` sets `success = signup_reason == SignupReason::Normal` and calls `debug_report.enrollment_status(...)` directly, skipping the `enroll_user()` call (`src/plans/mod.rs:646-656` vs. `src/plans/enroll_user.rs:90-176`) that would otherwise perform the backend fraud/duplicate confirmation before reporting success.

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

**File:** src/plans/enroll_user.rs (L90-176)
```rust
        let signup_id = self.signup_id.to_string();
        for i in 0..RETRIES_COUNT {
            let response = signup_post::request(
                signature.as_ref(),
                &signup_id,
                &self.operator_qr_code,
                &self.user_qr_code,
                &self.s3_region_str,
                self.capture,
                self.pipeline,
                self.signup_reason,
            )
            .await;
            match response {
                Ok(signup_post::Response {
                    software_version_status:
                        versions @ (signup_post::SoftwareVersionStatus::Allowed
                        | signup_post::SoftwareVersionStatus::Deprecated
                        | signup_post::SoftwareVersionStatus::Unknown
                        | signup_post::SoftwareVersionStatus::Empty),
                }) => {
                    if matches!(versions, signup_post::SoftwareVersionStatus::Deprecated) {
                        tracing::warn!("Orb component versions are deprecated");
                        notify_failed_signup(
                            orb,
                            Some(SignupFailReason::SoftwareVersionDeprecated),
                        );
                    }
                    if matches!(versions, signup_post::SoftwareVersionStatus::Empty)
                        || matches!(versions, signup_post::SoftwareVersionStatus::Unknown)
                    {
                        tracing::warn!("Backend doesn't know this software version.");
                        tracing::warn!(
                            "This is considered a deprecated version on staging builds, and \
                             blocked on prod."
                        );
                        #[cfg(feature = "stage")]
                        notify_failed_signup(
                            orb,
                            Some(SignupFailReason::SoftwareVersionDeprecated),
                        );
                        #[cfg(not(feature = "stage"))]
                        return Status::SoftwareVersionUnknown;
                    }
                    for i in 0..POLL_STATUS_COUNT {
                        sleep(POLL_STATUS_INTERVAL).await;
                        #[cfg(not(feature = "ui-test-successful-signup"))]
                        let response = signup_poll::request(&signup_id).await;

                        #[cfg(feature = "ui-test-successful-signup")]
                        let response: Result<signup_poll::Response> = Ok(signup_poll::Response {
                            status: signup_poll::Status::Completed,
                            success: true,
                            error: None,
                        });

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

**File:** src/backend/user_status.rs (L163-212)
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

        let BackendKeys {
            iris:
                BackendKey {
                    public_key: backend_iris_public_key,
                    encrypted_private_key: backend_iris_encrypted_private_key,
                },
            normalized_iris:
                BackendKey {
                    public_key: backend_normalized_iris_public_key,
                    encrypted_private_key: backend_normalized_iris_encrypted_private_key,
                },
            face:
                BackendKey {
                    public_key: backend_face_public_key,
                    encrypted_private_key: backend_face_encrypted_private_key,
                },
            tier2: backend_tier2,
        } = backend_keys;
        let backend_tier2_public_key =
            backend_tier2.as_ref().map(|backend_tier2| backend_tier2.public_key.as_str());
        let backend_tier2_encrypted_private_key =
            backend_tier2.as_ref().map(|backend_tier2| backend_tier2.encrypted_private_key.clone());
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
