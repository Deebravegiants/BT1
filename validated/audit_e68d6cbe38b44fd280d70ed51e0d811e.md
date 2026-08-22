### Title
Local-only success determination for user-centric signups bypasses backend confirmation, mirroring "state committed without underlying verification" — ([File: src/plans/mod.rs])

### Summary
The reported bug is a class of "phantom success" accounting: a claim is recorded as fulfilled (vesting minted) even though the underlying resource (RDNT reserve) was never actually transferred, because the success state is derived and persisted before/without verifying the real downstream outcome. The reachable analog in `orb-core` is in the signup pipeline's `do_signup` function, where for `user_centric_signup` sessions, the enrollment "success" status is computed and recorded purely from local in-memory values (`signup_reason`) instead of confirming with the backend that the signup was actually accepted/persisted.

### Finding Description
In `src/plans/mod.rs`, `do_signup` branches on `user_centric_signup`: [1](#0-0) 

When `user_centric_signup && !ignore_user_centric_signups`, the code sets:
```
debug_report.enrollment_status(match signup_reason {
    SignupReason::Normal => enroll_user::Status::Success,
    _ => enroll_user::Status::Error,
});
success = signup_reason == SignupReason::Normal;
```
This bypasses the `enroll_user::Plan::run` path entirely — the path that otherwise performs the actual backend round-trip (`signup_post::request` followed by a `signup_poll::request` retry loop) that confirms with the server that the signup was uniquely accepted, deduplicated, and recorded server-side: [2](#0-1) 

Instead, for the user-centric branch, `enrollment_status::Success` is derived solely from `signup_reason`, which itself is computed as: [3](#0-2) 

Critically, `detect_fraud` in this build always returns `false` — all fraud checks have been stripped: [4](#0-3) 

So for any user-centric signup where the local biometric pipeline produced a result (`pipeline.is_some()`), `signup_reason` is unconditionally `Normal`, and `enrollment_status` is unconditionally set to `Success` — with no external confirmation that the backend actually accepted/committed this signup (no dedup check, no server fraud check, no persisted acknowledgment). This is directly analogous to the reported bug: the "reserve" (backend-side confirmation/acceptance) is never checked before the local ledger (`debug_report.enrollment_status`, `result.success`) records success, and that recorded success subsequently drives `ui_complete_signup` (showing the user a success signal) and the relay message `SignupEnded { success: true }`: [5](#0-4) 

### Impact Explanation
If the backend never actually persisted/accepted the signup (e.g., it was a duplicate, backend detected fraud server-side, or the request never reached/registered with the backend), the Orb-side state and UI would still declare `SignupSuccess`, and the `self_serve` relay flow would report `SignupEnded { success: true }` to the companion app. This is a misattributed-signup / cross-signup-state-bleed class impact: a local success record is created and propagated to the operator/app UI and relay channel without confirmation from the source of truth (the backend), potentially leading to inconsistent state between the Orb's local accounting of "who is verified" and what the backend actually recorded — the same "insolvency-style" divergence as the original report (local ledger says success/funds-received when the authoritative source has no record of it).

### Likelihood Explanation
This path is reachable only when `user_centric_signup` is true (set by backend-issued QR-code user data) and `ignore_user_centric_signups` config is false — this is a real, backend-controlled and reachable condition, not a hypothetical or hardware-only path. Given fraud detection is fully disabled in this build (`detect_fraud` always returns `false`), the "phantom success" condition is not a rare edge case but the default outcome whenever the local pipeline produces any result for a user-centric signup — the only remaining condition is `pipeline.is_none()`.

### Recommendation
For the `user_centric_signup` branch, do not synthesize `enrollment_status::Success` purely from local `signup_reason`. Instead, still perform (or otherwise wait for) an equivalent backend-side confirmation/acknowledgment step (analogous to the `signup_poll` loop in `enroll_user::Plan::run`) before marking `debug_report.enrollment_status` and `result.success` as successful, so that the locally recorded success state can never diverge from what the backend has actually accepted/persisted.

### Proof of Concept
1. Backend issues a QR-code session with `user_centric_signup: true`.
2. Orb completes local biometric capture and pipeline successfully (`pipeline.is_some()`).
3. `detect_fraud` returns `false` unconditionally (fraud checks are stripped in this build) — see `src/plans/mod.rs:1390-1406`.
4. `signup_reason` resolves to `SignupReason::Normal` — see `src/plans/mod.rs:565-571`.
5. `do_signup` takes the `user_centric_signup` branch and sets `enrollment_status = Success` and `result.success = true` without ever calling `enroll_user::Plan::run` (i.e., without any backend `signup_post`/`signup_poll` round trip) — see `src/plans/mod.rs:639-663`.
6. `after_signup` then reports `SignupSuccess` to the UI and sends `SignupEnded { success: true }` over the relay to the companion app — see `src/plans/mod.rs:1481-1495` — even though no backend confirmation of acceptance ever occurred.

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

**File:** src/plans/mod.rs (L639-663)
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

**File:** src/plans/mod.rs (L1481-1495)
```rust
        if let Some(signup_status) = signup_status {
            Self::ui_complete_signup(orb, &signup_status, enrollment_status);
        }

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

**File:** src/plans/enroll_user.rs (L90-156)
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
```
