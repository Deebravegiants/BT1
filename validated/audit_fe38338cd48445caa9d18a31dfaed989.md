### Title
Unauthenticated Magic QR-Code Bypasses Operator Authorization to Trigger Wi-Fi Reset and Mirror Recalibration - ([File: src/plans/mod.rs])

### Summary
The Orb's operator QR-code handling flow parses and immediately executes "magic" administrative actions (`reset_wifi_credentials`, `reset_mirror_calibration`) *before* the operator identity is validated against the backend. Any unprivileged individual who can present a QR code to the Orb's camera — without ever being an authenticated/registered operator — can trigger privileged hardware state changes, most notably forcing the Orb off its trusted Wi-Fi network and re-prompting for a new network via WiFi QR code (MECARD), enabling a follow-on man-in-the-middle attack.

### Finding Description
`qr_scan::operator::Data::try_parse` in [1](#0-0)  parses any scanned code matching `magic_action:<action>` into `Data::MagicResetWifi` or `Data::MagicResetMirror` with no signature, credential, or backend check whatsoever — unlike the `Normal(user::Data)` variant, which still requires validation.

In the signup flow (`src/plans/mod.rs`), the order of operations is:
1. `scan_operator_qr_code` — purely scans the camera for a QR code, returning the parsed `qr_scan::operator::Data`.
2. `handle_magic_operator_qr_code` — dispatches on the variant. If it is `MagicResetMirror` or `MagicResetWifi`, the privileged action is executed **immediately**, and the function returns `None` so the loop simply retries scanning: [2](#0-1) 
3. Only if the variant is `Normal` does the code proceed to `verify_operator_qr_code`, which performs the actual backend authorization check via `backend::operator_status::request` (validating the operator ID against the backend and confirming it's a legitimate registered operator): [3](#0-2) 

This ordering is used consistently in both `scan_initial_qr_codes` and `scan_remaining_qr_codes`: [4](#0-3) [5](#0-4) 

The root cause is that the "magic" action branch of `handle_magic_operator_qr_code` never routes through `verify_operator_qr_code`/`operator_status::request` — the one function that actually checks operator authorization against the backend (analogous to the missing ownership/authorization check that let the DYAD `deposit()` function be called by any caller instead of only the dNFT owner). Anyone capable of printing/presenting an arbitrary QR code to the Orb's camera can invoke these actions; no operator badge, backend token, or prior pairing is required.

The `MagicResetWifi` action calls `reset_wifi_and_ensure_network`, which resets the current Wi-Fi state and immediately re-enters the Wi-Fi QR/MECARD scanning flow, waiting for a new network's credentials from the next scanned QR code: [6](#0-5) [7](#0-6) 
which parses the next QR-code using the MECARD `Credentials::parse` in [8](#0-7)  and joins that network via `network::join`.

### Impact Explanation
An unprivileged attacker with no relationship to a legitimate operator or backend credentials can:
1. Present a `magic_action:reset_wifi_credentials` QR code to force the Orb to disconnect from its currently configured (presumably trusted) Wi-Fi network.
2. Immediately follow up with an attacker-controlled `WIFI:...` MECARD QR code, causing the Orb to join an attacker-controlled network.
3. From that network position, intercept, delay, or tamper with the Orb's backend HTTP traffic used for signup validation, biometric image/PCP uploads, and operator/user QR-code verification requests — since those requests traverse the network the attacker now controls.

Additionally, `magic_action:reset_mirror_calibration` can be used to repeatedly force mirror recalibration, disrupting Orb availability/denial-of-service against legitimate operators performing signups, entirely without authorization.

This directly parallels the reported bug class: a state-mutating action reachable by an unauthorized party due to a missing ownership/authorization check, enabling denial of legitimate use and setting up follow-on attacks (network MITM) against the signup and biometric upload pipeline.

### Likelihood Explanation
Likelihood is high: the `magic_action:` QR format is a fixed, publicly-derivable string (`magic_action:reset_wifi_credentials`, `magic_action:reset_mirror_calibration`, confirmed by the unit tests in [9](#0-8) ), requiring no secret knowledge, no operator registration, and no backend interaction to construct or use. Any bystander with a printed QR code and physical proximity to the Orb's camera can trigger it.

### Recommendation
Route the `MagicResetWifi`/`MagicResetMirror` branches through the same backend operator authorization check (`verify_operator_qr_code`) that `Normal` operator QR-codes require, so that magic administrative actions can only be triggered by a verified/authenticated operator, mirroring the fix of enforcing an ownership/ authorization check before allowing a privileged, state-mutating action.

### Proof of Concept
1. Print a QR code containing the string `magic_action:reset_wifi_credentials`.
2. Present it to the Orb camera during idle/operator-QR-scanning state — `handle_magic_operator_qr_code` executes `reset_wifi_and_ensure_network` with no authorization check (see `src/plans/mod.rs:978-1009` and `src/plans/mod.rs:741-747`).
3. Immediately present a second QR code in MECARD Wi-Fi format (`WIFI:T:WPA;S:attacker-ap;P:password;;`) pointing to an attacker-controlled access point — parsed by `network::mecard::Credentials::parse` and joined via `network::join` in `src/plans/wifi/mod.rs:17-73`.
4. The Orb is now connected to the attacker's network, from which subsequent backend HTTP(S) traffic can be intercepted/manipulated.

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

**File:** src/plans/qr_scan/operator.rs (L64-90)
```rust
#[cfg(test)]
mod tests {
    use super::*;

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

**File:** src/network/mecard.rs (L77-127)
```rust
impl Credentials {
    /// Parses WiFi credentials encoded in MECARD format.
    pub fn parse(input: &str) -> IResult<&str, Self> {
        let (mut input, _) = tag("WIFI:")(input)?;

        // Parses a set of fields with the following requirements:
        // 1. A field is parsed no more than once.
        // 2. Fields are parsed in arbitrary order.
        // 3. Each field is optional.
        macro_rules! parse_fields {
            ($($parse:path => $opt:ident,)*) => {
                $(let mut $opt = None;)*
                loop {
                    $(
                        if $opt.is_none() {
                            if let Ok((next_input, parsed)) = $parse(input) {
                                $opt = Some(parsed);
                                input = next_input;
                                continue;
                            }
                        }
                    )*
                    break;
                }
            };
        }
        parse_fields! {
            AuthType::parse => auth_type,
            parse_ssid => ssid,
            parse_password => password,
            parse_hidden => hidden,
        }

        let ssid = ssid.filter(|ssid| !ssid.is_empty());
        let (password, auth_type) = password
            .filter(|pwd| !pwd.is_empty())
            .map_or((None, Some(AuthType::Nopass)), |pwd| (Some(Password(pwd)), auth_type));

        // ssid is actually not optional.
        if ssid.is_none() {
            let (_, ()) = fail(input)?;
        }

        let (input, _) = tag(";")(input)?;
        let (input, _) = eof(input)?;

        let auth_type = auth_type.unwrap_or_default();
        let ssid = ssid.unwrap_or_default();
        let hidden = hidden.unwrap_or_default();
        Ok((input, Self { auth_type, ssid, password, hidden }))
    }
```
