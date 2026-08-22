I have enough evidence to finalize the analog now.

The key finding: `handle_magic_operator_qr_code` in `src/plans/mod.rs` intercepts `MagicResetMirror`/`MagicResetWifi` QR codes **before** `verify_operator_qr_code` is ever called, meaning these privileged hardware-reconfiguration actions execute with zero backend/operator authentication — unlike the `Normal` operator QR-code path which requires backend validation via `backend::operator_status::request`.

### Title
Unauthenticated Hardware Reconfiguration via Magic QR-Codes Bypasses Operator Authorization - ([File: src/plans/mod.rs])

### Summary
The Orb's QR-code intake pipeline treats "magic" operator QR-codes (`magic_action:reset_wifi_credentials`, `magic_action:reset_mirror_calibration`) as privileged administrative commands but executes them without ever validating operator identity against the backend. This mirrors the reported `acceptedContracts` flaw: a single trust gate (successfully parsing a QR code) is reused to grant access to multiple, unrelated privileged capabilities without applying the correct authorization check to each capability.

### Finding Description
`qr_scan::operator::Data::try_parse` in [1](#0-0)  accepts any string matching the regex `magic_action:(\w+)` and maps `reset_wifi_credentials`/`reset_mirror_calibration` to `Data::MagicResetWifi`/`Data::MagicResetMirror` — no cryptographic signature, backend lookup, or operator credential is required to produce these variants.

In `scan_remaining_qr_codes` and `scan_initial_qr_codes`, the flow is:
1. `scan_operator_qr_code` — returns the parsed `qr_scan::operator::Data` (no auth).
2. `handle_magic_operator_qr_code` — is called **immediately after**, and for `MagicResetMirror`/`MagicResetWifi` it directly calls `self.reset_mirror_calibration(orb)` or `self.reset_wifi_and_ensure_network(orb)` and returns `Ok(None)`, short-circuiting the loop.
3. Only the `Normal(qr_code)` variant is passed on to `verify_operator_qr_code`, which performs the actual backend authentication call (`backend::operator_status::request`). [2](#0-1) [3](#0-2) [4](#0-3) 

Because `handle_magic_operator_qr_code` runs *before* `verify_operator_qr_code`, the magic actions never reach the backend-authenticated code path at all. The underlying privileged operations are:
- `reset_mirror_calibration` — overwrites the stored mirror calibration file and re-applies it to the mirror actuator: [5](#0-4) 
- `reset_wifi_and_ensure_network` — wipes the WiFi configuration (`network::reset()`, which runs `wpa-supplicant-interface restore-default-config` + `reconfigure`) and forces the orb into WiFi-QR pairing mode: [6](#0-5) , [7](#0-6) 

This is structurally the same root cause as the reported bug: the system uses one coarse-grained gate (a scanned QR code being parseable as `operator::Data`) to authorize several distinct privileged actions, but fails to apply the finer-grained authorization (backend operator validation) that the "normal" signup path enforces — a violation of least privilege between the two use cases (`Normal` operator authentication vs. `Magic*` maintenance actions).

### Impact Explanation
Any unprivileged person with physical/visual access to the orb's camera (i.e., anyone who can present a QR code to it — no operator badge, backend account, or credential needed) can force the device to:
- Overwrite/reset the mirror calibration used to steer the IR/RGB cameras during biometric capture, corrupting eye-tracking targeting used for iris capture and liveness/fraud checks.
- Reset the WiFi credentials/network, disconnecting the orb from its operating network (denial of service) and forcing it into an unauthenticated WiFi-pairing QR flow (`wifi::Plan.ensure_network_connection`), which itself accepts a scanned QR code without operator authentication ( [8](#0-7) ) — allowing an attacker to redirect the orb onto an attacker-controlled network.

This is a genuine authorization-bypass affecting core signup-adjacent state (mirror calibration integrity, network trust) reachable purely as an unprivileged user, not a hardware/operator-privileged attacker.

### Likelihood Explanation
High. The trigger requires only printing/displaying a short static string as a QR code and presenting it during the routine "scan operator QR-code" phase — no special access, timing, or race condition is needed. The `MAGIC_QR_CODE` regex and dispatch values are static and discoverable directly from source.

### Recommendation
Require the same operator-authentication step (`verify_operator_qr_code`/backend validation) for `MagicResetWifi`/`MagicResetMirror` as for `Normal` operator codes before invoking `reset_mirror_calibration` or `reset_wifi_and_ensure_network`, or otherwise gate these maintenance actions behind a separate, backend-verified administrative credential distinct from the generic "successfully parsed operator QR" trust level.

### Proof of Concept
1. Generate a QR code encoding the literal string `magic_action:reset_mirror_calibration` (or `magic_action:reset_wifi_credentials`).
2. Present it to the orb's camera during the "Operator QR-code scanning" phase (`scan_operator_qr_code`).
3. Observe `handle_magic_operator_qr_code` matches `Data::MagicResetMirror`/`Data::MagicResetWifi` and immediately invokes `reset_mirror_calibration`/`reset_wifi_and_ensure_network` — confirmed by the `main.count.signup.during.general.magic_qr.reset_mirror`/`reset_wifi` telemetry and `orb.ui.magic_qr_action_completed` UI signal in [9](#0-8)  — with no prior call to `backend::operator_status::request`.

### Citations

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

**File:** src/plans/mod.rs (L731-739)
```rust
    /// Resets the mirror calibration.
    pub async fn reset_mirror_calibration(&self, orb: &mut Orb) -> Result<()> {
        let calibration: Calibration = (&*orb.config.lock().await).into();
        calibration.store(CALIBRATION_FILE_PATH).await?;
        orb.enable_mirror()?;
        orb.recalibrate(calibration).await?;
        orb.disable_mirror();
        Ok(())
    }
```

**File:** src/plans/mod.rs (L741-747)
```rust
    /// Resets the network and requests a new one.
    pub async fn reset_wifi_and_ensure_network(&self, orb: &mut Orb) -> Result<()> {
        network::reset().await?;
        wifi::Plan.ensure_network_connection(orb).await?;
        orb.reset_rgb_camera().await?;
        Ok(())
    }
```

**File:** src/plans/mod.rs (L821-841)
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
```

**File:** src/plans/mod.rs (L978-1009)
```rust
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

**File:** src/plans/mod.rs (L1543-1558)
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
```

**File:** src/network/mod.rs (L101-123)
```rust
/// Restores the default wpa_supplicant.conf configuration file.
/// Then forces wpa_supplicant to re-read its configuration file,
/// thus disconnecting from the current network.
pub async fn reset() -> Result<()> {
    spawn_blocking(move || {
        Command::new(WPA_SUPPLICANT_INTERFACE_BIN)
            .arg("restore-default-config")
            .status()
            .wrap_err("running `wpa-supplicant-interface`")?
            .success()
            .then_some(())
            .ok_or_else(|| eyre!("`wpa-supplicant-interface` terminated unsuccessfully"))?;

        Command::new(WPA_SUPPLICANT_INTERFACE_BIN)
            .arg("reconfigure")
            .status()
            .wrap_err("running `wpa-supplicant-interface`")?
            .success()
            .then_some(())
            .ok_or_else(|| eyre!("`wpa-supplicant-interface` terminated unsuccessfully"))
    })
    .await?
}
```

**File:** src/plans/wifi/mod.rs (L43-68)
```rust
                network::Status::Connected { has_internet: false }
                | network::Status::Disconnected
                | network::Status::InProgress => {
                    tracing::debug!("Network is disconnected, or has no connection to the backend");
                    if has_requested_qr_code {
                        orb.ui.qr_scan_fail(QrScanSchema::Wifi);
                    }
                    has_requested_qr_code = true;
                    match qr_scan::Plan::new(None, false).run(orb).await? {
                        Ok((credentials, _)) => {
                            tracing::info!(
                                "Read WiFi credentials from hotspot QR: {:?}",
                                credentials
                            );
                            network::join(credentials).await?;
                            in_progress_start = Instant::now();
                        }
                        Err(qr_scan::ScanError::Invalid) => {
                            orb.ui.qr_scan_unexpected(
                                QrScanSchema::Wifi,
                                QrScanUnexpectedReason::WrongFormat,
                            );
                        }
                        Err(qr_scan::ScanError::Timeout) => {}
                    }
                    orb.reset_rgb_camera().await?;
```
