Confirmed: `operator_qr_expiration_time` defaults to 23 hours [1](#0-0) , and `scan_remaining_qr_codes` reuses a previously validated `OperatorData` for that entire window without re-checking the backend as long as `operator_data.timestamp.elapsed() < operator_qr_expiration_time` [2](#0-1) .

### Title
Signup Authorization Accepts Stale Operator Validation for up to 23 Hours - (File: src/plans/mod.rs)

### Summary
`verify_operator_qr_code` performs a one-time backend validation of an operator QR code and its `LocationData`, then caches the result in `OperatorData { timestamp: Instant::now(), .. }`. `scan_remaining_qr_codes` and `scan_initial_qr_codes` reuse this cached, already-validated `OperatorData` for every subsequent signup as long as `operator_data.timestamp.elapsed() < operator_qr_expiration_time`, which defaults to 23 hours. This mirrors the StakingKo bug class: a backend-issued authorization/attestation (analogous to a signed price) is accepted for use throughout its entire validity window even though the authoritative state it represents (operator validity, location, permissions) may have changed in the interim.

### Finding Description
`verify_operator_qr_code` calls `backend::operator_status::request(qr_code)` once and returns `(elapsed_ms, LocationData)` on success [3](#0-2) . The caller wraps this into `OperatorData { qr_code, location_data, timestamp: Instant::now() }` [4](#0-3) .

In `scan_remaining_qr_codes`, subsequent signup attempts check only `operator_data.timestamp.elapsed() < operator_qr_expiration_time` to decide whether to reuse this previously fetched `OperatorData` instead of re-validating with the backend [5](#0-4) . `operator_qr_expiration_time` defaults to `Duration::from_secs(60 * 60 * 23)` — 23 hours [1](#0-0) .

This cached, stale `OperatorData` (including `location_data.session_coordinates`) is then fed directly into `verify_user_qr_code`, which — depending on `user_qr_validation_use_only_operator_location` (default `true`) or `user_qr_validation_use_full_operator_qr` — uses the *stale* operator location/identity to authorize each new user's signup against the backend `/api/v2/session/{user_id}/status` endpoint [6](#0-5) [7](#0-6) . There is no re-check that the operator's authorization is still current at the time each individual signup is validated — exactly the same root cause as the StakingKo bug: an authorization decision computed at time T is trusted as valid for an entire window afterward, regardless of intervening state changes at the source of truth.

### Impact Explanation
If an operator's authorization is revoked, their assigned location/country changes, or session coordinates become invalid on the backend during this up-to-23-hour window (e.g., an operator's field-deployment permission is pulled mid-shift, or the operator moves outside an authorized region), the orb continues to authorize new user signups against the stale `OperatorData` without re-querying `operator_status::request`. Because the backend's `/api/v2/session/{user_id}/status` check uses `operator_data.location_data.session_coordinates` for location-gated signup decisions, a revoked or relocated operator can still enable unauthorized signups for the remainder of the cached window — a form of unauthorized/misattributed signup authorization caused by stale trusted data, matching the "outdated but not yet expired signature" pattern in the report.

### Likelihood Explanation
This is reachable by any operator/orb session in normal operation, not by a privileged attacker — it only requires the backend-side operator status to change (revocation, relocation, or config change) while an operator's local orb session has already cached a valid `OperatorData` and continues performing signups within the 23-hour default window. No privileged access or credential compromise is needed; the flaw is purely in the client-side trust duration versus the freshness of the underlying authorization.

### Recommendation
Reduce reliance on locally cached authorization for a fixed wall-clock window; instead re-validate `operator_status::request` on some materially shorter cadence, or attach a monotonically increasing version/generation identifier from the backend to each operator status response and reject cached `OperatorData` whose generation is behind the backend's current one (mirroring the report's recommendation to add an incrementing ID to the signed message and reject stale generations, rather than relying purely on a time-based expiry).

### Proof of Concept
1. Operator scans their QR code; `verify_operator_qr_code` succeeds and `OperatorData { timestamp: T0 }` is cached in-memory for the orb session [8](#0-7) .
2. Backend operator status is later flipped to invalid/relocated (e.g., operator badge revoked) at T0 + 1 hour.
3. A new signup is attempted at T0 + 2 hours (well within the 23-hour `operator_qr_expiration_time`). `scan_remaining_qr_codes` matches the `QrCodes::Operator { operator_data } if operator_data.timestamp.elapsed() < operator_qr_expiration_time` branch and skips re-calling `verify_operator_qr_code` entirely [9](#0-8) .
4. `scan_user_qr_code`/`verify_user_qr_code` proceeds using the stale `operator_data.location_data`, allowing the backend user-status check to be evaluated against a now-invalid operator context, enabling a signup that should have been blocked.

### Citations

**File:** src/config.rs (L438-438)
```rust
            user_qr_validation_use_only_operator_location: true,
```

**File:** src/config.rs (L443-443)
```rust
            operator_qr_expiration_time: Duration::from_secs(60 * 60 * 23),
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

**File:** src/backend/user_status.rs (L112-134)
```rust
#[cfg(not(feature = "skip-user-qr-validation"))]
async fn do_request(
    qr_code: &qr_scan::user::Data,
    operator_data: &OperatorData,
    use_full_operator_qr: bool,
    use_only_operator_location: bool,
) -> Result<Response> {
    let request = if use_only_operator_location {
        super::client()?
            .get(format!("{}/api/v2/session/{}/status", *SIGNUP_BACKEND_URL, qr_code.user_id,))
            .query(&[
                ("lat", operator_data.location_data.session_coordinates.latitude),
                ("lon", operator_data.location_data.session_coordinates.longitude),
            ])
    } else if use_full_operator_qr {
        super::client()?
            .get(format!("{}/api/v2/session/{}/status", *SIGNUP_BACKEND_URL, qr_code.user_id))
            .query(&[("operator_id", &operator_data.qr_code.user_id)])
    } else {
        super::client()?
            .get(format!("{}/api/v1/user/{}/status", *SIGNUP_BACKEND_URL, qr_code.user_id))
    }
    .basic_auth(&*ORB_ID, Some(get_orb_token()?));
```
