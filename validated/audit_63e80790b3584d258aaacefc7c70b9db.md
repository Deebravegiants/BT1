### Title
User-centric signup path bypasses server-side enrollment/uniqueness verification, allowing local fraud/duplicate decisions to determine signup success - (File: `src/plans/mod.rs`)

### Summary
The Aave report describes a hard cap that is properly enforced on one code path (borrowing directly at a fixed rate) but is silently bypassed by taking an alternate path (borrow variable, then switch) that reaches the same effective outcome without the guard being re-applied. The same bug class exists in `MasterPlan::do_signup`: the server round-trip that actually validates a signup with the backend (`enroll_user`, which posts to and polls `signup_post`/`signup_poll`) is the mechanism that enforces authoritative acceptance/duplicate checks, but it is entirely skipped for `user_centric_signup` accounts, where success is instead decided purely from locally computed flags.

### Finding Description
In `MasterPlan::do_signup` [1](#0-0) , the flow branches on `user_centric_signup` (a boolean pulled from the user's QR-linked backend data, see `UserData::user_centric_signup` in `src/backend/user_status.rs`, lines 46 and 209-244) combined with the `ignore_user_centric_signups` config flag:

```
let success = if user_centric_signup && !orb.config.lock().await.ignore_user_centric_signups {
    debug_report.enrollment_status(match signup_reason {
        SignupReason::Normal => enroll_user::Status::Success,
        _ => enroll_user::Status::Error,
    });
    signup_reason == SignupReason::Normal
} else {
    Box::pin(self.enroll_user(orb, debug_report, &capture, pipeline.as_ref(), signup_reason)).await.is_success()
};
```
For the normal (non-user-centric) path, `enroll_user::Plan::run` performs the actual server-side enrollment check by POSTing the signup (`signup_post::request`) and polling for backend-confirmed completion/duplicate detection (`signup_poll::request`) before deciding success [2](#0-1) . This backend round-trip is the analog of the Aave `borrow` function's hard cap check — it is the authoritative gate that is supposed to be applied for every signup.

For the `user_centric_signup` path, this authoritative check is completely bypassed. `success` is instead derived only from `signup_reason`, which itself is computed earlier purely from locally-derived values: `pipeline.is_none()` and the on-device `detect_fraud` result [3](#0-2) . No `signup_post`/`signup_poll` request is issued at all in this branch, so the backend never gets a chance to reject the signup (e.g., for duplicate identity, fraud correlation across orbs, or other server-side checks that only exist in that call).

This mirrors the Aave bug precisely in structure: a restriction/verification is enforced on one path (`enroll_user`'s backend round trip) but an alternate path reaches the same "signup succeeded" outcome (`success = true`) without ever exercising that verification, relying solely on a locally computed condition.

### Impact Explanation
If a signup is routed through the `user_centric_signup` branch, the Orb will mark `SignupReason::Normal` as `Status::Success` and finalize the signup (uploading identity data via `build_pcp`/`upload_pcp_tier_0`, PCP tiers 1/2) purely based on on-device pipeline/fraud results, without the backend ever confirming acceptance or checking for duplicate/misattributed identities via `signup_post`/`signup_poll`. This is a cross-signup state bleed / unauthorized-signup risk: identity binding is completed locally and reported to the backend as already-decided, bypassing the same server-side dedup/fraud gate that the "normal" enrollment path always exercises.

### Likelihood Explanation
The branch is gated by `user_centric_signup`, a value sourced from backend-issued, signature-verified QR user data (`orb_qr_link::UserData`, verified via `user_data.verify(user_data_hash)` in `src/backend/user_status.rs` lines 166-179), so an unprivileged attacker cannot forge this flag directly under normal (non-`skip-user-qr-validation`) builds. However, the `#[cfg(feature = "skip-user-qr-validation")]` `do_request` stub hardcodes `user_centric_signup: true` unconditionally [4](#0-3) , meaning any build/environment with that feature enabled routes every signup through the bypass branch. Whether that feature is enabled in production is not determinable from the indexed code alone.

### Recommendation
Do not let the `user_centric_signup` path fully substitute for the backend enrollment verification. At minimum, still perform a lightweight backend confirmation call (equivalent to `signup_post`/`signup_poll`) even for user-centric signups so duplicate/fraud checks are never entirely skipped, and audit whether `ignore_user_centric_signups` and the `skip-user-qr-validation` feature can be toggled or reached by non-trusted actors in any deployed configuration.

### Proof of Concept
Not concretely demonstrable from static analysis alone: exploitation requires either (a) the backend issuing `user_centric_signup: true` for a QR-linked account under attacker control, or (b) a build with `skip-user-qr-validation` enabled, in which case any local signup with `SignupReason::Normal` (achievable by ensuring `pipeline.is_some()` and having `detect_fraud` return false, both device-observable/on-device-influenceable conditions) will be marked `Status::Success` at `src/plans/mod.rs` line 645 without ever calling `enroll_user`'s backend verification round trip.

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

**File:** src/plans/mod.rs (L638-656)
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
