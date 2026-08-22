### Title
Stale User-Validity/Identity-Binding Check Reused Across Long Signup Window Enables Cross-Signup State Bleed - (File: `src/plans/mod.rs`)

### Summary
The reported `LendingPool.deposit()` bug is a classic "checked-then-used-later" (slippage/TOCTOU) flaw: a value (`liquidityIndex`) is validated at request time but can drift before it is actually consumed, because there is no re-validation/guard at the point of use. `orb-core` has a structurally analogous pattern in the signup flow: the result of `verify_user_qr_code` (backend `user_status` validation, including identity-binding data such as `backend_iris_public_key`, `id_commitment`, `self_custody_user_public_key`, and `data_policy`) is cached once as `UserData` inside `QrCodes`/`ResolvedQrCodes`, and is reused unconditionally later in `do_signup` as long as the *operator* QR-code timestamp has not expired — with no re-check of the *user* validation state itself.

### Finding Description
In `scan_remaining_qr_codes`, cached `QrCodes::Both`/`QrCodes::Operator` variants are reused solely based on operator QR staleness: [1](#0-0) 

The user-facing validation happens once, in `handle_user_qr_code` → `verify_user_qr_code`, which calls the backend `user_status::request` and returns a `UserData` snapshot (crypto keys, `id_commitment`, `data_policy`, `user_centric_signup` flag): [2](#0-1) [3](#0-2) 

This `UserData` is carried forward as `qr_codes.user_data` and used, unrevalidated, at the very end of `do_signup` — after an arbitrary amount of time has elapsed for QR scanning, a 3-second wait, full biometric capture (which can run up to `self_serve_biometric_capture_timeout`/`BIOMETRIC_CAPTURE_TIMEOUT`), and the biometric pipeline — to decide whether the signup is "user-centric" (bypassing local enrollment entirely) and which encryption keys/identity-commitment to bind the captured biometrics to: [4](#0-3) 

The only "freshness" gate applied before reusing state is `operator_data.timestamp.elapsed() < operator_qr_expiration_time` — a check tied to the *operator*'s QR code, not to the *user's* backend validation result: [5](#0-4) [6](#0-5) 

This is directly analogous to the reported bug class: a value is fetched/verified once (`liquidityIndex` ≈ `UserData`/identity-binding keys), and is later consumed to determine a security-relevant outcome (`rTokenAmount` ≈ which cryptographic identity/keys the biometric package is bound to, or whether local fraud/enrollment checks are skipped) without re-checking that the originally-verified condition still holds at the time of use. There is no mechanism to re-poll `user_status` immediately before `enroll_user`/`build_pcp` to confirm the user's backend keys/`id_commitment`/`data_policy` are still the ones that should be bound to this specific biometric capture.

Compounding this, local fraud detection is a no-op in this build (`// FOSS: WE HAVE DELETED ALL FRAUD CHECKS`), so the `user_centric_signup` short-circuit path (which trusts the stale `UserData` entirely and skips `enroll_user`) is the only other backend-side check: [7](#0-6) 

### Impact Explanation
If a user's backend-side state (encryption keys, `id_commitment`, or `data_policy`) changes between the initial QR validation and the actual biometric enrollment/PCP-build step — whether due to backend-side key rotation, a race between two concurrent sessions for the same `user_id`, or an app-side state change during the multi-second capture+pipeline window — the orb will bind the newly captured biometric package (iris/face encryption, identity commitment) to a stale `UserData` snapshot. This risks misattributed signup binding (biometrics encrypted to/associated with an identity-commitment/public key that no longer matches the current legitimate session) or bypass of intended local logic gated on `user_centric_signup`/`data_policy`, which are exactly in the "misattributed signup" / "cross-signup state bleed" impact categories called out as in-scope.

### Likelihood Explanation
The window between validation and use is not instantaneous — it spans QR scanning of the remaining code, a fixed 3-second wait, full biometric capture (up to the capture timeout), and biometric pipeline processing — giving a non-trivial amount of time for backend-side state to change relative to when it was fetched. No re-validation call is made in that path before the stale `UserData` is consumed for building the PCP and deciding the enrollment/user-centric bypass logic.

### Recommendation
Re-validate (or at minimum re-fetch a freshness token/version for) the user's backend `user_status` data immediately before it is consumed in `build_pcp`/the `user_centric_signup` branch in `do_signup`, rather than trusting a `UserData` snapshot captured potentially minutes earlier. At minimum, apply an expiration policy to `UserData` analogous to `operator_qr_expiration_time`, and abort/re-scan if the user-side validation is stale at the point of use.

### Proof of Concept
1. Operator scans the operator QR code; user then scans the user QR code, triggering `verify_user_qr_code`, which fetches `UserData` (keys, `id_commitment`, `data_policy`) at time `T0` [8](#0-7) .
2. `do_signup` proceeds through `scan_remaining_qr_codes` (reused because operator timestamp is still fresh), a 3s sleep, `biometric_capture`, and `biometric_pipeline` — a multi-second-to-tens-of-seconds window before the cached `UserData` is consumed [9](#0-8) .
3. At time `T1 > T0`, if the backend-side state for that `user_id` has changed (e.g., re-issued keys, changed `data_policy`, or a second concurrent session overwrote server-side state), the orb still binds the just-captured biometrics using the `T0`-era `UserData` when it builds the PCP and decides the `user_centric_signup` short-circuit [4](#0-3) , with no re-check performed in between.

### Citations

**File:** src/plans/mod.rs (L456-467)
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
```

**File:** src/plans/mod.rs (L506-509)
```rust
        } = *orb.config.lock().await;
        let mut result = self.start_signup(orb, dbus).await?;
        let Some(qr_codes) =
            self.scan_remaining_qr_codes(orb, qr_codes, operator_qr_expiration_time).await?
```

**File:** src/plans/mod.rs (L550-562)
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

**File:** src/plans/mod.rs (L1085-1090)
```rust
        if let Some(user_data) =
            self.verify_user_qr_code(orb, &user_qr_code, operator_data, qr_capture_start).await?
        {
            return Ok(Some(Some((user_qr_code, user_data, user_qr_code_string))));
        }
        Ok(None)
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

**File:** src/plans/mod.rs (L1580-1622)
```rust
    /// Checks if `qr_code` is a valid user QR-code through the backend.
    async fn verify_user_qr_code(
        &self,
        orb: &mut Orb,
        user_qr_code: &qr_scan::user::Data,
        operator_data: &OperatorData,
        qr_capture_start: Option<Instant>,
    ) -> Result<Option<backend::user_status::UserData>> {
        let Config {
            user_qr_validation_use_full_operator_qr,
            user_qr_validation_use_only_operator_location,
            ..
        } = *orb.config.lock().await;
        match backend::user_status::request(
            user_qr_code,
            operator_data,
            user_qr_validation_use_full_operator_qr,
            user_qr_validation_use_only_operator_location,
        )
        .await
        {
            Ok(Some(user_data)) => {
                orb.ui.qr_scan_success(QrScanSchema::User);
                dd_incr!("main.count.signup.during.general.user_qr_code_validate");
                tracing::info!("User QR-code validated: {user_qr_code:?}");
                if let Some(qr_capture_start) = qr_capture_start {
                    dd_timing!("main.time.signup.user_qr_code_capture", qr_capture_start);
                }
                return Ok(Some(user_data));
            }
            Ok(None) => {
                orb.ui.qr_scan_fail(QrScanSchema::User);
                dd_incr!("main.count.signup.result.failure.user_qr_code", "type:invalid_qr");
            }
            Err(_) => {
                orb.ui.qr_scan_fail(QrScanSchema::User);
                dd_incr!(
                    "main.count.signup.result.failure.user_qr_code",
                    "type:validation_network_error"
                );
            }
        }
        Ok(None)
```
