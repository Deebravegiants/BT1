### Title
Overlong `operator_qr_expiration_time` (up to 23h) allows stale operator authorization/location data to gate signups without re-validation - (File: src/config.rs, src/plans/mod.rs)

### Summary
The `HEARTBEAT_TIME` bug class describes a validity window for externally-fetched trust data (an oracle price) that is set far larger than the data's actual freshness guarantee, letting stale data be trusted for security-relevant decisions. The orb-core analog is `operator_qr_expiration_time`, a config-controlled TTL that governs how long a previously backend-verified operator QR code and its associated location/authorization data (`OperatorData`) may be reused to gate signup flows without re-querying the backend. Its default value is 23 hours [1](#0-0) , an interval large enough that operator revocation, fraud flags, or location changes on the backend during that window are not observed by the orb.

### Finding Description
`OperatorData` carries an `Instant` timestamp captured at the moment the operator QR code was verified against the backend via `verify_operator_qr_code`, which calls `backend::operator_status::request` to check `valid` and fetch `LocationData` [2](#0-1)  and [3](#0-2) .

Both the idle loop and the main signup loop reuse this cached `OperatorData` — including its location/validity data — as long as `operator_data.timestamp.elapsed() < operator_qr_expiration_time`, skipping a fresh backend verification entirely: [4](#0-3) 

The initial QR scan follows the same pattern, only re-scanning the operator QR when the cached timestamp has exceeded `operator_qr_expiration_time` [5](#0-4) .

`operator_qr_expiration_time` defaults to `Duration::from_secs(60 * 60 * 23)` (23 hours) [1](#0-0) , and is only overridden by an operator-controlled backend config field with no documented minimum/maximum bound [6](#0-5) , mirroring the original `HEARTBEAT_TIME` pattern of an arbitrarily large, hardcoded/backend-set freshness window for a security-relevant piece of externally-sourced data.

### Impact Explanation
The cached `operator_data` (including `valid` status implicitly assumed and `LocationData`) is used to gate the entire signup flow: it is passed into `scan_user_qr_code`/`verify_user_qr_code` for user QR validation, embedded into `DebugReport` location fields [7](#0-6) , and reused across potentially many signups performed in the idle loop before re-verification. If the backend revokes an operator's authorization, flags the operator for fraud, or the operator's expected/stationary location changes at any point within the up-to-23-hour reuse window, the orb continues treating the operator as valid and continues to authorize and geographically attribute signups to that stale data — producing signups that should have been blocked or misattributed to an incorrect location/operator team. This matches the "unauthorized or misattributed signup" impact class.

### Likelihood Explanation
This is reachable in the normal, non-privileged signup flow (both operator-driven and self-serve idle scanning), requiring no hardware access or malicious peer — only that a backend-side operator status change occurs during an already-in-progress or resumed reuse window, which is a realistic operational scenario (revocation, fraud flag, operator reassignment) rather than a contrived edge case.

### Recommendation
Reduce the default/allowed `operator_qr_expiration_time` to a much shorter, bounded interval commensurate with how quickly operator status can change on the backend, and/or force re-verification of operator validity (not just re-use of cached `LocationData`) before each new signup rather than only after the TTL elapses. Consider validating server-provided `operator_qr_expiration_time` against a strict maximum in `Config::validate`.

### Proof of Concept
1. Operator scans QR at t=0; backend confirms `valid: true` and returns `LocationData`; `OperatorData.timestamp = Instant::now()` is cached [8](#0-7) .
2. At the backend, the operator is revoked/flagged for fraud at t=1h.
3. Because `operator_data.timestamp.elapsed() < operator_qr_expiration_time` (23h default) still holds, subsequent calls to `scan_remaining_qr_codes` skip re-verification and reuse the stale, now-invalid `operator_data` to authorize new signups [4](#0-3) , allowing unauthorized signups to proceed under a revoked operator's stale authorization for up to 22 more hours.

### Citations

**File:** src/config.rs (L443-443)
```rust
            operator_qr_expiration_time: Duration::from_secs(60 * 60 * 23),
```

**File:** src/plans/mod.rs (L756-760)
```rust
        if self_serve
            && qr_codes
                .operator_timestamp()
                .map_or(true, |ts| ts.elapsed() > operator_qr_expiration_time)
        {
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

**File:** src/plans/mod.rs (L849-853)
```rust
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

**File:** src/backend/operator_status.rs (L33-66)
```rust
/// Operator ID validation status.
#[derive(Deserialize, Debug)]
#[serde(rename_all = "camelCase")]
pub struct Status {
    /// Whether the operator ID is valid.
    pub valid: bool,
    /// Location data of the operator.
    pub location_data: Option<LocationData>,
    /// If 'valid == false', the 'reason' field contains the reason for the invalidation.
    pub reason: Option<String>,
}

/// Makes a validation request.
pub async fn request(qr_code: &qr_scan::user::Data) -> Result<Status> {
    let request = super::client()?
        .get(format!(
            "{}/api/v1/distributor/{}/orb/{}/status",
            *SIGNUP_BACKEND_URL, qr_code.user_id, *ORB_ID
        ))
        .basic_auth(&*ORB_ID, Some(get_orb_token()?));
    let status: Status = match request.send().await?.error_for_status() {
        Ok(response) => response.json().await?,
        Err(err) => {
            tracing::error!("Received error response {err:?}");
            return Err(err.into());
        }
    };
    if !status.valid {
        tracing::info!(
            "Operator QR-code invalid: {qr_code:?}, reason: {:?}",
            status.reason.as_deref().unwrap_or("<empty>")
        );
        return Ok(status);
    }
```

**File:** src/backend/config.rs (L74-74)
```rust
    pub operator_qr_expiration_time: Option<u64>,
```

**File:** src/debug_report.rs (L794-852)
```rust
impl DebugReport {
    #[must_use]
    pub fn builder(
        start_timestamp: SystemTime,
        signup_id: &SignupId,
        qr_codes: &plans::ResolvedQrCodes,
        backend_config: Config,
    ) -> Builder {
        let plans::ResolvedQrCodes {
            operator_data,
            user_qr_code,
            user_data,
            user_qr_code_string: _,
        } = qr_codes;
        let combined_signup_extension_config = user_qr_code
            .signup_extension_config
            .as_ref()
            .or(operator_data.qr_code.signup_extension_config.as_ref())
            .cloned();
        Builder {
            start_timestamp,
            signup_id: signup_id.clone(),
            operator_qr_code: operator_data.qr_code.clone(),
            user_qr_code: user_qr_code.clone(),
            user_qr_data: user_data.clone(),
            signup_extension_config: combined_signup_extension_config,
            biometric_capture_succeeded: false,
            signup_status: None,
            enrollment_status: None,
            extension_report: None,
            identification_images: None,
            rgb_net_left: None,
            rgb_net_right: None,
            fraud_check_results: FraudCheckResults::default(),
            iris_model_metadata_left: None,
            iris_model_metadata_right: None,
            pipeline_errors: PipelineErrors::default(),
            mega_agent_one_config: None,
            mega_agent_two_config: None,
            biometric_capture_gps_location: None,
            hardware_component_config: HardwareComponentConfig::default(),
            internal_state_data: InternalStateData::default(),
            rgb_camera: Vec::new(),
            ir_camera: Vec::new(),
            ir_face_camera: Vec::new(),
            thermal_camera: Vec::new(),
            self_custody_camera: Vec::new(),
            self_custody_bundle: None,
            self_custody_thumbnail: None,
            left_iris_normalized_image: None,
            right_iris_normalized_image: None,
            left_iris_normalized_image_resized: None,
            right_iris_normalized_image_resized: None,
            identification_image_ids: None,
            location_data: LocationData::new(
                backend_config.operation_country,
                backend_config.operation_city,
                operator_data.location_data.clone(),
            ),
```
