### Title
Unauthenticated "Magic QR Code" Allows Any Unprivileged Person to Trigger Privileged Orb Actions (WiFi Credential Reset / Network Rejoin) - ([File: src/plans/qr_scan/operator.rs])

### Summary
Similar to the Lybra bug class — where an incidental, non-explicit condition (a non-zero allowance) was treated by the code as implicit authorization for *any* party to act on behalf of another, enabling a party who never gave deliberate consent to be exploited — orb-core's operator QR-code scanning path treats a bare pattern match on scanned text (`magic_action:reset_wifi_credentials` / `magic_action:reset_mirror_calibration`) as sufficient authorization to execute privileged device actions, with **no backend authentication and no distinction between an authorized operator and any bystander holding up a piece of paper**.

### Finding Description
The operator QR-code schema parser recognizes two "magic" actions purely from an unauthenticated regex match against locally scanned text: [1](#0-0) 

Unlike a `Normal` operator QR-code, which must additionally pass a backend authorization check via `verify_operator_qr_code` (`backend::operator_status::request`) before being trusted, the `MagicResetWifi` / `MagicResetMirror` variants are dispatched and executed immediately in `handle_magic_operator_qr_code` — entirely bypassing `verify_operator_qr_code`: [2](#0-1) 

This function is reached directly from the operator QR scanning loop, both during the general signup flow and the self-serve initial QR scan loop, before any backend validation occurs: [3](#0-2) 

The two actions it can trigger without any authorization are:
- `reset_mirror_calibration`, which overwrites the mirror calibration with defaults and re-applies it live: [4](#0-3) 
- `reset_wifi_and_ensure_network`, which wipes the current WiFi configuration (`network::reset()` restores the default `wpa_supplicant.conf` and forces disconnect/reconfigure) and then re-enters the WiFi-provisioning flow, prompting for a *new* WiFi hotspot QR code to join: [5](#0-4) [6](#0-5) 

Once the WiFi is reset, `ensure_network_connection` immediately begins scanning for a *new* WiFi MECARD QR code and will join whatever network credentials it captures: [7](#0-6) 

This closely mirrors the report's bug class: the system conflates an incidental, unauthenticated signal ("this text matches a magic-action regex" ≈ "this address has non-zero allowance") with deliberate, verified authorization from the legitimate privileged party (the operator), letting any unprivileged actor who can present a QR code to the camera invoke a privileged capability meant only for operators.

### Impact Explanation
An unprivileged bystander (any person able to display a QR code to the orb's camera during the idle/operator-scan phase — which is the normal, publicly-facing phase of self-serve operation) can:
1. Force the orb to disconnect from its legitimate, backend-connected WiFi network and enter WiFi-provisioning mode by showing a `magic_action:reset_wifi_credentials` QR code, causing a denial of service (the orb will stop signups until it rejoins a network).
2. Immediately follow up by presenting a WiFi MECARD QR code of an attacker-controlled access point, which the orb will join automatically (per `ensure_network_connection`), giving the attacker the ability to man-in-the-middle all orb network traffic to the backend — a much stronger foothold than the wifi/DoS effect alone. Traffic tampered with in this position could feed spoofed identity/authorization responses back into the signup pipeline (e.g. `backend::user_status`, `backend::operator_status`), enabling unauthorized/misattributed signup flows or exposing sensitive requests.
3. Reset mirror calibration remotely, degrading iris/face capture quality for subsequent legitimate signups (integrity/availability impact on the biometric capture pipeline).

This maps to the "unauthorized... signup" / "identity binding" impact categories in scope, since regaining a MITM position on the orb's network path undermines the trust boundary between the orb and the backend that the rest of the signup-authorization logic (`verify_operator_qr_code`, `backend::user_status::request`) depends on.

### Likelihood Explanation
Likelihood is high for physically-present attackers: the magic QR codes are plain, unsigned text strings (`magic_action:reset_wifi_credentials`, `magic_action:reset_mirror_calibration`) that can be trivially generated and printed by anyone — no cryptographic material, backend session, or operator credential is required, and the code path is reached by simply presenting the QR-code to the camera during the "Operator QR-code scanning" phase, which occurs before any backend authentication in both the standard signup flow (`scan_remaining_qr_codes`) and the self-serve idle loop (`scan_initial_qr_codes`).

### Recommendation
Require the same backend authorization step (`verify_operator_qr_code` / equivalent operator-authentication check) for magic-action QR codes as for normal operator QR codes before executing privileged actions, or better, require a signed/backend-issued token embedded in the magic QR code that ties the action to a specific authenticated operator session. At minimum, rate-limit and log magic-action invocations, and disallow WiFi-network changes from an unauthenticated scan without a secondary explicit operator confirmation (e.g., PIN entry or backend-issued one-time code) to close the DoS/MITM vector.

### Proof of Concept
1. Print/display a QR code encoding the literal text `magic_action:reset_wifi_credentials`.
2. During the orb's idle/operator-QR-scanning phase (reachable by any passerby in self-serve deployments, per `scan_initial_qr_codes`), present the QR code to the orb's camera.
3. `qr_scan::operator::Data::try_parse` matches the `MAGIC_QR_CODE` regex and returns `Data::MagicResetWifi` with no backend call.
4. `handle_magic_operator_qr_code` dispatches directly to `reset_wifi_and_ensure_network`, which calls `network::reset()` (wiping WiFi config) and then `wifi::Plan::ensure_network_connection`, which begins scanning for a new WiFi MECARD QR code.
5. Present a second QR code encoding attacker-controlled WiFi credentials (`WIFI:T:WPA;S:evil-ap;P:password;;`); the orb joins the attacker's network via `network::join`, placing all subsequent orb↔backend traffic under attacker control.

*Note: I was unable to fully confirm from the indexed code whether this "Operator QR-code scanning" phase is exposed to unauthenticated bystanders in every deployment mode (e.g., whether physical operator presence/supervision is otherwise enforced in non-self-serve deployments), since UI/deployment-context details beyond the source shown here were not available in the index. This should be verified in a full checkout of the repository.*

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

**File:** src/plans/wifi/mod.rs (L17-73)
```rust
impl Plan {
    /// Checks whether connected to a WiFi network, if not connected scan the
    /// hotspot QR code.
    pub async fn ensure_network_connection(&self, orb: &mut Orb) -> Result<()> {
        let mut in_progress_start = Instant::now();
        let mut has_requested_qr_code = false;
        let success = |orb: &mut Orb, has_requested_qr_code| {
            if has_requested_qr_code {
                orb.ui.network_connection_success();
            }
            tracing::debug!("Network is connected");
            Ok::<(), Error>(())
        };
        loop {
            match network::status().await? {
                network::Status::Connected { has_internet: true } => {
                    success(orb, has_requested_qr_code)?;
                    break;
                }
                network::Status::InProgress
                | network::Status::Connected { has_internet: false }
                    if in_progress_start.elapsed() < NETWORK_CONNECTION_TIMEOUT =>
                {
                    tracing::debug!("Network connection in progress");
                    sleep(Duration::from_millis(250)).await;
                }
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
                }
            }
        }
        Ok(())
    }
```
