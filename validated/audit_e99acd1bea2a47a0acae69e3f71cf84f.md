### Title
Stale operator-QR validation reused for up to 23 hours allows signups to proceed under a revoked/changed operator identity - ([File: src/plans/mod.rs])

### Summary
In `src/plans/mod.rs`, `scan_initial_qr_codes` and `scan_remaining_qr_codes` cache the result of a single backend validation of the operator QR code (`OperatorData`, including `valid`/`location_data`) and reuse it for every subsequent signup as long as `operator_data.timestamp.elapsed() < operator_qr_expiration_time` — a window whose default is `Duration::from_secs(60 * 60 * 23)` (23 hours), per `src/config.rs`. This mirrors the report's bug class: an authorization decision (operator/distributor validity + location) made at time T0 is trusted unchanged at execution time T1..Tn without re-verifying the current state on the backend, even though that state (operator active/valid/location) can legitimately change during the window.

### Finding Description
`verify_operator_qr_code` calls `backend::operator_status::request(qr_code)` [1](#0-0)  once per operator QR scan, and the resulting `OperatorData { qr_code, location_data, timestamp }` is stored. Both callers that decide whether to trust this state for a *new* signup only check elapsed time, never re-validating with the backend:

- `scan_initial_qr_codes` only re-scans/re-validates if `ts.elapsed() > operator_qr_expiration_time` [2](#0-1) .
- `scan_remaining_qr_codes` reuses `operator_data` from a prior signup (`QrCodes::Both`/`QrCodes::Operator` branches) as long as `operator_data.timestamp.elapsed() < operator_qr_expiration_time`, skipping any call to `backend::operator_status::request` entirely for that path [3](#0-2) .

The cached `location_data` (including `session_coordinates` and `stationary_location_coordinates`, which are fraud-relevant per the doc comment "The operator's expected stationary location coordinates") [4](#0-3)  is then forwarded unchanged into `user_status::request` (used for user QR validation and fraud/location checks) [5](#0-4) , and the operator's `user_id` is submitted as `distributorId` on every subsequent `signup_post::request` within the window [6](#0-5) .

The default expiration window is 23 hours [7](#0-6) , so if the backend's authoritative state for that operator/distributor changes during that window (e.g., the operator's credential is revoked, blacklisted for fraud, or their approved/stationary location changes), the orb continues to treat the operator as valid and continues to bind every signup to the stale identity and stale location data — the operator/distributor state is never re-checked against the backend at signup time. This is directly analogous to the reported bug: an ID (`operator QR` here, `planetId` there) is validated once, but the mutable state behind it (`valid`/`location_data` here, `empireId` there) can change afterward, and the code performs the privileged action (signup, biometric enrollment, location-based fraud gating) using the stale state rather than re-verifying it, causing misattributed signups to be recorded under/against an operator/location that is no longer accurate.

### Impact Explanation
Signups performed during the (up to 23-hour) validity window after an operator's backend status changes will be misattributed to the wrong/no-longer-valid operator/distributor and will use outdated location data for location-based fraud checks. This can let a revoked or fraud-flagged operator's sessions continue producing valid signups, and can defeat the stationary-location fraud check by using coordinates captured before the operator moved or was reassigned — a fraud/location-check bypass reachable purely through normal operational timing, without needing privileged operator complicity to bypass, and worsened under any condition (self-serve deployments, long field days) that keeps the cached `operator_data` alive close to the 23-hour ceiling.

### Likelihood Explanation
Medium. This requires no attacker action beyond continuing to use the orb during the caching window after the backend-side operator state changes (revocation, fraud flag, relocation) — the same "natural occurrence during normal/high-load operation" scenario described in the source report, since the orb design intentionally reuses cached validation to reduce QR re-scans. The 23-hour default window makes the exposure window large in practice.

### Recommendation
Re-validate the operator QR code's status (and refresh `location_data`) against the backend before/at the time each new signup begins, rather than trusting a cached `OperatorData` purely based on elapsed time; at minimum, shorten `operator_qr_expiration_time` significantly and/or perform a lightweight re-check of operator validity immediately before submitting `signup_post::request` and before using cached `location_data` for fraud checks in `user_status::request`.

### Proof of Concept
1. Orb operator scans an operator QR code; `verify_operator_qr_code` validates it and caches `OperatorData{ valid: true, location_data, timestamp: t0 }` [8](#0-7) .
2. Multiple signups proceed using the same cached `operator_data` via `scan_remaining_qr_codes`'s reuse branches, with no additional call to `backend::operator_status::request` [3](#0-2) .
3. At some time `t1` (t0 < t1 < t0 + 23h) the backend revokes/reassigns the operator or the operator physically relocates, invalidating `valid`/`location_data`.
4. A signup at `t1` still uses the stale `operator_data`, submitting the (now invalid) operator id as `distributorId` in `signup_post::request` and stale coordinates to the user/fraud validation endpoint, with no re-check performed anywhere in this path.

### Citations

**File:** src/plans/mod.rs (L749-785)
```rust
    async fn scan_initial_qr_codes(
        &mut self,
        orb: &mut Orb,
        qr_codes: &mut QrCodes,
        self_serve: bool,
        operator_qr_expiration_time: Duration,
    ) -> Result<()> {
        if self_serve
            && qr_codes
                .operator_timestamp()
                .map_or(true, |ts| ts.elapsed() > operator_qr_expiration_time)
        {
            loop {
                let qr_capture_start = Instant::now();
                let operator_qr_code =
                    self.scan_operator_qr_code(orb, None).await?.expect("to never timeout");
                let Some(operator_qr_code) =
                    self.handle_magic_operator_qr_code(orb, operator_qr_code).await?
                else {
                    continue;
                };
                let Some((_, operator_location_data)) =
                    self.verify_operator_qr_code(orb, &operator_qr_code, qr_capture_start).await?
                else {
                    continue;
                };
                *qr_codes = QrCodes::Operator {
                    operator_data: OperatorData {
                        qr_code: operator_qr_code,
                        location_data: operator_location_data,
                        timestamp: Instant::now(),
                    },
                };
                break;
            }
        }
        Ok(())
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

**File:** src/plans/mod.rs (L1543-1577)
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
```

**File:** src/backend/operator_status.rs (L21-31)
```rust
/// Location data of the operator.
#[derive(Deserialize, Debug, Default, Clone)]
#[serde(rename_all = "camelCase")]
pub struct LocationData {
    /// The operator's team country.
    pub team_operating_country: String,
    /// The operator's coordinates during the session.
    pub session_coordinates: Coordinates,
    /// The operator's expected stationary location coordinates.
    pub stationary_location_coordinates: Option<Coordinates>,
}
```

**File:** src/backend/user_status.rs (L118-134)
```rust
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

**File:** src/backend/signup_post.rs (L125-133)
```rust
    let mut form = Form::new()
        .text("softwareVersion", &*ORB_OS_VERSION)
        .text("orbId", ORB_ID.as_str())
        .text("distributorId", operator_qr_code.user_id.clone())
        .text("userId", user_qr_code.user_id.clone())
        .text("region", s3_region.to_owned())
        .text("signature", signature.map_or(String::default(), Clone::clone))
        .text("codes", codes)
        .text("reason", signup_reason.to_screaming_snake_case().to_string());
```

**File:** src/config.rs (L443-443)
```rust
            operator_qr_expiration_time: Duration::from_secs(60 * 60 * 23),
```
