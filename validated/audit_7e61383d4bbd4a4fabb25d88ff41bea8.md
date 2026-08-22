This confirms the vulnerability. I have enough evidence to write the finding.

### Title
Missing operator authorization check on "magic" QR-code actions allows unauthenticated WiFi/Mirror reset (DDoS) - (File: `src/plans/qr_scan/operator.rs`, `src/plans/mod.rs`, `src/network/mod.rs`)

### Summary
The orb's operator QR-code scanning flow recognizes special "magic" QR codes (`magic_action:reset_wifi_credentials` and `magic_action:reset_mirror_calibration`) and executes privileged, state-changing device actions (WiFi credential wipe, mirror recalibration reset) as soon as the code is *parsed*, before the orb performs its backend authorization check that normally validates that a scanned QR code belongs to a legitimate operator. This is directly analogous to the reported `setBridge()` issue: a critical setter/state-mutating action is reachable without any permission check, and can be abused for a denial-of-service (DDoS-like) attack against the orb.

### Finding Description
Operator QR-codes are represented by `qr_scan::operator::Data`, which is parsed purely syntactically via regex, with no cryptographic signature or backend authorization performed at parse time: [1](#0-0) 

If the scanned text matches `magic_action:reset_wifi_credentials` or `magic_action:reset_mirror_calibration`, `try_parse` returns `Data::MagicResetWifi` / `Data::MagicResetMirror` — no signature, HMAC, or backend call is required, unlike the "normal" operator QR-code path which is later validated against the backend in `verify_operator_qr_code`.

In `MasterPlan`, the scanned operator QR-code is first fed to `handle_magic_operator_qr_code`, which — for magic codes — immediately executes the privileged action (`reset_wifi_and_ensure_network` or `reset_mirror_calibration`) and returns `None` (aborting the loop), all *before* `verify_operator_qr_code` (the backend authorization check) is ever called: [2](#0-1) 

This function is invoked in both the initial self-serve QR scan path and the normal (button-press) QR scan path, in each case strictly prior to the operator authorization call `verify_operator_qr_code`: [3](#0-2) [4](#0-3) 

The magic-reset-WiFi action calls `network::reset()`, which shells out to the privileged `wpa-supplicant-interface` binary to overwrite the WiFi configuration with the default config and force `wpa_supplicant` to reload it, disconnecting the orb from its current network: [5](#0-4) 

The magic-reset-mirror action calls `reset_mirror_calibration`, which rewrites the calibration file on disk and forces the orb to redo mirror calibration: [6](#0-5) 

The root cause is that the "magic" QR-code branch bypasses the authorization check (`verify_operator_qr_code`) that is applied to every other operator QR-code, meaning **any person able to present a QR code to the orb's camera** — with no special privilege, credential, or backend-issued token — can trigger these privileged device-state mutations. This is the same bug class as the reported `setBridge()` finding: a state-mutating entry point lacking the permission check that gates equivalent/adjacent functionality.

### Impact Explanation
- **Denial of Service**: Presenting a `magic_action:reset_wifi_credentials` QR code to any orb wipes its WiFi credentials and disconnects it from the network, requiring re-provisioning via the WiFi setup QR flow before the orb can process any signups again — an unauthenticated, repeatable DDoS against the device, matching exactly the impact called out in the original report ("could be used for DDoS attacks").
- Presenting `magic_action:reset_mirror_calibration` forces the orb to lose its calibration and re-run mirror recalibration, disrupting/blocking biometric signups until recalibration completes, which is also a service-availability impact.
- Both actions can be repeated indefinitely by anyone with physical access to the orb's camera (no operator badge, backend token, or signature needed), since the QR-code content is public/guessable ("magic_action:reset_wifi_credentials" is a fixed, unauthenticated string).

### Likelihood Explanation
High. No secrets, cryptographic material, or backend validation are required — an attacker only needs to print/display the two fixed magic strings as a QR code and show them to the orb's RGB camera during the operator-QR-scan phase (available in both self-serve and normal signup flows).

### Recommendation
Move the authorization check ahead of the magic-action dispatch: call `verify_operator_qr_code` (or an equivalent backend/operator authentication check) before executing `MagicResetWifi`/`MagicResetMirror` actions, or otherwise require a signed/authenticated payload for magic QR-codes so that only verified operators can trigger WiFi and mirror-calibration resets.

### Proof of Concept
1. Generate a QR code encoding the literal string `magic_action:reset_wifi_credentials`.
2. Trigger an operator QR-code scan on the orb (start a signup, or wait for the self-serve idle scan) and present the QR code to the camera.
3. `qr_scan::operator::Data::try_parse` matches the `MAGIC_QR_CODE` regex and returns `Data::MagicResetWifi` with no backend validation.
4. `handle_magic_operator_qr_code` immediately calls `reset_wifi_and_ensure_network`, which invokes `network::reset()`, wiping the orb's WiFi configuration and disconnecting it — before `verify_operator_qr_code` is ever reached.
5. Repeat with `magic_action:reset_mirror_calibration` to force mirror recalibration at will, disrupting signup availability.

### Citations

**File:** src/plans/qr_scan/operator.rs (L11-61)
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

**File:** src/plans/mod.rs (L761-774)
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
