### Title
Stale operator/user QR-code authorization reused across a long signup window without re-validation - (File: `src/plans/mod.rs`)

### Summary
The external report describes `rigidRedemption()` executing a price-dependent action against a value (wstETH price) that was correct at the moment of the initial check but can drift by the time the transaction is actually executed, with no re-check/expiry enforced at execution time. The analogous root cause in orb-core is that a signup's authorization data (the operator/distributor QR-code validity and the user QR-code/backend "authenticated app data") is validated once, then reused to drive a signup pipeline that takes an unbounded amount of additional wall-clock time (biometric capture, ML pipeline, fraud checks, PCP upload, enrollment), without any re-validation immediately before the state-changing enrollment call.

### Finding Description
`MasterPlan::scan_remaining_qr_codes` only re-checks freshness of the **operator** QR-code data via a coarse elapsed-time comparison against `operator_qr_expiration_time`: [1](#0-0) 

If that check passes (or if the code path re-uses previously scanned/cached `QrCodes::Both` data), the resolved `operator_data`, `user_qr_code`, and `user_data` are carried forward into `do_signup` and used, unmodified, to drive the entire remainder of the signup: constructing the `DebugReport`, announcing the orb over `orb_relay`, running biometric capture, the ML pipeline, fraud detection, personal-custody-package construction/upload, and finally `enroll_user`/`enroll_user::Status` determination: [2](#0-1) [3](#0-2) [4](#0-3) 

The only "freshness" guard anywhere in this flow is the coarse `operator_data.timestamp.elapsed() < operator_qr_expiration_time` duration check; there is no re-validation call to the backend (`backend::operator_status::request` / `backend::user_status::request`) performed right before the enrollment/authorization-consuming step, and the `user_data` fetched once during QR validation (`backend::user_status::request`) is never re-checked at all before being consumed: [5](#0-4) 

This mirrors the reported bug class exactly: a value/state is fetched and validated at time T0, then consumed at time T1 (which can be arbitrarily later due to biometric capture duration, pipeline processing, network retries such as the 6-retry PCP upload loop, or orb relay announce retries), with no check that the underlying authorization is still valid at T1.

### Impact Explanation
If a distributor/operator is deactivated, a user's QR/session is invalidated, or the user opts out of app-centric enrollment on the backend side during the window between the initial QR validation and the actual enrollment/upload, the Orb will still proceed to complete biometric capture, fraud checks, and enrollment using the stale authorization snapshot. This can result in a signup being completed (and iris data being enrolled / PCP packages uploaded) under authorization data that is no longer valid at execution time — an unauthorized or misattributed signup completing on stale state, analogous to a user unexpectedly receiving execution at a stale/unwanted price in the reported DeFi bug.

### Likelihood Explanation
The window between the QR-validation check and the enrollment call is not fixed — it spans hardware biometric capture (which can time out or be retried), the full ML/fraud pipeline, and multiple network round-trips including a 6-retry upload loop with backoff: [6](#0-5) 
This gives a realistic, non-adversarial-input window (analogous to "congested mempool" in the original report) during which backend-side state can legitimately change, making the staleness condition plausible without requiring any malicious actor, hardware access, or a compromised peer/node.

### Recommendation
Re-validate operator/user authorization state (or at minimum re-check remaining TTL against `operator_qr_expiration_time`, and re-query `backend::user_status`/`backend::operator_status`) immediately before the enrollment-consuming step in `do_signup`, rejecting or re-prompting the signup if the authorization is no longer within a freshness bound at the point the state-changing action (enrollment / PCP tier upload) is executed.

### Proof of Concept
1. Operator scans QR code; `verify_operator_qr_code` succeeds and `OperatorData::timestamp` is recorded (`src/plans/mod.rs:849-853`).
2. User QR code is scanned and validated via `backend::user_status::request`, returning `UserData` (`src/backend/user_status.rs:147-163`).
3. `scan_remaining_qr_codes` confirms `operator_data.timestamp.elapsed() < operator_qr_expiration_time` and returns the resolved QR codes unchanged (`src/plans/mod.rs:796-805`).
4. During the subsequent biometric capture, ML pipeline, fraud-check, and PCP upload phases (which include a 6-attempt retry loop, `src/plans/mod.rs:1786-1799`), the backend independently revokes the operator or invalidates the user session.
5. `do_signup` proceeds to `enroll_user`/PCP upload using the already-fetched, now-stale `qr_codes.user_data`/`operator_data` without any re-validation call, completing the signup under authorization state that is no longer current.

### Citations

**File:** src/plans/mod.rs (L507-518)
```rust
        let mut result = self.start_signup(orb, dbus).await?;
        let Some(qr_codes) =
            self.scan_remaining_qr_codes(orb, qr_codes, operator_qr_expiration_time).await?
        else {
            return Ok(result);
        };
        let debug_report = result.debug_report.insert(DebugReport::builder(
            result.capture_start,
            &result.signup_id,
            &qr_codes,
            orb.config.lock().await.clone(),
        ));
```

**File:** src/plans/mod.rs (L550-563)
```rust
        // wait for the sound to finish and user to get ready before starting the capture
        sleep(Duration::from_millis(3000)).await;

        let capture = self.biometric_capture(orb, debug_report).await?;
        self.after_biometric_capture(orb, debug_report, capture.is_some(), self_serve).await?;
        let Some(capture) = capture else {
            return Ok(result);
        };
        if self.skip_pipeline() || debug_report.signup_extension_config.is_some() {
            result.success = true;
            return Ok(result);
        }
        let pipeline = Box::pin(self.biometric_pipeline(orb, debug_report, &capture)).await?;
        let fraud_detected = !self.skip_fraud_checks()
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

**File:** src/plans/mod.rs (L794-820)
```rust
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

**File:** src/plans/mod.rs (L1786-1799)
```rust
    ) -> Result<bool> {
        const RETRIES_COUNT: usize = 6;
        tracing::info!("Start uploading personal custody package");
        let t = Instant::now();
        for i in 0..RETRIES_COUNT {
            let response = backend::upload_personal_custody_package::request(
                signup_id,
                user_id,
                checksum.as_ref(),
                &data,
                tier,
                &orb.config,
            )
            .await;
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
