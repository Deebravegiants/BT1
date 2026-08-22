Based on the investigation, this is a confirmed and reachable analog: `user_centric_signup` bypasses the backend enrollment/duplicate-check request entirely, deciding "success" locally on the orb using only local fraud-check state (which is itself a no-op FOSS stub), while still uploading the full Personal Custody Package (iris codes, PCP tiers, self-custody keys) to the backend/storage. This mirrors the double-spend root cause: a state/side-effect (data upload + "success" outcome) is finalized without the authoritative ledger-equivalent (the backend's `signup_post`/`signup_poll` dedup and validation) ever being invoked or subtracted/checked.

### Title
Unauthorized signup finalization bypassing backend enrollment verification when `user_centric_signup` is set - (File: `src/plans/mod.rs`)

### Summary
In `MasterPlan::do_signup`, when the user's QR-derived `UserData.user_centric_signup` flag is `true` (and `ignore_user_centric_signups` is not set), the orb marks the signup as successful/failed purely from locally computed `signup_reason`, without ever calling `enroll_user::Plan::run`, which is the only code path that submits the signup to the backend via `signup_post::request`/`signup_poll::request` and thereby performs backend-side duplicate/fraud verification and creates the authoritative signup record. [1](#0-0) 

### Finding Description
The flow in `do_signup` first builds and uploads the Personal Custody Package (iris codes, self-custody keys, biometric data) regardless of `user_centric_signup`: [2](#0-1) 

It then computes `success` via one of two mutually exclusive branches: [1](#0-0) 

For the `user_centric_signup` branch, `success` is derived purely from the local `signup_reason` (which itself only depends on the on-device, currently-empty fraud-check engine, `N_FRAUD_CHECKS = 0`): [3](#0-2) [4](#0-3) 

By contrast, the non-user-centric path calls `enroll_user`, which posts to the backend (`signup_post::request`) and polls for completion (`signup_poll::request`) — this is the only place where server-side duplicate detection ("Backend duplicates", "Backend inflight matches") happens, as documented in the comment: [5](#0-4) 

Because `user_centric_signup` is a boolean sourced from the *user's own QR-code-linked backend data* (`orb_qr_link::UserData`) that the orb trusts to decide whether to skip this backend enrollment/dedup call entirely, an unprivileged user who controls this flag on their own signup path can cause the orb to treat a signup as complete/successful without the backend's authoritative dedup/fraud pipeline ever running, all while still uploading (and thus registering in storage) the user's full iris/biometric PCP data. [6](#0-5) 

### Impact Explanation
This allows unauthorized or misattributed signup completion: the orb can report `Status::Success`/`signup_successful()` and finalize a signup (uploading biometric PCP tiers 0–2) without the backend ever validating the enrollment through `signup_post`, i.e., the equivalent of the "collateral" (backend dedup ledger) never being decremented/checked while the "loan" (successful signup + biometric upload) is still granted. This is analogous to the double-spend class: a locally-derived success bypasses the authoritative state update, enabling repeated or fraudulent signups for the same identity to be marked successful and have data persisted without ever registering with the source-of-truth signup ledger.

### Likelihood Explanation
Likelihood is high on any orb build where the backend serves `user_centric_signup: true` for the scanned user QR code and `ignore_user_centric_signups` is not force-enabled, since the branch is a straightforward boolean check evaluated on every signup with no cross-verification against the backend's enrollment/dedup response.

### Recommendation
Do not treat `user_centric_signup` as sufficient to skip the backend enrollment/dedup verification. Either require the backend confirmation (equivalent of `signup_post`/`signup_poll`) to still run for user-centric signups before setting `success = true`, or gate the local success only after confirming with the backend elsewhere that no duplicate/fraud state exists for this signup, so that the authoritative source of truth (the same check performed at [5](#0-4)  and [1](#0-0) ) is never bypassed based solely on client/app-controlled QR data.

### Proof of Concept
1. Scan an operator QR code, then a user QR code whose backend-provided `UserData.user_centric_signup` is `true` (as returned from `user_status::request`, see `orb_qr_link::UserData.user_centric_signup` at [6](#0-5) ).
2. Proceed through capture and biometric pipeline normally so `signup_reason == SignupReason::Normal`.
3. Observe that `do_signup` takes the branch at [7](#0-6) , setting `success = true` and `debug_report.enrollment_status(enroll_user::Status::Success)` without ever calling `signup_post::request`/`signup_poll::request`.
4. Repeat the same biometric capture (e.g., same iris) with a fresh `signup_id` and the same `user_centric_signup: true` QR flow; because the backend's `signup_post` dedup logic (`enroll_user.rs` lines 157–176) is never invoked, the orb-side flow reports success and re-uploads the full PCP again with no backend-side duplicate rejection observed by the orb.

### Citations

**File:** src/plans/mod.rs (L572-637)
```rust
        let user_id = qr_codes.user_qr_code.user_id.clone();
        let user_centric_signup = qr_codes.user_data.user_centric_signup;
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

**File:** src/plans/fraud_check.rs (L10-13)
```rust
/// Number of fraud checks performed by the Fraud Check Engine.
/// FOSS: This is set to 0 because we manually deleted all fraud checks
const N_FRAUD_CHECKS: usize = 0;

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
