I have sufficient evidence now to identify the strongest analog to the reported bug class.

### Title
Orb declares a user-centric signup "Success" without any authoritative backend confirmation of enrollment/dedup - ([File: src/plans/mod.rs])

### Summary
In THORChain's `transferOut()`, the contract emits a `TransferOut` "success" event based on the caller's intent (`to` address) rather than on the actual verified outcome of the transfer, so ThorChain is misinformed and finalizes state for a transfer that never really landed at the claimed recipient. The orb-core codebase has the same root-cause pattern in `do_signup()`: when a signup is marked `user_centric_signup` by the companion app's QR data, the orb marks the enrollment as `Success` purely from local, already-known information (whether the biometric pipeline produced a result and whether local fraud detection fired) - it never calls the backend enrollment endpoint (`enroll_user`/`signup_post`/`signup_poll`) that performs the authoritative duplicate/fraud check. The locally declared "Success" is then propagated to the UI, debug report, and the app via `SignupEnded`, exactly like the wrongly-emitted `TransferOut` event being propagated to ThorChain.

### Finding Description
`do_signup()` computes `signup_reason` from only two purely local signals: whether the biometric `pipeline` produced a result and whether `detect_fraud()` returned true [1](#0-0) . Critically, in this build `detect_fraud()` is a stub that always returns `false` ("FOSS: WE HAVE DELETED ALL FRAUD CHECKS") [2](#0-1) .

When the user's QR data flags `user_centric_signup` (and the orb config does not override it via `ignore_user_centric_signups`), the orb skips the call to `enroll_user()` — which is the only code path that talks to the backend's `signup_post`/`signup_poll` endpoints to actually register the signup and receive an authoritative pass/fail (including backend-side duplicate detection, "backend inflight matches", and "backend detected fraud", as documented in `enroll_user.rs`) [3](#0-2) . Instead it directly sets:
```rust
let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups {
    debug_report.enrollment_status(match signup_reason {
        SignupReason::Normal => enroll_user::Status::Success,
        _ => enroll_user::Status::Error,
    });
    signup_reason == SignupReason::Normal
} else {
    Box::pin(self.enroll_user(orb, debug_report, &capture, pipeline.as_ref(), signup_reason)).await.is_success()
};
``` [4](#0-3) 

This mirrors the THORChain bug precisely: the "signal of success" (`enroll_user::Status::Success` / `SignupResult.success`) is derived from the caller's/local intent rather than from confirmation by the authoritative party (the backend), yet it is propagated identically to a genuinely-confirmed success everywhere downstream — to the debug report via `report_signup_reason`/`signup_successful()` [5](#0-4) , to the operator UI via `ui_complete_signup` (`SignupStatus::Success => orb.ui.signup_success()`) [6](#0-5) , and to the companion app via the relay `SignupEnded { success, .. }` message [7](#0-6) .

### Impact Explanation
Because the backend's enrollment/dedup/fraud verification (`enroll_user`) is entirely bypassed for user-centric signups, and local fraud detection is a no-op stub in this build, an attacker (or an app claiming `user_centric_signup: true` in its QR payload) can obtain an orb-declared "Success" for every biometric capture whose pipeline merely produces a result — including signups that the backend would have rejected as duplicates or fraud. This is a cross-signup state bleed / misattributed-signup risk: the local orb state (`debug_report.enrollment_status`, `SignupResult.success`, and the `SignupEnded` message sent to the app) claims a confirmed, deduplicated identity enrollment when no such confirmation from the backend of record ever occurred, analogous to ThorChain vaults believing an outbound transfer succeeded when it did not.

### Likelihood Explanation
`user_centric_signup` is a boolean read straight from `UserData` parsed out of the user's QR-code-linked app data [8](#0-7) , i.e., attacker-controlled/app-controlled input, and the orb defaults to trusting it (`ignore_user_centric_signups` defaults to `false`) [9](#0-8) . No special privilege is required beyond running a signup as a normal unprivileged user with a companion app that sets this flag, and with fraud detection disabled in this build the bypass path is trivially reachable.

### Recommendation
Do not allow a signup to be reported/persisted as `Success` (or forwarded as such to UI/app/debug report) without an authoritative confirmation step performed by the backend equivalent to `enroll_user`'s `signup_post`/`signup_poll` round trip (or at minimum a backend-side dedup/fraud check specific to user-centric flows). If `user_centric_signup` is meant to let the app perform enrollment itself, the orb should still receive and verify a signed/confirmed acknowledgment from the backend before marking `enrollment_status` as `Success`, rather than deriving success solely from local pipeline/fraud-detection state.

### Proof of Concept
1. Have the companion app supply `UserData.user_centric_signup = true` in the signed app data attached to the user's QR code.
2. Ensure the orb config leaves `ignore_user_centric_signups` at its default `false` [9](#0-8) .
3. Run a signup; because `detect_fraud()` always returns `false` in this build [10](#0-9) , any pipeline result yields `SignupReason::Normal`.
4. Observe that `do_signup()` sets `enroll_user::Status::Success` and `success = true` without ever calling `enroll_user()`/`signup_post`/`signup_poll` [4](#0-3) , and this "success" is relayed to the app via `SignupEnded { success: true, .. }` [7](#0-6)  even though the backend's authoritative enrollment/dedup check never ran.

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

**File:** src/plans/mod.rs (L658-683)
```rust
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

**File:** src/plans/mod.rs (L1485-1495)
```rust
        if orb.config.lock().await.self_serve {
            if let Some(relay) = orb.orb_relay.as_mut() {
                relay
                    .send(self_serve::orb::v1::SignupEnded {
                        success: signup_result.success,
                        failure_feedback,
                    })
                    .await
                    .inspect_err(|e| tracing::error!("Relay: Failed to SignupEnded: {e}"))?;
            }
        }
```

**File:** src/plans/mod.rs (L1500-1506)
```rust
    fn ui_complete_signup(
        orb: &mut Orb,
        signup_status: &debug_report::SignupStatus,
        enrollment_status: Option<enroll_user::Status>,
    ) {
        match signup_status {
            SignupStatus::Success => orb.ui.signup_success(),
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

**File:** src/config.rs (L436-436)
```rust
            ignore_user_centric_signups: false,
```
