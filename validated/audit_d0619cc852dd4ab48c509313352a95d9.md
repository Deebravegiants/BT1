### Title
User-controlled `user_centric_signup` flag lets the orb skip backend signup verification/deduplication - (File: src/plans/mod.rs)

### Summary
`do_signup()` in `src/plans/mod.rs` decides whether to actually contact the signup backend for verification/deduplication based on a boolean, `user_centric_signup`, that originates from the user's own companion-app data (`authenticated_app_data`) and is only checked for internal consistency, not for actual entitlement. When this attacker-controlled flag is set, the orb reports a signup as successful purely from a locally-computed `signup_reason`, entirely skipping the backend round-trip (`signup_post`/`signup_poll`) that is the only place the backend performs duplicate-person and fraud checks.

### Finding Description
In `do_signup()`, once biometric capture/pipeline finish, the code computes `signup_reason` locally (`Normal`/`Failure`/`Fraud`) and reads `user_centric_signup` straight from the scanned user's QR-bound app data: [1](#0-0) 

Then, if that flag is set (and the operator hasn't overridden it via `ignore_user_centric_signups`), the orb **never calls `enroll_user()`** — it just derives `success` from the local `signup_reason`: [2](#0-1) 

`enroll_user()` is the code path that actually talks to the backend (`signup_post::request` then repeated `signup_poll::request`), and it is explicitly documented as the place where backend-side duplicate detection happens: [3](#0-2) 

The `user_centric_signup` value itself is sourced from `authenticated_app_data`, i.e., data supplied by the user's own phone/app during the QR exchange, and is only validated by checking a self-consistency hash (`user_data.verify(user_data_hash)`), not by any independent backend entitlement decision: [4](#0-3) [5](#0-4) 

Additionally, local fraud detection — the only other gate that could produce a non-`Normal` `signup_reason` — is fully neutered in this build: [6](#0-5) 

So the combination of (a) a self-attested, user-controlled flag that (b) skips the sole backend verification/dedup step, gated only by (c) a local fraud check that is a stub always returning `false`, produces a code path where an unprivileged user (the person being scanned, via their own app) can make the orb locally mark arbitrary signups as `Success` without the backend ever getting the chance to reject them as duplicates, fraud, or otherwise ineligible.

This mirrors the structural root cause of the Nouns DAO H-2 report: a state/flag that is supposed to represent an intermediate/no-op path (there, a cancelled proposal; here, an "app already verified this, orb doesn't need to re-check" flag) is trusted by downstream aggregation/acceptance logic without re-validating it against the authoritative source, letting the controlling actor cheaply mint multiple "valid" outcomes that should have gone through the full, dedup-enforcing lifecycle.

### Impact Explanation
An unprivileged end-user (via their own app data) can cause the orb to report successful, enrolled signups while completely bypassing the backend's request/poll cycle — the only mechanism that performs duplicate-person and backend-side fraud checks. This can result in unauthorized or misattributed signups being accepted locally (and downstream personal-custody-package uploads proceeding) without ever being checked or recorded as verified/unique by the backend, i.e., a form of dedup/fraud-enforcement bypass and potential cross-signup state inconsistency between what the orb reports locally and what the backend actually knows.

### Likelihood Explanation
The prerequisite is control over the companion app / QR data supplying `user_centric_signup: true`, which is inherent to the normal user flow (any signee's own phone). No collusion with an operator or orb owner is required, and the check gating this bypass (`ignore_user_centric_signups`) defaults to `false`: [7](#0-6) 

### Recommendation
Do not allow a user-supplied/app-supplied flag to skip the backend enrollment call that performs duplicate/fraud verification. At minimum, `enroll_user()` (and thus `signup_post`/`signup_poll`) should always run so the backend remains the source of truth for uniqueness and fraud, regardless of `user_centric_signup`; if the "app-centric" flow is meant to change *how* results are delivered to the app, it should not change *whether* the backend verification actually occurs.

### Proof of Concept
1. A user runs a signup with their own companion app, which supplies `authenticated_app_data.user_centric_signup = true` (self-consistent, hash-verified, but not independently authorized).
2. Orb performs capture/pipeline; `detect_fraud()` is a stub that always returns `Ok(false)` (`src/plans/mod.rs:1390-1406`), so `signup_reason` becomes `Normal`.
3. In `do_signup()`, because `user_centric_signup` is `true` and `ignore_user_centric_signups` is `false` (default), `enroll_user()`/`signup_post`/`signup_poll` are never invoked (`src/plans/mod.rs:639-656`).
4. `result.success` is set to `true` purely from the local `signup_reason`, so the orb (and its UI/dbus signal) report a completed, successful signup without the backend ever performing its duplicate-person/fraud check that `enroll_user.rs` documents as covering "Backend duplicates ... Backend detected fraud" (`src/plans/enroll_user.rs:157-176`).
5. Repeating this with different capture attempts allows an unprivileged actor to generate multiple locally-"successful" signups that were never subjected to the backend's authoritative verification.

### Citations

**File:** src/plans/mod.rs (L562-573)
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
        let user_id = qr_codes.user_qr_code.user_id.clone();
        let user_centric_signup = qr_codes.user_data.user_centric_signup;
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

**File:** src/backend/user_status.rs (L203-244)
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
        let backend_iris_public_key = decode_public_key(&backend_iris_public_key)
            .wrap_err("decoding backend_iris_public_key")?;
        let backend_normalized_iris_public_key =
            decode_public_key(&backend_normalized_iris_public_key)
                .wrap_err("decoding backend_normalized_iris_public_key")?;
        let backend_face_public_key = decode_public_key(&backend_face_public_key)
            .wrap_err("decoding backend_face_public_key")?;
        let backend_tier2_public_key = backend_tier2_public_key
            .map(decode_public_key)
            .transpose()
            .wrap_err("decoding backend_tier2_public_key")?;
        let user_public_key =
            decode_public_key(&user_public_key).wrap_err("decoding user_public_key")?;
        Ok(Some(UserData {
            backend_iris_public_key: Some(backend_iris_public_key),
            backend_iris_encrypted_private_key: Some(backend_iris_encrypted_private_key),
            backend_normalized_iris_public_key: Some(backend_normalized_iris_public_key),
            backend_normalized_iris_encrypted_private_key: Some(
                backend_normalized_iris_encrypted_private_key,
            ),
            backend_face_public_key: Some(backend_face_public_key),
            backend_face_encrypted_private_key: Some(backend_face_encrypted_private_key),
            backend_tier2_public_key,
            backend_tier2_encrypted_private_key,
            self_custody_user_public_key: Some(user_public_key),
            id_commitment: Some(identity_commitment),
            #[cfg(feature = "internal-data-acquisition")]
            data_policy,
            pcp_version,
            user_centric_signup,
            orb_relay_app_id,
        }))
```

**File:** src/config.rs (L436-436)
```rust
            ignore_user_centric_signups: false,
```
