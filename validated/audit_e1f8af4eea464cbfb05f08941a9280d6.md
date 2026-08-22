### Title
Signup declared successful without backend confirmation when `user_centric_signup` is set - ([File: src/plans/mod.rs])

### Summary
In the Amphor report, `_claimDeposit`/`_claimRedeem` finalize a user-facing outcome using data from an epoch that was never confirmed as "settled" by the authoritative source (the vault's own settlement logic), resulting in an outcome (claimed shares/assets) that doesn't reflect the true, confirmed state. The orb-core analog is in `MasterPlan::do_signup`, where a signup's success/failure is finalized as `SignupReason::Normal` locally, on the orb, without ever validating that outcome against the backend's authoritative signup record when `user_centric_signup` is `true`, unlike the normal path which polls the backend until it reports `Status::Completed`.

### Finding Description
In the normal ("orb-centric") signup path, `Plan::run` in `src/plans/enroll_user.rs` posts the signup to the backend via `signup_post::request` and then polls `signup_poll::request` in a loop until the backend explicitly reports `Status::Completed` with `success: true` [1](#0-0) . Only this backend-confirmed ("settled") status is treated as `Status::Success`.

However, when `user_centric_signup` is `true` (a flag sourced from the user's QR-code/backend user-status response, see `UserData::user_centric_signup` at [2](#0-1) ), `do_signup` in `src/plans/mod.rs` completely bypasses `enroll_user` (and therefore the `signup_post`/`signup_poll` confirmation loop) and instead derives `success` purely from the local `signup_reason` computed from on-orb pipeline/fraud results:

```
let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups
{
    debug_report.enrollment_status(match signup_reason {
        SignupReason::Normal => enroll_user::Status::Success,
        _ => enroll_user::Status::Error,
    });
    signup_reason == SignupReason::Normal
} else {
    ...
};
``` [3](#0-2) 

This mirrors the Amphor bug's root cause: an operation (claim / signup-completion) is finalized using state (`signup_reason == Normal`) that was never checked against the source-of-truth settlement mechanism (`signup_poll` reaching `Status::Completed`). The orb locally marks the signup as `signup_successful()` (`report_signup_reason`, [4](#0-3) ), drives `debug_report.enrollment_status`, and the resulting `result.success` flag is what feeds `after_signup`'s `SignupEnded { success, .. }` relay message to the app and the UI's `signup_success()` display (`ui_complete_signup`, [5](#0-4) ) — all before, or without ever, confirming with the backend that the corresponding enrollment/PCP submission was accepted.

Note that PCP tier-0/1/2 packages are already uploaded to the backend prior to this success determination (`upload_pcp_tier_0`, `data_uploader::Input::Pcp`, [6](#0-5) ), so the biometric identity submission has occurred, but whether the backend actually accepted/settled it (duplicate rejection, fraud rejection, inflight match, legacy request, etc. — the exact categories enumerated in the backend-confirmed path's comment at [7](#0-6) ) is never verified for user-centric signups.

### Impact Explanation
This can cause the orb to report and relay a successful, completed signup (`SignupEnded { success: true }`, UI ring shows success) even in cases where the backend would have rejected the corresponding enrollment (e.g., a duplicate signup, an inflight match, or a backend fraud determination) — outcomes that the backend-confirmed path explicitly guards against via `signup_poll`. This is a state/settlement validation gap analogous to the Amphor "unsettled epoch" claim bug: an unprivileged app/user-driven flag (`user_centric_signup`, ultimately controlled by data returned for the user's own QR code/session) causes the orb to skip the authoritative confirmation step and instead trust local, unconfirmed state to declare success, potentially leading to misattributed/duplicate signup completion being reported as valid.

### Likelihood Explanation
The `user_centric_signup` flag is read from backend-provided `UserData` tied to the scanned user QR code [8](#0-7)  and is used directly to gate which success-determination code path executes in `do_signup`, with only a single global config flag (`ignore_user_centric_signups`) as an override [9](#0-8) . Every signup for which the backend marks the session as user-centric goes through this locally-determined success path, so the missing-confirmation condition is reached on the normal, everyday self-serve signup flow rather than an edge case.

### Recommendation
For `user_centric_signup` flows, still perform the backend-confirmation step (equivalent to the `signup_post`/`signup_poll` loop) before declaring `success`, or otherwise require an explicit backend acknowledgment tied to the specific `signup_id`/PCP upload before setting `enroll_user::Status::Success` and emitting `SignupEnded { success: true }`. This mirrors the Amphor fix of validating that the relevant epoch/request has actually settled before honoring a claim.

### Proof of Concept
Not applicable as a runnable PoC (no test harness access in this mode); the vulnerable control flow is fully described above:
1. Attacker/user causes backend to return `user_centric_signup: true` for their QR-code session.
2. Orb runs biometric capture/pipeline; assume `pipeline.is_some()` and no fraud detected locally, so `signup_reason == SignupReason::Normal`.
3. `do_signup` takes the `user_centric_signup` branch at [10](#0-9) , sets `success = true`, and never calls `enroll_user`/`signup_post`/`signup_poll`.
4. `after_signup` relays `SignupEnded { success: true, .. }` and UI shows success — without any backend-side settlement check that would have caught duplicate/fraud/inflight conditions.

### Citations

**File:** src/plans/enroll_user.rs (L134-156)
```rust
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
```

**File:** src/plans/enroll_user.rs (L161-168)
```rust
                            }) => {
                                // This includes the following cases:
                                //   1. Backend duplicates
                                //   2. Backend legacy signup requests
                                //   3. Backend inflight matches
                                //   4. Backend detected fraud
                                //   5. Orb agent, internal, capture or pipeline failures
                                //   6. Orb detected fraud
```

**File:** src/backend/user_status.rs (L44-49)
```rust
    pub pcp_version: u16,
    /// Whether the orb should perform app-centric signups.
    pub user_centric_signup: bool,
    /// The Orb Relay id which we will use to send information. New apps should always report this.
    pub orb_relay_app_id: Option<String>,
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

**File:** src/plans/mod.rs (L665-683)
```rust
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

**File:** src/plans/mod.rs (L1500-1509)
```rust
    fn ui_complete_signup(
        orb: &mut Orb,
        signup_status: &debug_report::SignupStatus,
        enrollment_status: Option<enroll_user::Status>,
    ) {
        match signup_status {
            SignupStatus::Success => orb.ui.signup_success(),
            SignupStatus::OrbFailure | SignupStatus::InternalError => {
                notify_failed_signup(orb, Some(SignupFailReason::Unknown));
            }
```
