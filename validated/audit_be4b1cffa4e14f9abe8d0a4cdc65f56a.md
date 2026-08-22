### Title
Unauthorized/misattributed signup success when `user_centric_signup` is true bypasses backend enrollment verification - ([File: src/plans/mod.rs])

### Summary
The bug class described in the external report (a boolean flag that disables a mandatory verification/transfer step, letting an unprivileged actor obtain the full "successful outcome" without passing the authoritative check) has a direct analog in orb-core's signup completion logic: the `user_centric_signup` flag skips the call to the backend-authoritative `enroll_user` plan, so signup success is instead determined purely by local, unauthoritative state.

### Finding Description
In `do_signup`, after biometric capture/pipeline processing and PCP upload, the code decides whether to call `enroll_user` (a network round-trip that lets the backend perform authoritative enrollment/deduplication/fraud verification) based on a boolean: [1](#0-0) 

If `user_centric_signup` is `true` and the orb's config `ignore_user_centric_signups` is `false`, the backend enrollment call `enroll_user` (which performs `signup_post`/`signup_poll` — the actual server-side check that detects duplicates, in-flight matches, and fraud) is skipped entirely, and `success` is instead derived solely from the local `signup_reason` variable: [2](#0-1) 

`enroll_user::Plan::run` is the code path that would normally poll the backend for `SIGNUP SUCCESS`/`SIGNUP FAIL` (duplicate detection, fraud, legacy signup, in-flight matches): [3](#0-2) 

Meanwhile, the local `signup_reason` is computed from `detect_fraud`, which in this FOSS build is a stub that unconditionally returns `false` (fraud checks removed): [4](#0-3) 

`user_centric_signup` originates from `orb_qr_link::UserData`, part of the `authenticated_app_data` returned by the signup backend and checked only against a hash carried in the user's own QR code: [5](#0-4) [6](#0-5) 

The struct field itself is documented as controlling whether the orb should perform "app-centric" (i.e., locally-attested) signups instead of the authoritative flow: [7](#0-6) 

This mirrors the CreditLine `autoLiquidation` pattern precisely: a single boolean field gates whether a mandatory, authoritative verification/settlement step executes, and when the flag takes one value, the code silently substitutes a weaker, locally-derived outcome for the strong, backend-verified one — with no additional requirement that the substitute outcome ever be confirmed by the authority (the backend) it claims to represent.

### Impact Explanation
When `user_centric_signup` is true, a signup can be marked and reported as `enroll_user::Status::Success` (and thus `SignupReason::Normal`/successful signup) purely from local pipeline results, without the orb ever contacting the backend's enrollment endpoint to check for duplicates, in-flight matches, or backend-side fraud. This is a misattributed-signup risk: the local success determination is not equivalent to (and can diverge from) the backend's authoritative determination that would normally gate whether a given identity is uniquely enrolled. Given that on-orb fraud checks in this build are stubbed out (`detect_fraud` always returns `false`), the only real signal for a "duplicate" or "fraud" outcome is the backend round-trip that is being skipped in the `user_centric_signup` branch.

### Likelihood Explanation
`user_centric_signup` is sourced from `authenticated_app_data`, which is nominally backend-issued and hash-checked against QR data, but this hash-based check only confirms consistency with what the user's own QR/app pair presented — it does not independently re-verify against a stronger identity/liveness proof at signup-completion time. The orb-side gate (`ignore_user_centric_signups`) defaults to `false`: [8](#0-7) 
so the bypass path is live by default whenever the backend/app opts into "app-centric" signup, without any additional per-signup requirement that the orb independently re-verify the result with the backend.

### Recommendation
Do not let a client/app-supplied flag fully substitute for the backend's authoritative enrollment check. At minimum, require that `enroll_user` (or an equivalent backend confirmation call) always run to validate uniqueness/fraud status before `success` is set, regardless of `user_centric_signup`; if the "app-centric" flow is intended to skip only the *notification* step and not the *verification* step, split those concerns so verification is never conditioned on this flag.

### Proof of Concept
1. Backend/app issues QR-linked `UserData` with `user_centric_signup: true` (this is attacker/user-app influenced input path, verified only by hash matching against the same user's QR code). [9](#0-8) 
2. During `do_signup`, since `user_centric_signup` is `true` and `ignore_user_centric_signups` is `false` (default), the branch at `src/plans/mod.rs:639-656` sets `success` from `signup_reason == SignupReason::Normal` alone.
3. Because `detect_fraud` (`src/plans/mod.rs:1390-1406`) always returns `false`, `signup_reason` is `Normal` whenever the local pipeline produced any result, and `enroll_user` (the only code path that would contact the backend for duplicate/fraud detection, `src/plans/enroll_user.rs:69-176`) is never invoked.
4. The signup is reported and recorded as successful (`report_signup_reason`, `debug_report.signup_successful()`) without any backend-side authoritative confirmation of uniqueness.

### Citations

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

**File:** src/backend/user_status.rs (L44-49)
```rust
    pub pcp_version: u16,
    /// Whether the orb should perform app-centric signups.
    pub user_centric_signup: bool,
    /// The Orb Relay id which we will use to send information. New apps should always report this.
    pub orb_relay_app_id: Option<String>,
}
```

**File:** src/backend/user_status.rs (L100-109)
```rust
    let authenticated_app_data = Some(orb_qr_link::UserData {
        identity_commitment: "test".to_string(),
        self_custody_public_key: BASE64.encode(public_key.as_ref()),
        data_policy: orb_qr_link::DataPolicy::OptOut,
        pcp_version: 2,
        user_centric_signup: true,
        orb_relay_app_id: Some(format!("test-skip-user-qr-validation-{}", ORB_ID.to_string())),
    });

    Ok(Response { valid: true, reason: None, backend_keys, authenticated_app_data })
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

**File:** src/config.rs (L431-436)
```rust
            pcp_v3: false,
            pcp_tier1_blocking_threshold: 12,
            pcp_tier1_dropping_threshold: u32::MAX,
            pcp_tier2_blocking_threshold: u32::MAX,
            pcp_tier2_dropping_threshold: 12,
            ignore_user_centric_signups: false,
```
