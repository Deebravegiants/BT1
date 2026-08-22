### Title
Stale cached user/operator authorization is reused for signup without re-validation - (File: `src/plans/mod.rs`)

### Summary
The `IncentiveVoting.sol` report describes a re-registration function (`registerAccountWeight()`) that reuses previously-granted voting authority for a receiver without re-checking whether that receiver is still active, because the active-state check only exists in the sibling `_storeAccountVotes()` path. The analogous pattern exists in orb-core's signup state machine: once a user's QR-code authorization (`backend::user_status::UserData`) has been validated a single time by `verify_user_qr_code()`, the resulting `QrCodes::Both` variant is cached and re-used for the entire remaining lifetime of the operator QR-code window (`operator_qr_expiration_time`, default ~23 hours) without ever calling back into the backend to confirm the user's authorization is still valid.

### Finding Description
`MasterPlan::scan_remaining_qr_codes()` is the gate that resolves the `QrCodes` state into a `ResolvedQrCodes` used to drive the rest of the signup (biometric capture, pipeline, enrollment): [1](#0-0) 

Note the first match arm: if the enum is already `QrCodes::Both { operator_data, user_qr_code, user_data, user_qr_code_string }` and `operator_data.timestamp.elapsed() < operator_qr_expiration_time`, the function immediately returns the **cached** `user_data` without ever calling `backend::user_status::request` again — the only place that performs the "is this user authorized to sign up" check is `verify_user_qr_code()`: [2](#0-1) 

`QrCodes::Both` is produced once, during idle scanning, by `idle_scan_user_qr_code()` → `handle_user_qr_code()` → `verify_user_qr_code()`: [3](#0-2) 

That single validation result (including whether the user is authorized, `user_centric_signup`, `orb_relay_app_id`, and the backend-issued encryption keys used to build the Personal Custody Package) is carried forward as `qr_codes` into `do_signup()`, and then into `scan_remaining_qr_codes()`, which treats the presence of an unexpired operator timestamp as sufficient proof that the cached user authorization is still current: [4](#0-3) 

This is structurally identical to the `IncentiveVoting.sol` flaw: a state-changing/authorization check (`isReceiverActive` / `backend::user_status::request`) is performed once at grant time, but a downstream "continuation" code path (`registerAccountWeight()` / the `QrCodes::Both` branch of `scan_remaining_qr_codes()`) reuses the previously granted authorization for an extended period (until `operator_qr_expiration_time`, up to 23 hours by default) without re-verifying the condition that made the grant valid in the first place.

### Impact Explanation
If the backend revokes or invalidates a user's signup authorization after the initial QR validation (e.g., the user is flagged for fraud, blocked, or their session is otherwise invalidated) but before the cached `operator_qr_expiration_time` window elapses, the orb will continue to treat the previously-fetched `UserData` as valid and proceed through biometric capture and enrollment using stale authorization data, rather than re-checking with the backend. Because the operator QR expiration window is a full day by default, this creates a large time window during which a since-revoked authorization can still drive a signup attempt on the orb, relying entirely on `enroll_user`/`signup_post` at the very end of the pipeline to catch it server-side — mirroring how, in the original bug, `registerAccountWeight()` let a stale vote continue accruing weight for a receiver that had since been deactivated, relying only on a later, separate code path to eventually reject it.

### Likelihood Explanation
This path is reachable in the normal signup flow whenever an operator scans multiple users under one operator QR-code session (the standard non-self-serve or self-serve batch flow), and simply requires the elapsed time between the initial user QR validation and the actual signup completion to be less than `operator_qr_expiration_time`. No attacker-controlled input is needed beyond normal use of the device; likelihood is driven purely by the (long) default expiration window and does not require any special conditions.

### Recommendation
Re-verify user authorization (`backend::user_status::request` via `verify_user_qr_code`) whenever `scan_remaining_qr_codes()` is about to consume a cached `QrCodes::Both`/`QrCodes::Operator` value for an actual signup, instead of relying solely on the operator QR-code timestamp as a proxy for "the cached user authorization is still valid." At minimum, re-check user status immediately before `do_signup` transitions into biometric capture, similar to how `IncentiveVoting.sol`'s recommendation was to check `isReceiverActive` in every function that assigns or continues voting power.

### Proof of Concept
1. Operator scans their QR-code; `scan_initial_qr_codes` sets `QrCodes::Operator`.
2. First user scans their QR-code; `idle_scan_user_qr_code`/`handle_user_qr_code`/`verify_user_qr_code` call the backend once and cache `QrCodes::Both { operator_data, user_data, .. }` with `user_data` reflecting the user's authorization at that moment.
3. Backend-side, the user's authorization is revoked (e.g., fraud flag, block) shortly afterward, well within the `operator_qr_expiration_time` window (default ~23h).
4. `do_signup` runs `scan_remaining_qr_codes(orb, qr_codes, operator_qr_expiration_time)`; since `operator_data.timestamp.elapsed() < operator_qr_expiration_time`, the `QrCodes::Both` branch fires and returns the stale, cached `user_data` directly — no backend call is made to reconfirm the user's now-revoked status — and the signup proceeds into biometric capture with the previously valid `UserData`. [5](#0-4)

### Citations

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

**File:** src/plans/mod.rs (L490-512)
```rust
    #[allow(clippy::too_many_lines)]
    async fn do_signup(
        &mut self,
        orb: &mut Orb,
        qr_codes: QrCodes,
        dbus: Option<&zbus::SignalContext<'_>>,
    ) -> Result<SignupResult> {
        let Config {
            self_serve,
            pcp_v3,
            orb_relay_announce_orb_id_retries,
            orb_relay_announce_orb_id_timeout,
            orb_relay_shutdown_wait_for_pending_messages,
            orb_relay_shutdown_wait_for_shutdown,
            operator_qr_expiration_time,
            ..
        } = *orb.config.lock().await;
        let mut result = self.start_signup(orb, dbus).await?;
        let Some(qr_codes) =
            self.scan_remaining_qr_codes(orb, qr_codes, operator_qr_expiration_time).await?
        else {
            return Ok(result);
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

**File:** src/plans/mod.rs (L1580-1608)
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
```
