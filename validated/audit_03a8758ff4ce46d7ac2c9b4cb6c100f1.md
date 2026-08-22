### Title
Unauthenticated "magic" operator QR codes trigger privileged device actions (WiFi reset, mirror recalibration) before any operator verification - (File: `src/plans/qr_scan/operator.rs`, `src/plans/mod.rs`)

### Summary
The Orb's operator QR-code scanning flow recognizes special "magic" QR codes (`magic_action:reset_wifi_credentials`, `magic_action:reset_mirror_calibration`) and executes the corresponding privileged action immediately upon scan, before the operator identity encoded in a QR code is ever validated against the backend. Any person able to present a QR code to the Orb's camera — not just an authorized operator — can trigger these state-changing actions.

### Finding Description
`qr_scan::operator::Data::try_parse` parses raw QR code text and, if it doesn't match the normal user/operator QR schema, matches it against a `magic_action:<name>` regex, returning `Data::MagicResetWifi` or `Data::MagicResetMirror` for two whitelisted actions: [1](#0-0) 

This value is fed into `handle_magic_operator_qr_code`, which unconditionally executes `reset_mirror_calibration` or `reset_wifi_and_ensure_network` for the respective magic action: [2](#0-1) 

Critically, in both the initial QR scan loop and the repeat QR scan loop, `handle_magic_operator_qr_code` is invoked directly after `scan_operator_qr_code`, and only *after* it returns (for the non-magic/"Normal" case) does the code call `verify_operator_qr_code`, which is what actually checks the scanned QR-code's operator ID against the backend: [3](#0-2) [4](#0-3) 

So the magic actions (`MagicResetMirror`, `MagicResetWifi`) are dispatched and executed with zero authentication — they never reach `verify_operator_qr_code`. Unlike the "Normal" operator QR-code path, whose value must still pass backend validation before a signup session can proceed, the magic-action path performs the privileged action as a side effect of merely parsing the string.

This closely mirrors the referenced report's bug class: an entry point (QR-code scan, analogous to the "swap" calldata submission) grants powerful, state-mutating capability to an untrusted input source with no guarantee that the entity presenting the input has any authorization, and no additional validation of the "target"/"action" beyond a simple string match.

### Impact Explanation
An unprivileged individual with physical proximity to the Orb (the same population that can scan a "normal" user/operator QR code) can print or display a `magic_action:reset_wifi_credentials` or `magic_action:reset_mirror_calibration` QR code and force the device to:
- Drop its network connection and re-enter WiFi provisioning (`network::reset()` + `wifi::Plan.ensure_network_connection`), creating a denial-of-service / operational disruption, and opening a window during which the attacker could attempt to have the Orb join an attacker-controlled WiFi network via a subsequent WiFi-credentials QR code (`Plan::ensure_network_connection` accepts any scanned WiFi MECARD QR code once disconnected).
- Reset and re-run mirror calibration, degrading imaging/eye-tracking accuracy for subsequent signups until recalibrated, causing capture failures or operational downtime.

Both are reachable without any operator credential or backend check, purely by controlling the string shown to the QR scanner.

### Likelihood Explanation
High. The trigger requires only printing two fixed, publicly-derivable magic strings as a QR code and holding it up to the Orb's camera during the operator QR-code scanning phase — no special access, credentials, or insider knowledge beyond the fixed action names, which are hardcoded and discoverable by inspecting the parsed enum/regex.

### Recommendation
Perform operator/backend authorization before executing magic actions, or require the magic QR code itself to be signed/validated (e.g., only accept it embedded within an otherwise-verified operator QR-code payload, or require it to be confirmed against the backend / require a second factor). At minimum, move `handle_magic_operator_qr_code` execution to occur only after `verify_operator_qr_code` succeeds for an authenticated operator, ensuring untrusted scans cannot mutate device network or calibration state.

### Proof of Concept
1. Generate a QR code containing the literal text `magic_action:reset_wifi_credentials` (or `magic_action:reset_mirror_calibration`).
2. During the Orb's operator QR-code scanning phase (e.g. `scan_initial_qr_codes`/`scan_remaining_qr_codes` in `src/plans/mod.rs`), present the QR code to the camera.
3. Observe that `qr_scan::operator::Data::try_parse` returns `Data::MagicResetWifi`/`Data::MagicResetMirror` [5](#0-4)  and `handle_magic_operator_qr_code` immediately performs `reset_wifi_and_ensure_network`/`reset_mirror_calibration` [6](#0-5)  without any prior call to `verify_operator_qr_code`.

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

**File:** src/plans/mod.rs (L761-784)
```rust
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

**File:** src/plans/mod.rs (L978-1008)
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
```
