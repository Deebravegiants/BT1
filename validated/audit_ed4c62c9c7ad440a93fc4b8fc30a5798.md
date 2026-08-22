### Title
Biometric custody package (iris code shares) is permanently uploaded to backend/MPC storage *before* the backend verifies signup uniqueness/fraud, so raw biometric data is retained even when the signup is ultimately rejected - (File: `src/plans/mod.rs`)

### Summary
The ERC-777 finding is a "credit-before-verify" ordering bug: shares (`_mint`) are issued before the asset transfer that is supposed to back them is confirmed, letting an attacker re-enter and double-credit. `orb-core`'s signup flow has the same ordering flaw at the biometric-data layer: the Personal Custody Package (PCP), which contains the user's encrypted iris code shares, is built and permanently uploaded to backend/MPC storage nodes *before* the backend actually confirms the signup is valid (unique, non-fraudulent). The "verification" step (`enroll_user`, which performs `signup_post` + `signup_poll`) runs strictly after the irreversible upload.

### Finding Description
In `do_signup` (`src/plans/mod.rs`), the sequence is:

1. `detect_fraud` is called, but all on-orb fraud checks have been removed (`// FOSS: WE HAVE DELETED ALL FRAUD CHECKS`), so it always returns `false`. [1](#0-0) 

2. Regardless of that result, the biometric custody package is built and its tiers are uploaded to the backend/custody storage immediately: [2](#0-1) 

3. Only *after* the iris code shares (tier0/1/2) have already been transmitted and stored does the code call `enroll_user`, which is the step that actually asks the backend to validate the signup (`signup_post`) and poll for the real verdict (`signup_poll`) — including backend-side duplicate detection and fraud detection, as explicitly documented in the comment inside `enroll_user::run`: [3](#0-2) [4](#0-3) 

So the "asset transfer" (irreversible upload of raw biometric material to storage/MPC nodes) happens before the "mint" is validated (server-side confirmation that the signup is legitimate/unique). This is the exact inversion recommended against in the report's mitigation ("transfer first, then credit"): here the sensitive artifact is persisted first, and the legitimacy check happens second.

### Impact Explanation
Even when the backend later determines the signup is a duplicate, a fraud attempt, or otherwise invalid (`SIGNUP FAIL`/`Backend detected fraud`/`Backend duplicates`, per the comment in `enroll_user.rs:162-168`), the user's iris code shares have already been irreversibly uploaded to custody/MPC storage in `upload_pcp_tier_0` and the tier1/tier2 sends. There is no compensating deletion/rollback path invoked on a failed `enroll_user::Status` for already-uploaded tiers. This results in biometric data being retained on backend infrastructure despite the enrollment ultimately being rejected — a retention/disclosure issue for data that should only be persisted for legitimate, verified signups.

### Likelihood Explanation
This triggers on every normal signup attempt that later fails verification (duplicate iris, backend-side fraud determination, or any of the `SignupVerificationNotSuccessful`/`ServerError` outcomes in `enroll_user::run`), since the upload always precedes the verification call in `do_signup`. No special privileges are needed — any user going through the standard signup flow can be affected, and because local (`detect_fraud`) checks are disabled, the backend check is the *only* gate, yet it runs after data has already left the device.

### Recommendation
Re-order the flow so that biometric custody-package upload only occurs after `enroll_user` (or an equivalent backend pre-check) confirms the signup is accepted/unique, or gate the tier1/tier2 uploads and treat tier0 upload as provisional/rejectable, with an explicit backend-side purge triggered by a non-success `enroll_user::Status`. Alternatively, perform the uniqueness/fraud check first and only build/upload the PCP once the signup is confirmed legitimate, mirroring the recommended "transfer assets, then mint" ordering from the referenced report.

### Proof of Concept
1. Initiate a signup with an iris that is already enrolled elsewhere (or trigger any backend-side duplicate/fraud condition).
2. Observe that `do_signup` calls `build_pcp` → `upload_pcp_tier_0` → tier1/tier2 uploads (`src/plans/mod.rs:574-636`) unconditionally, before `enroll_user` runs.
3. `enroll_user::Plan::run` subsequently returns `Status::SignupVerificationNotSuccessful` (or `ServerError`) per the "Backend duplicates"/"Backend detected fraud" cases documented at `src/plans/enroll_user.rs:157-176`.
4. Despite the failed verdict, the iris code shares uploaded in step 2 remain persisted on the backend/custody storage with no rollback triggered by the failed status in `after_signup`/`report_signup_reason` (`src/plans/mod.rs:665-683`).

### Citations

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
