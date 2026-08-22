### Title
Magic operator QR codes (`reset_wifi_credentials`, `reset_mirror_calibration`) execute privileged actions before backend operator authorization - (File: src/plans/mod.rs)

### Summary
The Orb's QR-scanning flow validates an operator QR code against the signup backend (`verify_operator_qr_code`) before allowing it to be used for a signup. However, "magic" operator QR codes (`magic_action:reset_wifi_credentials` and `magic_action:reset_mirror_calibration`) are dispatched and executed by `handle_magic_operator_qr_code` *before* this backend authorization step runs, so anyone who can present such a QR code to the Orb's camera can trigger these privileged device-state-changing actions without ever being verified as an authorized operator.

### Finding Description
`Data::try_parse` for the operator QR schema recognizes two "magic" codes that are not normal operator identities: `MagicResetWifi` and `MagicResetMirror` [1](#0-0) .

In the signup flow, both `scan_initial_qr_codes` and `scan_remaining_qr_codes` call `handle_magic_operator_qr_code` immediately after a QR code is scanned, and only call `verify_operator_qr_code` (the backend authorization/validation call) for QR codes that are *not* magic actions: [2](#0-1) [3](#0-2) 

`handle_magic_operator_qr_code` itself performs the privileged action directly, with no authorization check against the backend, and only reports success/failure via the UI: [4](#0-3) 

Compare this to the normal (non-magic) path, where `verify_operator_qr_code` calls `backend::operator_status::request` to confirm the scanned code belongs to a valid, registered operator before any signup-related action proceeds: [5](#0-4) 

This is structurally the same bug class as the reported `MFDBase.claimAndCompound` issue: a function performs a privileged action on behalf of whoever triggered it (`RewardCompounder`/QR scanner) without first confirming that the actor has been authorized to request that action (`toggleAutocompound()` opt-in / backend operator validation). Here, the "opt-in"/authorization check (`verify_operator_qr_code`) is entirely bypassed for the magic-action code path.

### Impact Explanation
Any person able to present a crafted QR code (`magic_action:reset_wifi_credentials` or `magic_action:reset_mirror_calibration`) to the Orb's camera - without being a validated, backend-authorized operator - can:
- Trigger `reset_wifi_and_ensure_network`, which resets the Orb's stored Wi-Fi network configuration/credentials and re-triggers network setup [6](#0-5) .
- Trigger `reset_mirror_calibration`, altering the physical mirror calibration used for iris/face biometric capture [7](#0-6) .

Both are orb-state-changing actions gated, by design, behind operator identity/authorization in the normal flow, but reachable here by an unauthorized party with only a printed QR code, causing denial-of-service (loss of network connectivity) or degraded/incorrect biometric capture until manually recalibrated.

### Likelihood Explanation
Likelihood is high: the QR code strings are simple, static, publicly-guessable text patterns (`magic_action:reset_wifi_credentials`, `magic_action:reset_mirror_calibration`) that require no cryptographic material or backend interaction to construct [8](#0-7) , and the check is entirely bypassed before any authorization occurs.

### Recommendation
Require the same operator-authorization step (`verify_operator_qr_code`/backend validation) to succeed before dispatching magic actions in `handle_magic_operator_qr_code`, or otherwise gate execution of `MagicResetWifi`/`MagicResetMirror` behind a verified-operator check, so unauthorized QR codes cannot trigger privileged device actions.

### Proof of Concept
1. Generate a QR code containing the literal text `magic_action:reset_wifi_credentials`.
2. Present it to the Orb's camera during idle/operator-scan state.
3. Observe `handle_magic_operator_qr_code` is invoked and `reset_wifi_and_ensure_network` executes immediately — `verify_operator_qr_code` (backend authorization) is never called for this code path [4](#0-3) .

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

**File:** src/plans/mod.rs (L762-784)
```rust
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
