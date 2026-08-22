### Title
Silent skip of Personal Custody Package (PCP) build/upload on missing backend credentials, with signup still marked successful - ([File: src/plans/mod.rs])

### Summary
`do_signup` converts `ResolvedQrCodes` into `personal_custody_package::Credentials` via `TryInto`, but if that conversion fails, the branch is silently skipped with no error logged, no `debug_report` update, and no `notify_failed_signup` call. Execution then falls through to independently compute the enrollment `success` state, so a signup can be recorded as successful even though the user's Personal Custody Package (containing their own encrypted iris/face key material) was never built or uploaded — mirroring the "controller does not raise an error on insufficient resources" pattern from the analog report, where a required step silently no-ops instead of aborting/erroring, leaving the caller with an inconsistent success/committed state.

### Finding Description
In `do_signup`, credential conversion is gated only by `if let Ok(...)`: [1](#0-0) 

If `qr_codes.try_into()` yields `Err(())`, there is no `else` branch — the whole `build_pcp` → `upload_pcp_tier_0` → tier1/tier2 upload sequence is skipped entirely, without any logging, metric, or `debug_report` mutation: [2](#0-1) 

The `TryInto` implementation returns `Err(())` whenever any one of several backend-provided key fields (`backend_iris_public_key`, `backend_iris_encrypted_private_key`, `backend_normalized_iris_public_key`, `backend_normalized_iris_encrypted_private_key`, `backend_face_public_key`, `backend_face_encrypted_private_key`, `self_custody_user_public_key`) is `None`: [3](#0-2) 

After this silent skip, `do_signup` proceeds to compute `success` completely independently, either via the `user_centric_signup` short-circuit or via `enroll_user`, which talks to the backend through `signup_post`/`signup_poll` and does not depend on the PCP path at all: [4](#0-3) 

The net effect: the enrollment/signup can be reported as `Status::Success` (and surfaced to the operator/user as a successful signup) even though the personal custody package — the artifact that gives the user self-custody of their own encrypted biometric key material — was never generated or uploaded, and no failure signal (log, metric, debug report field, or UI notification) records that this happened.

### Impact Explanation
This is directly analogous to the referenced report's core defect: a required sub-operation (liquidity withdrawal / here, custody-package build+upload) can silently fail to complete, yet the encompassing operation (withdrawal / here, signup) is still treated as complete and reports success without reverting or signaling error. In this codebase the consequence is a "cross-signup state bleed"-style inconsistency: the backend's signup record indicates the enrollment succeeded, but the user's own copy of self-custody key material for their iris/face data is missing, with zero error trail (`tracing::error!`, `dd_incr!`, `debug_report` field, or `notify_failed_signup`) to alert engineering or the user that their custody package upload was skipped. This silently breaks the self-custody guarantee for an unprivileged, otherwise-successfully-enrolled user.

### Likelihood Explanation
The `Err(())` path is reachable whenever `user_status` backend responses to a legitimate user's QR scan omit any one of the seven required key fields (e.g., due to backend/version skew, partial responses, or unexpected `None` fields for a given user account state) — this does not require a malicious operator, peer, or hardware access, only ordinary backend response variability during a normal, unprivileged user signup flow.

### Recommendation
Replace the silent `if let Ok(...)` skip with explicit handling of the `Err` case: log the failure, increment a metric, update `debug_report` (e.g. a dedicated failure reason), and cause the signup to be reported as failed via `notify_failed_signup`/`result.success = false` rather than letting execution continue to the independent `success` computation below. Consider making `TryInto::Error` carry which field(s) were missing instead of `()` to aid diagnosis.

### Proof of Concept
1. A user completes QR scanning and biometric capture normally.
2. Backend's `user_status` response for this user is missing e.g. `self_custody_user_public_key` (any of the seven required `Option` fields is `None`).
3. `qr_codes.try_into()` at `src/plans/mod.rs:574` returns `Err(())`; the `if let Ok(...)` body (lines 574-637) is skipped entirely — no `tracing::error!`, no `dd_incr!`, no `debug_report` update.
4. Control falls to line 639-656, where `success` is computed via `enroll_user` (or the `user_centric_signup` branch), independent of whether the PCP was built/uploaded.
5. If `enroll_user`/`signup_post` reports success, `result.success` is `true` and the UI shows a successful signup (`Self::ui_complete_signup` → `orb.ui.signup_success()`), even though the user's personal custody package was never generated or uploaded, and nothing in logs/metrics/debug_report reflects that this step was skipped.

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

**File:** src/plans/mod.rs (L639-662)
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
```

**File:** src/plans/mod.rs (L1898-1939)
```rust
impl TryInto<personal_custody_package::Credentials> for ResolvedQrCodes {
    type Error = ();

    fn try_into(self) -> Result<personal_custody_package::Credentials, Self::Error> {
        let ResolvedQrCodes { operator_data, user_data, user_qr_code, user_qr_code_string } = self;
        if let (
            Some(backend_iris_public_key),
            Some(backend_iris_encrypted_private_key),
            Some(backend_normalized_iris_public_key),
            Some(backend_normalized_iris_encrypted_private_key),
            Some(backend_face_public_key),
            Some(backend_face_encrypted_private_key),
            Some(self_custody_user_public_key),
        ) = (
            user_data.backend_iris_public_key,
            user_data.backend_iris_encrypted_private_key,
            user_data.backend_normalized_iris_public_key,
            user_data.backend_normalized_iris_encrypted_private_key,
            user_data.backend_face_public_key,
            user_data.backend_face_encrypted_private_key,
            user_data.self_custody_user_public_key,
        ) {
            Ok(personal_custody_package::Credentials {
                operator_qr_code: operator_data.qr_code,
                user_qr_code,
                user_qr_code_string,
                backend_iris_public_key,
                backend_iris_encrypted_private_key,
                backend_normalized_iris_public_key,
                backend_normalized_iris_encrypted_private_key,
                backend_face_public_key,
                backend_face_encrypted_private_key,
                backend_tier2_public_key: user_data.backend_tier2_public_key,
                backend_tier2_encrypted_private_key: user_data.backend_tier2_encrypted_private_key,
                self_custody_user_public_key,
                pcp_version: user_data.pcp_version,
            })
        } else {
            Err(())
        }
    }
}
```
