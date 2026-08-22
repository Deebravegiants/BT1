### Title
Stale operator QR-code authorization is reused for up to `operator_qr_expiration_time` (23h) across multiple signups without re-validation, enabling unauthorized signups after revocation - ([File: src/plans/mod.rs])

### Summary
`MasterPlan` validates an operator QR-code once through the backend via `verify_operator_qr_code` and then caches that "valid" result (as `OperatorData` with a `timestamp`) for reuse across many subsequent signups, as long as `operator_data.timestamp.elapsed() < operator_qr_expiration_time` (default 23 hours). This is structurally the same bug class as the MagicSpend `address(this).balance` check: a validity/authorization check performed once at "validation time" is trusted for many later "execution" events (each user signup) instead of being re-verified per use, so any change in the underlying authorization state that happens after the initial check is not reflected during the batch of dependent operations that follow.

### Finding Description
`verify_operator_qr_code` performs a single backend call (`backend::operator_status::request`) that returns `valid: true/false` plus location data for a given operator QR-code: [1](#0-0) 

The result of this one check is stored as `OperatorData` together with a capture `timestamp`: [2](#0-1) 

That `OperatorData` is then reused, without any further backend re-validation, for scanning and processing an arbitrary number of subsequent user QR-codes / signups, gated only by an elapsed-time check against `operator_qr_expiration_time`: [3](#0-2) [4](#0-3) 

`operator_qr_expiration_time` defaults to 23 hours: [5](#0-4) 

The core issue mirrors the referenced report: a balance/authorization check ("is this operator currently valid?") is performed once at a single point in time, and the result is trusted for a large batch of subsequent operations (every signup within the following up-to-23-hours window) rather than being re-checked at each point of actual use. Just as MagicSpend's validation-time balance check cannot guarantee funds remain available for every withdrawal executed later in the same or a later block, orb-core's operator-QR validation-time check cannot guarantee the operator is still authorized for every signup performed later in that up-to-23-hour window. If the backend revokes/deactivates the operator (e.g. distributor banned, fraud detected, location/compliance change) at any point after the initial scan, `orb-core` has no mechanism to detect this until the cached `OperatorData` expires, and will continue to accept and process new user signups under the stale authorization.

### Impact Explanation
Because the operator authorization is not re-verified per signup, an operator whose authorization is revoked by the backend mid-session can continue to have unauthorized signups performed and uploaded (biometric capture, PCP upload, `signup_post::request`) for up to `operator_qr_expiration_time` (23h) after revocation. This is an unauthorized-signup class impact: work performed on the Orb (biometric enrollment, image/PCP upload, backend `signups` record creation) proceeds under a distributor/operator identity that the backend no longer considers valid, and any operator-tied compliance/location gating (e.g. `stationary_location_coordinates`, `team_operating_country`) captured at the single check point is also stale for every later signup in that window.

### Likelihood Explanation
This requires no attacker action beyond normal operation: any legitimate revocation event (fraud detection, compliance ban, distributor deactivation) that happens after the operator QR is scanned, but before the cached authorization naturally expires, will result in signups proceeding on stale authorization. Given the default window is 23 hours, and operator QR-codes are explicitly designed to be reused across many signups within that window (`scan_remaining_qr_codes` re-uses `QrCodes::Operator` while `operator_data.timestamp.elapsed() < operator_qr_expiration_time`), this is a realistic operational scenario rather than a contrived one.

### Recommendation
Re-validate the operator authorization (or at minimum poll a lightweight revocation-check endpoint) before each new signup that reuses a cached `OperatorData`, rather than relying solely on the elapsed-time comparison against `operator_qr_expiration_time`. Alternatively, shorten the reuse window significantly and/or invalidate cached `OperatorData` proactively when backend config polling (`config_update` in `src/brokers/observer.rs`) detects operator-related config/status changes.

### Proof of Concept
1. Operator scans their QR code; `verify_operator_qr_code` succeeds and `OperatorData { timestamp: now }` is cached. [2](#0-1) 
2. Backend subsequently revokes/deactivates this operator (e.g., a fraud/compliance action) at `now + 1h`.
3. Because `operator_data.timestamp.elapsed() < operator_qr_expiration_time` (23h) still holds, `scan_remaining_qr_codes` continues to reuse the cached, now-stale `OperatorData` for every new signup request in `idle_wait_for_signup_request` / `scan_remaining_qr_codes` without calling `backend::operator_status::request` again: [3](#0-2) 
4. Multiple signups proceed and are uploaded to the backend (`signup_post::request`) tagged with this operator's QR-code, even though the backend has already revoked that operator - unauthorized signup processing under a revoked authorization, directly analogous to MagicSpend processing withdrawals that exceed the balance actually available at execution time.

### Citations

**File:** src/plans/mod.rs (L394-436)
```rust
    async fn idle_wait_for_signup_request(
        &mut self,
        orb: &mut Orb,
        qr_codes: &QrCodes,
        self_serve: bool,
        self_serve_button: bool,
        operator_qr_expiration_time: Duration,
    ) -> Result<Option<QrCodes>> {
        // We currently support 4 scenarios:
        // 1. Internal testing with a biometric input file.
        // 2. Self-serve mode that always scans for a user QR code.
        // 3. Self-serve mode that expects a button press to ask for a user QR code.
        // 4. Normal mode that expects a button press to ask for an operator QR code and then a user QR code.
        //
        // Scenarios 3 and 4 are handled by the same code path in the following last else-statement.
        let ui_idle_delay = self.ui_idle_delay.take();
        let qr_codes = if self.oneshot || self.has_biometric_input() {
            qr_codes.clone()
        } else if self_serve && !self_serve_button {
            orb.set_phase("User QR-code idle scanning").await;
            let QrCodes::Operator { operator_data } = &qr_codes else {
                panic!("operator QR code needs to be scanned beforehand in self-serve mode");
            };
            let Some((user_qr_code, user_data, user_qr_code_string)) = self
                .idle_scan_user_qr_code(
                    orb,
                    operator_data,
                    operator_qr_expiration_time,
                    ui_idle_delay,
                )
                .await?
            else {
                return Ok(None);
            };
            qr_codes.with_user_qr_code(user_qr_code, user_data, user_qr_code_string)
        } else {
            orb.set_phase("Idle waiting for button press").await;
            self.idle_wait_for_button_press(orb, ui_idle_delay).await?;
            orb.ui.signup_start_operator();
            qr_codes.clone()
        };
        Ok(Some(qr_codes))
    }
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

**File:** src/plans/mod.rs (L836-853)
```rust
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
```

**File:** src/plans/mod.rs (L1543-1578)
```rust
    /// Checks if `qr_code` is a valid operator QR-code through the backend.
    #[allow(clippy::cast_possible_truncation)]
    async fn verify_operator_qr_code(
        &self,
        orb: &mut Orb,
        qr_code: &qr_scan::user::Data,
        qr_capture_start: Instant,
    ) -> Result<Option<(u64, backend::operator_status::LocationData)>> {
        if qr_code.signup_extension() || self.operator_qr_code_override.is_some() {
            return Ok(Some((0, backend::operator_status::LocationData {
                team_operating_country: "DEV".to_string(),
                session_coordinates: Coordinates { latitude: 0.0f64, longitude: 0.0f64 },
                stationary_location_coordinates: None,
            })));
        }
        let http_start = Instant::now();
        match backend::operator_status::request(qr_code).await {
            Ok(backend::operator_status::Status { valid: true, location_data, reason: _ }) => {
                let location_data = location_data
                    .expect("to always have a result from the backend if valid == true");
                orb.ui.qr_scan_success(QrScanSchema::Operator);
                dd_incr!("main.count.global.distr_code_validated");
                tracing::info!("Operator QR-code validated: {qr_code:?}");
                dd_timing!("main.time.signup.distr_qr_code_capture", qr_capture_start);
                return Ok(Some((http_start.elapsed().as_millis() as u64, location_data)));
            }
            Ok(backend::operator_status::Status { valid: false, .. }) => {
                orb.ui.qr_scan_fail(QrScanSchema::Operator);
                dd_incr!("main.count.signup.result.failure.distr_qr_code", "type:invalid_qr");
            }
            Err(_) => {
                orb.ui.qr_scan_fail(QrScanSchema::Operator);
            }
        }
        Ok(None)
    }
```

**File:** src/config.rs (L443-443)
```rust
            operator_qr_expiration_time: Duration::from_secs(60 * 60 * 23),
```
