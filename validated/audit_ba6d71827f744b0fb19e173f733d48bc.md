### Title
Stale cached user-status checkpoint reused for signup authorization without revalidation - (File: `src/plans/mod.rs`)

### Summary
`MasterPlan::scan_remaining_qr_codes` treats a previously fetched `backend::user_status::UserData` checkpoint (obtained during idle scanning, before a signup officially begins) as still valid for the entire signup as long as only the *operator* QR-code timestamp has not expired. The *user* status/authorization checkpoint itself is never re-fetched or re-validated before it is used to authorize and drive the actual biometric enrollment, mirroring the reported bug class of "a checkpoint used to gate/allocate a benefit is not refreshed before it is consumed."

### Finding Description
`idle_scan_user_qr_code` (self-serve idle loop) calls `handle_user_qr_code` → `verify_user_qr_code` → `backend::user_status::request`, which performs a backend call to `/api/v2/session/{user_id}/status` and returns a `UserData` snapshot (containing eligibility, keys, `user_centric_signup` flag, etc.). [1](#0-0) [2](#0-1) 

This `UserData` snapshot is stored as part of `QrCodes::Both { operator_data, user_qr_code, user_data, .. }`. [3](#0-2) [4](#0-3) 

Later, `do_signup` calls `scan_remaining_qr_codes`, which — if the *operator* QR-code timestamp is still within `operator_qr_expiration_time` — takes the fast path and returns the already-cached `QrCodes::Both` tuple **as-is**, without re-requesting `backend::user_status::request` or otherwise re-checking that the user's status/eligibility is still current:

```rust
QrCodes::Both { operator_data, user_qr_code, user_data, user_qr_code_string }
    if operator_data.timestamp.elapsed() < operator_qr_expiration_time =>
{
    break Ok(Some(ResolvedQrCodes {
        operator_data,
        user_qr_code,
        user_data,
        user_qr_code_string,
    }));
}
``` [5](#0-4) 

Only the operator checkpoint's freshness is validated (`operator_data.timestamp.elapsed() < operator_qr_expiration_time`); the `user_data` checkpoint (analogous to `extraRewardPerToken` in the report) is never refreshed. This cached, potentially stale `user_data` is then used directly to build the `personal_custody_package::Credentials` (backend keys, `identity_commitment`, `self_custody_user_public_key`) and to decide the enrollment path (`user_centric_signup`), all the way through biometric capture, pipeline, and enrollment: [6](#0-5) [7](#0-6) 

Meanwhile there can be an arbitrary amount of elapsed time between the initial idle scan (where `user_data` was fetched) and the actual biometric capture/enrollment — including the idle wait for a button/trigger, QR re-scans, and a fixed 3-second pre-capture delay — during which the backend-side session/eligibility could have changed (expired, been consumed by a duplicate signup, blocked, or reassigned) without orb-core detecting it.

### Impact Explanation
Because the `user_data` checkpoint that encodes backend authorization/eligibility and cryptographic key material is never refreshed before being consumed, the orb can proceed with and complete a signup using stale authorization state. This mirrors the reward-report's root cause exactly: a "benefit distribution" decision (here, signup enrollment/authorization) is computed from a shared checkpoint value that should have been refreshed at the point of consumption but wasn't, enabling misattributed/duplicate or unauthorized signup completion.

### Likelihood Explanation
Every self-serve idle-scan flow (`self_serve && !self_serve_button`) populates `QrCodes::Both` ahead of the operator-QR expiration path, and the operator's expiration window (`operator_qr_expiration_time`) is independent from and typically longer than the time needed to invalidate a user's session server-side. This is a normal, non-adversarial code path triggered on every self-serve signup, not merely a theoretical edge case.

### Recommendation
Re-validate (or re-fetch) the cached `user_data`/authorization checkpoint in `scan_remaining_qr_codes` immediately before it is consumed to build `personal_custody_package::Credentials` and drive enrollment — i.e., call `backend::user_status::request` again (or otherwise confirm current validity) right before `do_signup` uses it, rather than only checking the operator QR-code timestamp.

### Proof of Concept
1. Enable self-serve idle scanning (`self_serve && !self_serve_button`).
2. Scan a user QR-code; `idle_scan_user_qr_code` fetches and caches `user_data` via `backend::user_status::request`. [8](#0-7) 
3. Before biometric capture actually begins, have the backend invalidate/consume that user's session (e.g., the same user completes signup on a different orb, or the session naturally expires server-side) — this happens on the backend, invisible to the orb.
4. Because `operator_data.timestamp.elapsed() < operator_qr_expiration_time` still holds, `scan_remaining_qr_codes` returns the stale cached `user_data` without re-checking it. [9](#0-8) 
5. The signup proceeds to `build_pcp`/`enroll_user` using the outdated authorization/key data, completing an enrollment that should have been rejected.

### Citations

**File:** src/plans/mod.rs (L144-157)
```rust
#[allow(clippy::large_enum_variant)]
#[derive(Clone)]
enum QrCodes {
    Both {
        operator_data: OperatorData,
        user_qr_code: qr_scan::user::Data,
        user_data: backend::user_status::UserData,
        user_qr_code_string: String,
    },
    Operator {
        operator_data: OperatorData,
    },
    None,
}
```

**File:** src/plans/mod.rs (L456-488)
```rust
    async fn idle_scan_user_qr_code(
        &mut self,
        orb: &mut Orb,
        operator_data: &OperatorData,
        operator_qr_expiration_time: Duration,
        mut ui_idle_delay: Option<time::Sleep>,
    ) -> Result<Option<(qr_scan::user::Data, backend::user_status::UserData, String)>> {
        loop {
            orb.reset_rgb_camera().await?;
            match idle::Plan::with_user_qr_scan(
                ui_idle_delay.take(),
                Some(operator_qr_expiration_time.saturating_sub(operator_data.timestamp.elapsed())),
                #[cfg(feature = "internal-data-acquisition")]
                self.data_acquisition,
            )
            .run(orb)
            .await?
            {
                idle::Value::UserQrCode(qr_scan_result) => {
                    if !check_signup_conditions(orb).await? {
                        continue;
                    }
                    if let Some(Some((user_qr_code, user_data, user_qr_code_string))) =
                        self.handle_user_qr_code(qr_scan_result, orb, operator_data, None).await?
                    {
                        break Ok(Some((user_qr_code, user_data, user_qr_code_string)));
                    }
                }
                idle::Value::TimedOut => break Ok(None),
                idle::Value::ButtonPress => unreachable!(),
            }
        }
    }
```

**File:** src/plans/mod.rs (L572-598)
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

**File:** src/plans/mod.rs (L788-820)
```rust
    async fn scan_remaining_qr_codes(
        &mut self,
        orb: &mut Orb,
        qr_codes: QrCodes,
        operator_qr_expiration_time: Duration,
    ) -> Result<Option<ResolvedQrCodes>> {
        loop {
            match qr_codes {
                QrCodes::Both { operator_data, user_qr_code, user_data, user_qr_code_string }
                    if operator_data.timestamp.elapsed() < operator_qr_expiration_time =>
                {
                    break Ok(Some(ResolvedQrCodes {
                        operator_data,
                        user_qr_code,
                        user_data,
                        user_qr_code_string,
                    }));
                }
                QrCodes::Operator { operator_data }
                    if operator_data.timestamp.elapsed() < operator_qr_expiration_time =>
                {
                    let Some((user_qr_code, user_data, user_qr_code_string)) =
                        self.scan_user_qr_code(orb, &operator_data).await?
                    else {
                        break Ok(None);
                    };
                    break Ok(Some(ResolvedQrCodes {
                        operator_data,
                        user_qr_code,
                        user_data,
                        user_qr_code_string,
                    }));
                }
```

**File:** src/plans/mod.rs (L1869-1886)
```rust
impl QrCodes {
    fn with_user_qr_code(
        &self,
        user_qr_code: qr_scan::user::Data,
        user_data: backend::user_status::UserData,
        user_qr_code_string: String,
    ) -> Self {
        match self {
            QrCodes::Operator { operator_data } => QrCodes::Both {
                operator_data: operator_data.clone(),
                user_qr_code,
                user_data,
                user_qr_code_string,
            },
            QrCodes::Both { .. } => panic!("user QR code is already present"),
            QrCodes::None => panic!("no operator QR code"),
        }
    }
```

**File:** src/backend/user_status.rs (L145-163)
```rust
/// Makes a validation request.
#[allow(clippy::too_many_lines)]
pub async fn request(
    qr_code: &qr_scan::user::Data,
    operator_data: &OperatorData,
    use_full_operator_qr: bool,
    use_only_operator_location: bool,
) -> Result<Option<UserData>> {
    let Response { valid, reason, backend_keys, authenticated_app_data } =
        do_request(qr_code, operator_data, use_full_operator_qr, use_only_operator_location)
            .await?;
    if !valid {
        tracing::info!(
            "User QR-code invalid: {qr_code:?}, reason: {:?}",
            reason.as_deref().unwrap_or("<empty>")
        );
        return Ok(None);
    }
    if let (Some(backend_keys), Some(user_data)) = (backend_keys, authenticated_app_data) {
```
