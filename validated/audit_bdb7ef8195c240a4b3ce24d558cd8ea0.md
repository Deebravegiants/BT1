### Title
Unauthenticated "magic" QR-code action bypasses operator authorization to reset Wi-Fi and mirror calibration - (File: src/plans/qr_scan/operator.rs)

### Summary
Behodler's `parameterize` bug allowed any unprivileged actor to mutate a pending proposal's parameters because the function lacked access control tying the mutation to the proposal's creator. The equivalent flaw in `orb-core` is in the operator QR-code parsing/handling path: a QR code matching `magic_action:reset_wifi_credentials` or `magic_action:reset_mirror_calibration` is accepted and *acted upon* by `handle_magic_operator_qr_code` without any backend/operator identity verification — unlike normal operator QR codes, which go through `verify_operator_qr_code` (a backend call validating the operator). Anyone who can present such a QR code to the Orb's camera gains the ability to trigger privileged device-configuration actions.

### Finding Description
Operator QR-code data is parsed by `qr_scan::operator::Data::try_parse` [1](#0-0) . This function first tries to parse the code as a normal operator QR (`user::Data`), and if that fails, matches it against a `MAGIC_QR_CODE` regex that recognizes `magic_action:<name>`, producing `Data::MagicResetWifi` or `Data::MagicResetMirror` [2](#0-1) .

These magic variants are consumed by `handle_magic_operator_qr_code`, which is invoked immediately after scanning, *before* the normal operator-authorization step (`verify_operator_qr_code`, which calls the backend distributor/status endpoint to validate the operator and only then proceeds) is ever reached: [3](#0-2) 

Both `scan_initial_qr_codes` and `scan_remaining_qr_codes` call `handle_magic_operator_qr_code` right after `scan_operator_qr_code`, and only call `verify_operator_qr_code` for the `Normal` branch: [4](#0-3) [5](#0-4) 

For the magic branches, `reset_mirror_calibration` and `reset_wifi_and_ensure_network` are executed unconditionally, with no backend authorization check of any kind: `reset()` erases the current Wi-Fi configuration and forces `wpa_supplicant` to reload defaults [6](#0-5) , and `reset_wifi_and_ensure_network` re-triggers the network setup flow which itself accepts a fresh WiFi QR code without any operator check [7](#0-6) .

This mirrors the Behodler bug class exactly: normal, "authorized" operator QR codes require a backend-validated check (`verify_operator_qr_code`), analogous to going through the DAO's proper `lodgeProposal`/community-vote gate, whereas the "magic" administrative action path (`parameterize`-equivalent) has no access control at all — any camera-visible QR code triggers it.

### Impact Explanation
An unprivileged individual (anyone able to present a QR code to the Orb's camera during idle/operator-scan state — e.g., a bystander, a person queued for signup, or an attacker who prints/displays the magic string) can:
- Force a Wi-Fi credential reset (`network::reset`) and re-trigger the join flow, disconnecting the Orb from its legitimate network and potentially causing it to join an attacker-controlled Wi-Fi network via a subsequently displayed WiFi QR code, enabling a man-in-the-middle position against Orb-to-backend traffic.
- Force a mirror recalibration reset, degrading or corrupting the iris/face capture optical alignment for the operator/user's next legitimate signup, potentially leading to failed or unreliable biometric captures.

Both actions are triggered through the same QR-code channel used for signup, i.e. no privileged access, no operator role check, and no backend authorization is required — a direct "lack of access control" analog to the referenced finding, with concrete device/session-availability impact rather than a purely theoretical one.

### Likelihood Explanation
Likelihood is high: the trigger is a single QR code scan during the normal operator-scanning idle loop that every signup session passes through, requires no credentials, no network access, and no prior state; the magic action strings (`reset_wifi_credentials`, `reset_mirror_calibration`) are static and visible in the shipped source/tests [8](#0-7) , making them trivial to reproduce with any QR generator.

### Recommendation
Require the same backend/operator authorization used for normal operator QR codes (`verify_operator_qr_code`) before executing any magic action, or otherwise cryptographically sign/scope magic QR codes so they can only be issued by an authorized backend/operator and only for a specific Orb, with replay protection (e.g., expiry, nonce). At minimum, gate `handle_magic_operator_qr_code` behind the same operator-identity check as the normal flow before calling `reset_wifi_and_ensure_network` or `reset_mirror_calibration`.

### Proof of Concept
1. Print or display a QR code containing the literal string `magic_action:reset_wifi_credentials`.
2. During the Orb's idle/operator QR-scan loop (`scan_initial_qr_codes` / `scan_remaining_qr_codes`), present this QR code to the camera.
3. `qr_scan::operator::Data::try_parse` matches it to `Data::MagicResetWifi` (confirmed by the existing unit test `test_qr_code_variants`) [9](#0-8) .
4. `handle_magic_operator_qr_code` immediately calls `reset_wifi_and_ensure_network`, wiping the Wi-Fi configuration with no backend/operator validation [10](#0-9) .
5. Repeat with `magic_action:reset_mirror_calibration` to force a mirror recalibration reset with the same lack of authorization.

### Citations

**File:** src/plans/qr_scan/operator.rs (L11-33)
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
