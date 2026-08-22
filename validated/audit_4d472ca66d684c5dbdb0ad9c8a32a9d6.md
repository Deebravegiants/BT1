### Title
Unauthenticated `magic_action:reset_wifi_credentials` operator QR-code triggers unauthenticated Wi-Fi/network reset - (File: `src/plans/qr_scan/operator.rs`, `src/plans/mod.rs`, `src/network/mod.rs`)

### Summary
The operator QR-code parser `Data::try_parse` in `src/plans/qr_scan/operator.rs` recognizes a "magic" action pattern `magic_action:(?P<magic_action>[\w]+)` and maps the literal value `reset_wifi_credentials` to `Data::MagicResetWifi` with no signature, HMAC, or backend check. When this QR code is scanned during the operator QR-code scanning step, `handle_magic_operator_qr_code` in `src/plans/mod.rs` immediately calls `reset_wifi_and_ensure_network`, which calls `network::reset()` (`src/network/mod.rs`), spawning `wpa-supplicant-interface restore-default-config` and `reconfigure` as child processes with no authorization gate.

### Finding Description
`Data::try_parse` first attempts to parse the code as a normal user/operator QR code via `user::Data::try_parse`; if that fails, it matches against `MAGIC_QR_CODE` and returns `Data::MagicResetWifi` for the literal string `magic_action:reset_wifi_credentials`: [1](#0-0) 

This QR data type is consumed unconditionally in `handle_magic_operator_qr_code`: for `Data::MagicResetWifi` it directly invokes `self.reset_wifi_and_ensure_network(orb)` with no operator authentication, no backend verification (`verify_operator_qr_code` is only invoked for the `Normal` variant, never for magic actions), and no signature check on the QR content itself: [2](#0-1) 

`reset_wifi_and_ensure_network` then calls `network::reset()` followed by `wifi::Plan.ensure_network_connection`: [3](#0-2) 

`network::reset()` spawns `wpa-supplicant-interface restore-default-config` then `wpa-supplicant-interface reconfigure` as child processes, disconnecting the Orb from its currently configured Wi-Fi network: [4](#0-3) 

The scan path is reachable by an unprivileged bystander. In self-serve mode, `MasterPlan::run` calls `scan_initial_qr_codes` on every loop iteration, which calls `scan_operator_qr_code` → `handle_magic_operator_qr_code` before any button press or credential check, gated only by an operator QR timestamp expiry: [5](#0-4) [6](#0-5) 

In non-self-serve mode, the same `handle_magic_operator_qr_code` call is reached from `scan_remaining_qr_codes` once the button is pressed (a low-friction physical action any bystander at the device can perform, not an authentication mechanism): [7](#0-6) 

No component in this call chain checks that the QR presenter is an authenticated operator; the "operator" QR scan is authenticated by the backend only for `Data::Normal` (via `verify_operator_qr_code`), but the `MagicResetWifi`/`MagicResetMirror` variants bypass that verification entirely and execute directly.

### Impact Explanation
This allows an unprivileged person standing in front of the Orb to force a Wi-Fi/network reset at will, disconnecting the device from its configured network and disrupting availability of the signup/upload pipeline (network connectivity requests, backend calls, biometric data uploads depend on network availability). This is a denial-of-service / unauthenticated privileged-action-execution issue: an action intended for operators (resetting network configuration) is triggered purely by unauthenticated physical presence and QR-code content, invoking OS-level child processes (`wpa-supplicant-interface`) with no authorization gate.

### Likelihood Explanation
Trivial and fully repeatable: no operator credentials, signing keys, or backend interaction are required — printing/displaying the string `magic_action:reset_wifi_credentials` as a QR code and presenting it to the camera during operator QR-code scanning (self-serve idle loop, or after any button press in normal mode) is sufficient. The existing unit test `test_qr_code_variants` in `src/plans/qr_scan/operator.rs` (lines 74-77) already demonstrates that `try_parse` accepts this exact value and produces `Data::MagicResetWifi` without any authentication check.

### Recommendation
Require operator-level authentication/backend verification (similar to `verify_operator_qr_code`) before executing any `MagicResetWifi`/`MagicResetMirror` action, e.g., only accept magic actions embedded within (or signed by) a verified operator QR-code payload, or require an additional operator confirmation step (PIN, backend call, or physical/administrative gesture) before invoking `network::reset()`.

### Proof of Concept
Unit/integration test plan (extending the existing test module in `src/plans/qr_scan/operator.rs` and `src/plans/mod.rs`):
1. Call `qr_scan::operator::Data::try_parse("magic_action:reset_wifi_credentials")` and assert it returns `Some(Data::MagicResetWifi)` (already demonstrated in existing test at lines 74-77).
2. In a `MasterPlan` test harness (as in `src/plans/mod.rs` lines 2169-2281), construct a fake `Orb`, set `operator_qr_code_override` to `Some(Data::MagicResetWifi)`, call `scan_operator_qr_code` then `handle_magic_operator_qr_code`, and assert that `reset_wifi_and_ensure_network`/`network::reset()` is invoked (e.g., via a mock/spy on the `WPA_SUPPLICANT_INTERFACE_BIN` command execution) without any preceding backend `verify_operator_qr_code` call or operator authentication check, confirming the unauthenticated code path.

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

**File:** src/plans/mod.rs (L344-392)
```rust
        let mut initial_qr_codes = QrCodes::None;
        loop {
            self.scan_initial_qr_codes(
                orb,
                &mut initial_qr_codes,
                self_serve,
                operator_qr_expiration_time,
            )
            .await?;
            let Some(qr_codes) = self
                .idle_wait_for_signup_request(
                    orb,
                    &initial_qr_codes,
                    self_serve,
                    self_serve_button,
                    operator_qr_expiration_time,
                )
                .await?
            else {
                continue;
            };

            dd_incr!("main.count.signup.during.general.signup_started");
            self.signup_flag.store(true, Ordering::Relaxed);
            let signup_result = Box::pin(self.do_signup(orb, qr_codes, dbus.as_ref())).await?;
            let success = signup_result.success;
            Box::pin(self.after_signup(orb, signup_result)).await?;
            self.signup_flag.store(false, Ordering::Relaxed);

            orb.disable_image_notary();
            if let Some(r) = orb.orb_relay.as_mut() {
                r.graceful_shutdown(
                    orb_relay_shutdown_wait_for_pending_messages,
                    orb_relay_shutdown_wait_for_shutdown,
                )
                .await;
            }
            orb.orb_relay = None;
            self.reset_hardware_except_led(orb).await?;
            if let Some(dbus_ctx) = dbus.as_ref() {
                dbus::Signup::signup_finished(dbus_ctx, success).await?;
            }

            if self.oneshot || self.has_biometric_input() {
                break Ok(());
            }
            self.ui_idle_delay = Some(time::sleep(Duration::from_secs(10)));
        }
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

**File:** src/plans/mod.rs (L806-835)
```rust
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
