### Title
Unauthenticated "magic" operator QR-codes let anyone trigger privileged Wi-Fi/mirror-calibration resets - (File: src/plans/mod.rs, src/plans/qr_scan/operator.rs)

### Summary
The operator QR-code scanning path recognizes special "magic" QR-codes (`magic_action:reset_wifi_credentials`, `magic_action:reset_mirror_calibration`) and executes privileged device actions (Wi-Fi credential reset and mirror-recalibration reset) immediately upon scan, with no verification that the scanning party is an authorized operator. This mirrors the reported bug class: a state-changing action (`RollerPeriphery.approve()`) reachable by any caller with no access control gate.

### Finding Description
`qr_scan::operator::Data::try_parse` matches any scanned code against a fixed, public regex `magic_action:(reset_wifi_credentials|reset_mirror_calibration)` and returns `Data::MagicResetWifi` / `Data::MagicResetMirror` without any cryptographic signature, operator-authenticated context, or backend round-trip. [1](#0-0) 

These magic variants are handled by `handle_magic_operator_qr_code`, which is called directly from the QR-scanning loop (`scan_initial_qr_codes`/`scan_remaining_qr_codes`) *before* `verify_operator_qr_code` is ever invoked — i.e. the normal operator-authorization backend check (`backend::operator_status::request`) is entirely bypassed for magic codes: [2](#0-1) [3](#0-2) 

The privileged actions themselves reset Wi-Fi network state and reset/re-run mirror calibration outright: [4](#0-3) 

Unlike the "Normal" operator QR-code branch, which is subsequently validated against `backend::operator_status::request` for a `valid == true` status before any signup proceeds, the magic-action branch performs the state-changing operation and returns `None` — no backend validation gate exists on this path at all.

### Impact Explanation
Any unprivileged party who can present a printed/displayed QR-code containing the fixed, publicly-known string `magic_action:reset_wifi_credentials` or `magic_action:reset_mirror_calibration` to the orb's camera can force it to reset its Wi-Fi credentials (disconnecting it from its configured network, requiring re-provisioning via a new hotspot QR-code) or reset/re-trigger mirror calibration, without holding operator credentials or any authorization token. This is a state-changing / denial-of-service impact on the device's operational availability and calibration integrity, directly analogous to the unauthorized `approve()` call in the original report where an unprivileged caller can invoke a privileged, unguarded function.

### Likelihood Explanation
Likelihood is high: the trigger strings are public (they even appear in the repo's own unit tests), require no secret, no signature, and no network/backend interaction to be accepted — merely displaying the QR-code to the orb's camera during the operator-scan phase of any signup flow is sufficient. [5](#0-4) 

### Recommendation
Require operator authentication/authorization for magic-action QR-codes just as is required for normal operator QR-codes (e.g., route magic actions through `verify_operator_qr_code`/backend validation, or require a signed/keyed magic-action payload) before executing `reset_mirror_calibration` or `reset_wifi_and_ensure_network`.

### Proof of Concept
1. Generate a QR-code encoding the literal string `magic_action:reset_wifi_credentials` (or `magic_action:reset_mirror_calibration`).
2. During the operator QR-code scanning phase of any signup session, present this QR-code to the orb's camera.
3. `Data::try_parse` matches the magic regex and returns `Data::MagicResetWifi`/`Data::MagicResetMirror`.
4. `handle_magic_operator_qr_code` executes `reset_wifi_and_ensure_network` (or `reset_mirror_calibration`) immediately, with no operator-status backend check, causing the orb to drop its Wi-Fi connection or perform an unrequested mirror recalibration. [6](#0-5)

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

**File:** src/plans/qr_scan/operator.rs (L68-90)
```rust
    #[test]
    fn test_qr_code_variants() {
        {
            let code = "userid:66ad4897-0ca7-4727-8365-ca808348e3cd:1";
            assert!(matches!(Data::try_parse(code), Some(Data::Normal(_))));
        }
        {
            let code = "magic_action:reset_wifi_credentials";
            assert!(matches!(Data::try_parse(code), Some(Data::MagicResetWifi)));
        }
        {
            let code = "magic_action:reset_mirror_calibration";
            assert!(matches!(Data::try_parse(code), Some(Data::MagicResetMirror)));
        }
        {
            let code = "magic_action:burn_and_destroy_everything";
            assert!(Data::try_parse(code).is_none());
        }
        {
            let code = "random_text";
            assert!(Data::try_parse(code).is_none());
        }
    }
```

**File:** src/plans/mod.rs (L731-747)
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
