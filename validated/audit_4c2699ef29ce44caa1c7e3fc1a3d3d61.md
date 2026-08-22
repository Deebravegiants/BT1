### Title
Local, unattested `user_centric_signup` success determination bypasses backend enrollment/uniqueness confirmation, enabling misattributed signup after biometric data upload - (File: src/plans/mod.rs)

### Summary
The Sherlock finding describes a race condition where `CrossChainRouter.borrowCrossChain()` mutates critical state (collateral tracking) and dispatches a message to a remote authority *before* that authority confirms the operation, while allowing the local actor (`redeem()`) to act on stale, unlocked state — resulting in an outcome (undercollateralization) that the remote confirmation was supposed to prevent. The structural root cause is: **irreversible local state changes are committed and treated as final before the actual verifying authority (source of truth) confirms the operation, and no lock prevents inconsistent use of that state in the interim.**

The same structural pattern exists in orb-core's signup pipeline: for `user_centric_signup` requests, `do_signup()` uploads the user's Personal Custody Package (biometric PCP tiers 0/1/2, keyed to the user's `id_commitment`/self-custody public key from the QR code) to the backend, and only *afterward* decides `success` purely from **local** state (`signup_reason`) — it never calls `enroll_user()` to obtain the backend's authoritative confirmation (uniqueness check, fraud verdict, duplicate detection) for this path.

### Finding Description
In `MasterPlan::do_signup` (`src/plans/mod.rs`), the flow is:
1. Biometric capture and pipeline run locally, producing `signup_reason` from `detect_fraud()`.
2. PCP tiers (biometric/identity data bound to `user_id`/`id_commitment`) are uploaded to the backend via `upload_pcp_tier_0` and `data_uploader` sends for tier 1/2 [1](#0-0) .
3. Only after that upload, the success outcome is computed: [2](#0-1) 

For the `user_centric_signup` branch, `success` is derived *exclusively* from the locally computed `signup_reason == SignupReason::Normal` — the authoritative `enroll_user()` call (which performs the backend `signup_post`/`signup_poll` round-trip that checks for duplicate/fraudulent signups, as seen in `src/plans/enroll_user.rs`) is skipped entirely [3](#0-2) .

Compounding this, `detect_fraud()` — the only local safeguard feeding `signup_reason` — has had all fraud checks removed: [4](#0-3) 

So for `user_centric_signup` flows, the orb: (a) uploads biometric/PCP data bound to a user identity to the backend, and (b) reports "success" to the UI/app/backend purely on the basis that the local pipeline produced a result and no (now-empty) fraud check flagged it — with no lock or wait on the backend's own uniqueness/duplicate verdict, analogous to `borrowCrossChain()` committing collateral-tracking state and dispatching a cross-chain message without a lock, while the destination confirmation is still pending.

This mirrors the reported root cause precisely: state is written (PCP upload to backend, `debug_report.enrollment_status` marked `Success`, UI shows success) based on an intermediate, unconfirmed local computation, with no mechanism to lock/roll back that state if the actual verifying entity (the backend enrollment/uniqueness check) would have rejected it.

### Impact Explanation
Because the backend's uniqueness/duplicate/fraud verdict (via `enroll_user`/`signup_poll`) is never consulted for `user_centric_signup`, a signup can be marked successful, and its biometric PCP data uploaded and attributed to a given `user_id`/`id_commitment`, even in situations where the backend would have rejected it as a duplicate or fraudulent enrollment. This can cause cross-signup state bleed / misattributed signup: the app/orb-side state, PCP upload, and success reporting become inconsistent with the backend's authoritative signup record, without any lock reconciling the two. This is analogous in class (state committed and acted upon before authoritative confirmation, no lock) to the reported H-21 issue.

### Likelihood Explanation
This path is reachable by any unprivileged end user going through a normal self-serve/user-centric signup (`qr_codes.user_data.user_centric_signup` is attacker/app-controlled data parsed from the user QR code and travels straight into this decision point), and does not require a malicious operator, node, or hardware access — it triggers on the standard signup flow whenever `user_centric_signup` is true and `ignore_user_centric_signups` is not set to override it.

### Recommendation
For `user_centric_signup` signups, do not derive `success` solely from local `signup_reason`; require the backend's authoritative confirmation (equivalent of `enroll_user`'s `signup_post`/`signup_poll` round trip) before uploading PCP data or reporting/persisting success, or lock/gate the PCP upload and success reporting behind that confirmation so that no state is treated as final prior to backend verification.

### Proof of Concept
Not applicable — this is a logic/config-path analysis based on the reachable code path in `do_signup()`; no live exploitation was performed. Confidence in reachability is based on the code shown; verifying the runtime default of `ignore_user_centric_signups` and full behavior of `orb_qr_link::UserData::user_centric_signup` parsing would require further review of `src/backend/config.rs` and `src/config.rs`, which were only partially inspected.

### Citations

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
