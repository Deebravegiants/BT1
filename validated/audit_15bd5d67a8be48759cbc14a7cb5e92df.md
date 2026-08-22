### Title
Inconsistent config snapshot allows user QR-code validation policy to change mid-signup, causing misattributed authorization - (File: src/plans/mod.rs)

### Summary
`MasterPlan::do_signup` and its sub-routines each independently re-acquire the shared `Arc<Mutex<Config>>` at different points in time during the same signup session instead of capturing one consistent configuration snapshot for the whole session. Because the backend config is refreshed asynchronously and continuously in the background (`Observer::config_update`), a signup that spans multiple QR scan attempts/retries can have its operator-QR verification governed by one policy and its user-QR verification governed by a different, more permissive policy fetched later in the same session — exactly the "adjustment applied retroactively to an in-progress unit of work that has not been fully updated" bug class.

### Finding Description
The signup flow reads `Config` from the shared, periodically-refreshed `Arc<Mutex<Config>>` multiple times, at different phases, rather than once atomically for the whole signup:

- At the top of `do_signup`, a snapshot of `Config` is taken (`self_serve`, `pcp_v3`, `operator_qr_expiration_time`, etc.): [1](#0-0) 

- Later, deep inside the same signup, `verify_user_qr_code` independently re-locks the same shared config to fetch `user_qr_validation_use_full_operator_qr` and `user_qr_validation_use_only_operator_location`, which govern how strictly the user QR-code is checked against the previously-scanned operator QR-code/location: [2](#0-1) 

- This call is reached from `scan_remaining_qr_codes`, which loops and can retry the operator/user QR scan multiple times before succeeding, each iteration invoking `verify_user_qr_code` (and thus re-reading "live" config) separately from the operator QR verification that happened earlier in the same loop: [3](#0-2) 

- Meanwhile, the backend config is refreshed on a fixed interval fully independently of any in-progress signup, with no coordination to prevent an update from landing mid-session: [4](#0-3) 

There is no mechanism analogous to "update all markets before changing the parameter": the running signup session is not tracked or paused/redone when configuration parameters that affect its outcome change; each phase of the signup simply consults whatever configuration happens to be current at the exact moment it executes.

### Impact Explanation
If governance/backend operators tighten or loosen `user_qr_validation_use_full_operator_qr` or `user_qr_validation_use_only_operator_location` while a signup session is already underway (e.g., during operator-QR retries, which can span an operator-controlled expiration window via `operator_qr_expiration_time`), the operator-QR-derived location/identity data captured under the old policy can end up being checked against the user's QR code under a newer, different policy than the one in effect when the operator step was verified. This can result in a user QR-code being validated (and a signup proceeding) against operator identity/location data that would not have passed under the policy in effect at operator-verification time — a misattributed/unauthorized signup binding between operator and user identity data, without any warning that config changes made "for future signups" can retroactively affect one already in progress.

### Likelihood Explanation
This requires no attacker sophistication beyond normal operation: it only requires (a) a signup session that spans more than one QR scan attempt (a common, expected retry path — wrong-format scans, timeouts, or the `operator_qr_expiration_time` loop), and (b) a legitimate backend config push occurring in that window, which happens routinely via the periodic `CONFIG_UPDATE_INTERVAL` job. No malicious operator/peer/hardware access is required — an ordinary backend configuration update during a normal, ongoing signup is sufficient to trigger the inconsistency.

### Recommendation
Capture a single, consistent `Config` snapshot at the very start of `do_signup` (or at the start of each signup attempt) and thread that same snapshot through every downstream check (`verify_operator_qr_code`, `verify_user_qr_code`, `scan_remaining_qr_codes`, etc.) instead of re-locking the shared, continuously-refreshed `Config` at each phase. Alternatively, defer applying newly downloaded config until any in-flight signup session completes, so policy changes never retroactively apply mid-session.

### Proof of Concept
1. Start a signup; the operator QR-code is scanned and verified under the current config (`user_qr_validation_use_full_operator_qr = true`), per `verify_operator_qr_code`.
2. The user fails to present a valid QR on the first attempt (wrong format / timeout), causing `scan_remaining_qr_codes`'s retry loop to iterate again without re-verifying the operator (`operator_data.timestamp.elapsed() < operator_qr_expiration_time` path at `src/plans/mod.rs:806-820`).
3. Meanwhile, the backend pushes a config update disabling `user_qr_validation_use_full_operator_qr` (background task in `src/brokers/observer.rs:187-205`), which is stored into the shared `Arc<Mutex<Config>>`.
4. On the retried attempt, `verify_user_qr_code` re-locks `Config` and now reads the updated, looser flag (`src/plans/mod.rs:1588-1598`), so the user QR-code is validated under a policy different from the one active when the operator QR was verified in step 1 — producing a signup approval that mixes two different security policies within one session.

### Citations

**File:** src/plans/mod.rs (L497-506)
```rust
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
```

**File:** src/plans/mod.rs (L788-868)
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
                _ => {
                    let qr_capture_start = Instant::now();
                    let Some(operator_qr_code) =
                        self.scan_operator_qr_code(orb, Some(self.qr_scan_timeout)).await?
                    else {
                        break Ok(None);
                    };
                    if !check_signup_conditions(orb).await? {
                        continue;
                    }
                    let Some(operator_qr_code) =
                        self.handle_magic_operator_qr_code(orb, operator_qr_code).await?
                    else {
                        break Ok(None);
                    };
                    let Some((duration_since_shot_ms, operator_location_data)) = self
                        .verify_operator_qr_code(orb, &operator_qr_code, qr_capture_start)
                        .await?
                    else {
                        continue;
                    };
                    // a delay following the scan allows for a better user experience & increases the chance of
                    // not reusing any previous RGB frame for the next QR-code scan
                    if let Some(delay) =
                        QR_SCAN_INTERVAL.checked_sub(Duration::from_millis(duration_since_shot_ms))
                    {
                        sleep(delay).await;
                    }
                    let operator_data = OperatorData {
                        qr_code: operator_qr_code,
                        location_data: operator_location_data,
                        timestamp: Instant::now(),
                    };
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
            }
        }
    }
```

**File:** src/plans/mod.rs (L1580-1598)
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
```

**File:** src/brokers/observer.rs (L187-205)
```rust
    fn config_update(&mut self, observer: &mut Observer) -> Result<()> {
        if self.before_config_update()? {
            match observer.config_update.as_mut().map(future::FutureExt::now_or_never) {
                Some(None) => return Ok(()),
                Some(Some(result)) => result??,
                None => {}
            }
            let config = Arc::clone(&observer.config);
            let ui = observer.ui.clone();
            observer.config_update = Some(tokio::spawn(async move {
                if let Ok(new_config) = Config::download().await {
                    *config.lock().await = new_config;
                    config.lock().await.propagate_to_ui(ui.as_ref());
                }
                Ok(())
            }));
        }
        Ok(())
    }
```
