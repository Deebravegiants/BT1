### Title
Unauthenticated "Magic" Operator QR-Codes Allow Any Unprivileged Person to Trigger Wi-Fi Reset and Mirror Recalibration - ([File: src/plans/mod.rs])

### Summary
The Orb's operator QR-code scanning path accepts special "magic" QR codes (`magic_action:reset_wifi_credentials` and `magic_action:reset_mirror_calibration`) that trigger privileged, state-mutating hardware actions. Unlike normal operator/user QR codes, these magic codes are recognized purely by regex format matching and are executed with no backend authorization check, no operator identity verification, and no rate limiting — mirroring the reported bug class where a code path lacks required validation before performing a sensitive action, enabling griefing by any unprivileged party who can present a printed or displayed QR code to the Orb's camera.

### Finding Description
The operator QR-code schema recognizes three variants: a normal QR code and the two magic actions, distinguished purely by regex format: [1](#0-0) 

Unlike the `Normal` variant, whose value is later sent to `verify_operator_qr_code`, which calls the backend `operator_status::request` to validate that the operator ID is actually a legitimate operator before the QR code is trusted, the magic variants are handled by `handle_magic_operator_qr_code` and executed immediately, with **no backend verification at all**: [2](#0-1) 

`MagicResetWifi` calls `reset_wifi_and_ensure_network`, which restores wpa_supplicant to its default config and disconnects the Orb from its currently configured Wi-Fi network: [3](#0-2) [4](#0-3) 

`MagicResetMirror` calls `reset_mirror_calibration`, which overwrites the on-disk mirror calibration file and re-runs mirror recalibration: [5](#0-4) 

Both are reachable from the idle-scanning loop that runs continuously whenever the Orb is idle and waiting for an operator QR code, requiring no authenticated session or privileged role — the only gate is `qr_scan::operator::Data::try_parse` matching the magic-action regex: [6](#0-5) 

This is structurally the same defect class as the reported issue: a privileged/state-changing operation (`_deployMarket` in the original report; here, Wi-Fi credential wipe / mirror recalibration overwrite) is executed without validating that the invoking input/parameters are legitimate and authorized, enabling any unprivileged caller to trigger it.

### Impact Explanation
Any person who can present a QR code to the Orb's camera — with no operator badge, backend account, or physical access to the device internals — can:
- Force a Wi-Fi credential wipe (`reset_wifi_credentials`), disconnecting the Orb from its network and requiring an operator to physically re-provision Wi-Fi via another QR code before the Orb can resume normal operation (denial of service/griefing on deployed hardware).
- Force a mirror recalibration reset (`reset_mirror_calibration`), overwriting the stored calibration file and re-running the mirror's homing/calibration sequence, degrading iris/eye-tracking accuracy for subsequent signups until recalibrated, which can affect biometric capture quality relied upon for iris signup integrity.

Both actions are unauthenticated, repeatable griefing vectors against unattended or self-serve-deployed Orbs.

### Likelihood Explanation
High likelihood: the magic QR codes are static, published-format strings (`magic_action:reset_wifi_credentials`, `magic_action:reset_mirror_calibration`) requiring no secret, no signature, and no backend round-trip to be accepted — only camera line-of-sight to a printed/displayed code during the Orb's normal idle-scanning state, which is the Orb's default operating condition when not mid-signup.

### Recommendation
Require backend-verified operator authorization (equivalent to `verify_operator_qr_code`) or at minimum a cryptographically signed/nonce-bound token before executing `MagicResetWifi`/`MagicResetMirror`, and/or rate-limit and log these actions so they cannot be repeatedly triggered by unauthenticated physical presenters.

### Proof of Concept
1. Print or display a QR code containing the text `magic_action:reset_wifi_credentials`.
2. Present it to an idle Orb during its operator QR-code idle scan.
3. `qr_scan::operator::Data::try_parse` matches `MAGIC_QR_CODE`, returning `Data::MagicResetWifi` with no backend check.
4. `handle_magic_operator_qr_code` immediately calls `reset_wifi_and_ensure_network`, wiping the Orb's Wi-Fi configuration — repeatable at will by anyone with a printed code and camera access.

### Citations

**File:** src/plans/qr_scan/operator.rs (L24-61)
```rust
/// Operator QR-code data.
#[derive(Clone, Debug)]
pub enum Data {
    /// Normal Operator QR-code.
    Normal(user::Data),
    /// Action to reconfigure WiFi.
    MagicResetWifi,
    /// Action to reset mirror calibration.
    MagicResetMirror,
}

impl Schema for Data {
    fn ui() -> ui::QrScanSchema {
        ui::QrScanSchema::Operator
    }

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

**File:** src/plans/mod.rs (L749-786)
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
    }
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

**File:** src/network/mod.rs (L102-123)
```rust
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
