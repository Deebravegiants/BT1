### Title
Unauthenticated "magic" QR-codes let anyone reset WiFi credentials or mirror calibration before operator verification - ([File: src/plans/mod.rs])

### Summary
`handle_magic_operator_qr_code` executes privileged, disruptive device-reset actions (`reset_wifi_and_ensure_network`, `reset_mirror_calibration`) as soon as a QR-code matching the `magic_action:` pattern is scanned by the camera, and this happens *before* `verify_operator_qr_code` runs. Since no backend authorization or operator-identity check gates these actions, any person able to present a QR code to the orb's camera (i.e., an unprivileged bystander, not a verified operator) can trigger them, repeatedly disrupting signup availability — the same bug class as the reported `checkTransaction`-DoS: an unauthenticated party can invoke a function that mutates security/operational-relevant state and blocks normal operation.

### Finding Description
The signup state machine scans an operator QR code and immediately branches on whether it is a "magic" QR code: [1](#0-0) 

`Data::try_parse` in the operator QR-code schema recognizes two magic actions from an unauthenticated regex match on the raw scanned text, with no cryptographic or backend verification: [2](#0-1) 

Crucially, `handle_magic_operator_qr_code` is invoked in `scan_initial_qr_codes` and `scan_remaining_qr_codes` *before* `verify_operator_qr_code` (which is the only step that performs backend/operator authentication): [3](#0-2) [4](#0-3) 

So the magic-action branch executes its side effect (`reset_mirror_calibration` or `reset_wifi_and_ensure_network`) unconditionally, and only afterward does the loop `continue`; there is no code path that subjects a magic QR code to `verify_operator_qr_code` or any other authorization check. `reset_wifi_and_ensure_network` actually tears down and reconfigures the wpa_supplicant network state: [5](#0-4) [6](#0-5) 

and `reset_mirror_calibration` disables/re-enables and recalibrates the physical mirror used for iris/face targeting during biometric capture: [7](#0-6) 

This mirrors the analog bug class in the report: a state-mutating "guard-adjacent" action (there, resetting a cooldown timestamp; here, resetting network/mirror state) is reachable without any authorization check that the rest of the flow otherwise enforces (`verify_operator_qr_code`).

### Impact Explanation
Any unprivileged person within camera view of the orb — not necessarily a verified operator or a signup participant — can present a piece of paper/QR code with the text `magic_action:reset_wifi_credentials` or `magic_action:reset_mirror_calibration` and force the device to:
- Drop and reconfigure its WiFi connection (`network::reset` → `wpa-supplicant-interface restore-default-config` + `reconfigure`), interrupting connectivity needed for QR verification, biometric-pipeline backend calls, and signup enrollment uploads.
- Force a mirror recalibration cycle, disrupting or degrading iris/face capture positioning during any concurrent or subsequent signup attempt.

Repeated presentation of such a code can be used to continuously interrupt the orb's operation, denying service to legitimate operators/users attempting to complete a signup — a denial-of-service on the device's core signup functionality, analogous in class (unauthenticated reset of operational state blocking normal flow) to the reported `checkTransaction` cooldown-reset DoS.

### Likelihood Explanation
High feasibility: the attacker requires only physical line-of-sight to the orb's camera (no credentials, no network access, no privileged role) and knowledge of the fixed, publicly-derivable regex pattern `magic_action:(reset_wifi_credentials|reset_mirror_calibration)`, which is present in the open-source `qr_scan/operator.rs` module and its unit tests. No rate limiting or authorization gate exists on this path.

### Recommendation
Require the magic QR-code actions to pass through the same authorization/verification step (`verify_operator_qr_code`, or an equivalent backend-authenticated operator check) before executing `reset_mirror_calibration` or `reset_wifi_and_ensure_network`. Alternatively, restrict recognition of magic QR codes to a mode/context that already establishes operator trust (e.g., only after a successful operator QR verification), and consider adding rate limiting to these reset actions.

### Proof of Concept
1. Generate a QR code encoding the literal string `magic_action:reset_wifi_credentials` (or `magic_action:reset_mirror_calibration`), matching the regex in `src/plans/qr_scan/operator.rs` (`MAGIC_QR_CODE`).
2. Present this QR code to the orb's camera at any point during `scan_initial_qr_codes`/`scan_remaining_qr_codes` (i.e., during normal idle/operator-scan phases), with no operator credentials and no prior authentication.
3. Observe that `handle_magic_operator_qr_code` matches `Data::MagicResetWifi` / `Data::MagicResetMirror` and unconditionally calls `reset_wifi_and_ensure_network` / `reset_mirror_calibration`, executing before any call to `verify_operator_qr_code`.
4. Repeat presenting the QR code to continuously disrupt WiFi connectivity or force repeated mirror recalibration, denying service to legitimate signup attempts.

Note: I was not able to fully verify from the indexed code whether any additional runtime gating (e.g., UI state, physical camera FOV constraints, or an operator-presence precondition enforced elsewhere in `brokers::Orb`) exists that might restrict when this scan loop is reachable; the plan logic itself shows no authorization check on the magic-action branch.

### Citations

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

**File:** src/plans/qr_scan/operator.rs (L35-62)
```rust
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
}
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
