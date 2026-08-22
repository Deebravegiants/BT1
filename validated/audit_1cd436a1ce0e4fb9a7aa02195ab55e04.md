### Title
Unauthenticated Magic Operator QR-Codes Allow Any Unprivileged User to Trigger Privileged Orb Reset Actions Before Operator Authorization - (File: src/plans/mod.rs)

### Summary
The orb's operator QR-code intake flow parses and executes "magic" reset actions (`MagicResetWifi`, `MagicResetMirror`) encoded in a scanned QR-code *before* the operator identity is authenticated against the backend. Because `qr_scan::operator::Data::try_parse` recognizes any string of the form `magic_action:reset_wifi_credentials` or `magic_action:reset_mirror_calibration` [1](#0-0)  and `handle_magic_operator_qr_code` immediately executes the corresponding reset without any prior authorization check [2](#0-1) , any bystander able to present such a QR-code to the orb's camera can repeatedly trigger these privileged state-mutating actions with no credentials and no cost — structurally the same "no access-control on a state-mutating, unbounded-repeat action" flaw as `lockOnBehalf`.

### Finding Description
In `scan_remaining_qr_codes`, the control flow for acquiring operator credentials is:

1. `scan_operator_qr_code` — scans/decodes the QR text into a `qr_scan::operator::Data` value.
2. `handle_magic_operator_qr_code` — dispatches on the parsed value.
3. `verify_operator_qr_code` — the only point that calls the backend (`backend::operator_status::request`) to confirm the scanned code actually belongs to a valid, authorized operator. [3](#0-2) 

Critically, step 2 happens **before** step 3. Inside `handle_magic_operator_qr_code`, the `MagicResetMirror` and `MagicResetWifi` branches call `self.reset_mirror_calibration(orb)` / `self.reset_wifi_and_ensure_network(orb)` directly and then return `Ok(None)`, which causes `scan_remaining_qr_codes` to abort the current signup attempt (`break Ok(None)`) — the backend `verify_operator_qr_code` call is never reached for these branches: [2](#0-1) 

Only the `Data::Normal(qr_code)` branch (a normal `userid:...` operator code) proceeds to `verify_operator_qr_code`, which performs the actual backend-authenticated check that the presented ID belongs to a real, authorized operator [4](#0-3)  and [5](#0-4) .

The QR-code parser itself performs no authentication — it is a pure regex match on unsigned, unauthenticated plaintext (`magic_action:<word>`), unlike the cryptographically-verified user QR-code path (`decode_qr` / `user_data_hash` verification) [6](#0-5) . There is no operator-identity check, no rate limit, and no minimum requirement (analogous to the missing `_quantity` check in `lockOnBehalf`) gating these two branches.

This is structurally identical to the `lockOnBehalf` root cause: a state-mutating entry point that is reachable by an unprivileged caller (anyone who can show a QR code to the camera, exactly the same interaction surface as a legitimate operator/self-serve user) and that has no access control, allowing the caller to repeatedly force a privileged reset action against the shared device state.

### Impact Explanation
- `MagicResetWifi` invalidates/reconfigures the orb's saved Wi‑Fi credentials/network state; a bystander can repeatedly trigger this at will, denying the legitimate operator's ability to keep the device online and process signups (network-availability griefing directly analogous to the victim being denied withdrawal via repeated `unlockTime` extension).
- `MagicResetMirror` forces a full mirror recalibration cycle; repeatedly triggering it degrades or blocks the biometric-capture pipeline (fraud/liveness-adjacent enforcement path), preventing legitimate signups from completing.
- Because no operator authentication occurs before executing the action, this is not merely an "authorized operator misusing a feature" scenario — it is exploitable by anyone with no privilege and at zero cost, purely via the same QR-scanning interaction the device already exposes to walk-up users.
- This qualifies as a fraud/liveness/signup-availability disruption impact category (denial of legitimate signup capability), consistent with the accepted impact classes for this analog scan.

### Likelihood Explanation
High. The only precondition is the ability to print/display a short text string as a QR-code and present it to the orb's camera during the normal operator QR-code scanning phase — the exact same interaction surface used by legitimate operators/users, requiring no special hardware access, no credential, and no cost. It can be repeated indefinitely.

### Recommendation
Move the `handle_magic_operator_qr_code` dispatch to occur **after** `verify_operator_qr_code` succeeds (i.e., require a backend-validated operator identity before executing `MagicResetWifi`/`MagicResetMirror`), or otherwise gate these two magic actions behind an authenticated-operator check equivalent to the one already used for the `Normal` operator QR-code branch. Additionally, consider rate-limiting/cooldown for these reset actions regardless of authorization to bound their impact.

### Proof of Concept
1. Generate a QR code encoding the literal string `magic_action:reset_wifi_credentials` (or `magic_action:reset_mirror_calibration`).
2. Present it to the orb during the "Operator QR-code scanning" phase (`scan_operator_qr_code`).
3. `qr_scan::operator::Data::try_parse` matches the `MAGIC_QR_CODE` regex and returns `Data::MagicResetWifi` (or `Data::MagicResetMirror`) — no cryptographic/backend validation is performed at parse time [1](#0-0) .
4. `scan_remaining_qr_codes` calls `handle_magic_operator_qr_code`, which immediately executes `reset_wifi_and_ensure_network`/`reset_mirror_calibration` and returns, short-circuiting before `verify_operator_qr_code` is ever invoked [7](#0-6) .
5. Repeat step 1–4 indefinitely; each repetition succeeds with no operator credential and no cost, denying the legitimate operator continuous Wi‑Fi/mirror-calibration availability.

Note: I could not locate the bodies of `reset_wifi_and_ensure_network`/`reset_mirror_calibration` within the indexed content (only their call sites and the sibling `reset_mirror_calibration` helper shown at [8](#0-7)  were retrievable); due to index size limits some file contents may not be fully available. If a full confirmation of the exact side effects of `reset_wifi_and_ensure_network` is needed, a Devin session with full repository access should be used to inspect it directly.

### Citations

**File:** src/plans/qr_scan/operator.rs (L11-22)
```rust
static MAGIC_QR_CODE: Lazy<Regex> = Lazy::new(|| {
    Regex::new(
        r"(?x)
        ^
        magic_action
        :
        (?P<magic_action>[\w]+)
        $
    ",
    )
    .expect("bad regex")
});
```

**File:** src/plans/qr_scan/operator.rs (L40-61)
```rust
    fn try_parse(code: &str) -> Option<Self> {
        let normal = user::Data::try_parse(code)
            .filter(
                |d| if d.signup_extension() { d.signup_extension_config.is_some() } else { true },
            )
            .map(Data::Normal);
        if normal.is_some() {
            return normal;
        }
        if let Some(captures) = MAGIC_QR_CODE.captures(code) {
            return match captures
                .name("magic_action")
                .expect("magic_action group must be present")
                .as_str()
            {
                "reset_wifi_credentials" => Some(Data::MagicResetWifi),
                "reset_mirror_calibration" => Some(Data::MagicResetMirror),
                _ => None,
            };
        }
        None
    }
```

**File:** src/plans/mod.rs (L731-738)
```rust
    /// Resets the mirror calibration.
    pub async fn reset_mirror_calibration(&self, orb: &mut Orb) -> Result<()> {
        let calibration: Calibration = (&*orb.config.lock().await).into();
        calibration.store(CALIBRATION_FILE_PATH).await?;
        orb.enable_mirror()?;
        orb.recalibrate(calibration).await?;
        orb.disable_mirror();
        Ok(())
```

**File:** src/plans/mod.rs (L821-1009)
```rust
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

    /// Scans the operator QR-code.
    /// Returns the operator data and the duration of the HTTP request
    /// used to check the operator ID for consistent UX.
    /// An artificial delay is added before returning for better UX.
    async fn scan_operator_qr_code(
        &self,
        orb: &mut Orb,
        timeout: Option<Duration>,
    ) -> Result<Option<qr_scan::operator::Data>> {
        orb.set_phase("Operator QR-code scanning").await;
        let qr_capture_start = Instant::now();
        loop {
            dd_incr!("main.count.signup.during.general.distributor_identification_request");

            let remaining_timeout = timeout
                .map(|timeout| {
                    timeout
                        .checked_sub(qr_capture_start.elapsed())
                        .ok_or(qr_scan::ScanError::Timeout)
                })
                .transpose();
            #[cfg_attr(not(feature = "internal-data-acquisition"), allow(unused_mut))]
            let mut result = match remaining_timeout {
                Ok(timeout) => {
                    if let Some(qr) = &self.operator_qr_code_override {
                        tracing::info!("Operator QR-code provided from CLI");
                        Ok(qr.clone())
                    } else {
                        qr_scan::Plan::<qr_scan::operator::Data>::new(timeout, false)
                            .run(orb)
                            .await?
                            .map(|(qr_code, _)| qr_code)
                    }
                }
                Err(err) => Err(err),
            };
            #[cfg(feature = "internal-data-acquisition")]
            if !self.data_acquisition {
                result = result.and_then(|data| {
                    if let qr_scan::operator::Data::Normal(data) = &data {
                        if data.signup_extension {
                            return Err(qr_scan::ScanError::Invalid);
                        }
                    }
                    Ok(data)
                });
            }
            orb.reset_rgb_camera().await?;
            match result {
                Ok(qr_code) => {
                    orb.ui.qr_scan_completed(QrScanSchema::Operator);
                    dd_incr!("main.count.global.distr_code_detected");
                    return Ok(Some(qr_code));
                }
                Err(qr_scan::ScanError::Invalid) => {
                    orb.ui.qr_scan_unexpected(
                        QrScanSchema::Operator,
                        QrScanUnexpectedReason::WrongFormat,
                    );
                    dd_incr!("main.count.signup.result.failure.distr_qr_code", "type:wrong_format");
                    continue; // retry
                }
                Err(qr_scan::ScanError::Timeout) => {
                    orb.ui.qr_scan_timeout(QrScanSchema::Operator);
                    dd_incr!("main.count.signup.result.failure.distr_qr_code", "type:timeout");
                    tracing::error!("Timeout while scanning operator QR-code");
                    return Ok(None);
                }
            }
        }
    }

    /// Scans the user QR-code.
    async fn scan_user_qr_code(
        &self,
        orb: &mut Orb,
        operator_data: &OperatorData,
    ) -> Result<Option<(qr_scan::user::Data, backend::user_status::UserData, String)>> {
        orb.set_phase("User QR-code scanning").await;
        dd_incr!("main.count.signup.during.general.user_identification_request");

        // QR capture starts now and timeout is updated after each scan attempt
        let qr_capture_start = Instant::now();
        loop {
            let scan_result = if let Some(new_timeout_ms) =
                self.qr_scan_timeout.checked_sub(qr_capture_start.elapsed())
            {
                if let Some(qr) = &self.user_qr_code_override {
                    tracing::info!("User QR-code provided from CLI");
                    Ok(qr.clone())
                } else {
                    orb.reset_rgb_camera().await?;
                    qr_scan::Plan::<qr_scan::user::Data>::new(Some(new_timeout_ms), false)
                        .run(orb)
                        .await?
                }
            } else {
                Err(qr_scan::ScanError::Timeout)
            };
            if let Some(result) = self
                .handle_user_qr_code(scan_result, orb, operator_data, Some(qr_capture_start))
                .await?
            {
                break Ok(result);
            }
        }
    }

    async fn handle_magic_operator_qr_code(
        &self,
        orb: &mut Orb,
        qr_code: qr_scan::operator::Data,
    ) -> Result<Option<qr_scan::user::Data>> {
        match qr_code {
            qr_scan::operator::Data::Normal(qr_code) => {
                tracing::info!("Operator QR-code detected: {qr_code:?}");
                Ok(Some(qr_code))
            }
            qr_scan::operator::Data::MagicResetMirror => {
                tracing::info!("Magic QR-code detected: Reset Mirror");
                dd_incr!("main.count.signup.during.general.magic_qr.reset_mirror");
                let result = self.reset_mirror_calibration(orb).await;
                if let Err(err) = &result {
                    tracing::error!("Failed to reset mirror calibration: {err}");
                }
                orb.ui.magic_qr_action_completed(result.is_ok());
                Ok(None)
            }
            qr_scan::operator::Data::MagicResetWifi => {
                tracing::info!("Magic QR-code detected: Reset Wi-Fi");
                dd_incr!("main.count.signup.during.general.magic_qr.reset_wifi");
                let result = self.reset_wifi_and_ensure_network(orb).await;
                if let Err(err) = &result {
                    tracing::error!("Failed to reset wifi: {err}");
                }
                orb.ui.magic_qr_action_completed(result.is_ok());
                Ok(None)
            }
        }
    }
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

**File:** src/backend/operator_status.rs (L45-76)
```rust
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
    if status.location_data.is_none() {
        tracing::error!("Operator location data are missing");
        return Ok(Status {
            valid: false,
            location_data: None,
            reason: Some("Operator location data are missing".to_string()),
        });
    }
    Ok(status)
}
```
