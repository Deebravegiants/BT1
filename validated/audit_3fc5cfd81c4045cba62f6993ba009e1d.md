I have enough evidence to write the finding now.

### Title
Unauthenticated "magic" QR codes let anyone reset mirror calibration or WiFi/network configuration without operator verification - (File: src/plans/mod.rs, src/plans/qr_scan/operator.rs)

### Summary
The `MagicResetMirror` and `MagicResetWifi` "magic QR-code" actions are executed as soon as a QR-code matching the pattern `magic_action:<action>` is scanned by the orb's camera, *before* the code is verified against the backend as belonging to a registered/authorized operator. Any person able to present such a QR code to the orb can trigger these privileged reconfiguration actions, analogous to the reported `FeeProvider` issue where sensitive setters lacked access control and could be invoked by any caller.

### Finding Description
`qr_scan::operator::Data::try_parse` parses any string of the form `magic_action:reset_wifi_credentials` or `magic_action:reset_mirror_calibration` into `Data::MagicResetWifi` / `Data::MagicResetMirror`, with no cryptographic signature or backend authorization check involved in the parsing step itself: [1](#0-0) 

In both `scan_initial_qr_codes` and `scan_remaining_qr_codes` (the two entry points that process a freshly scanned operator QR code during the signup flow), `handle_magic_operator_qr_code` is invoked immediately after the raw QR string is parsed, and *before* `verify_operator_qr_code`, which is the function that actually calls the backend (`backend::operator_status::request`) to confirm the QR code belongs to a valid, registered operator: [2](#0-1) [3](#0-2) 

`handle_magic_operator_qr_code` directly executes the privileged action for the two magic variants and returns `Ok(None)`, short-circuiting the loop before `verify_operator_qr_code` is ever reached for that code: [4](#0-3) 

The two privileged operations performed are:
- `reset_mirror_calibration`, which overwrites the on-disk mirror calibration file (`CALIBRATION_FILE_PATH`) with the default calibration and re-applies it to the mirror actuator hardware: [5](#0-4) 
- `reset_wifi_and_ensure_network`, which resets network state and forces the orb into a Wi-Fi (re)configuration flow: [6](#0-5) 

This is the same class of issue as the external report: a state-changing/administrative operation (`setFeesCollectionAddress`/`setLoanOriginationFeePercentage` analog) that is reachable and executable by any unprivileged caller — here, anyone who can show a QR code to the orb's camera — with no check that the caller is an authenticated operator, mirroring the missing access-control pattern.

### Impact Explanation
An unauthenticated party (any bystander, not an authorized operator) who can present a crafted QR code to an orb can:
- Force a mirror-calibration reset, silently overwriting the currently calibrated (potentially field-recalibrated) `calibration.json` with hardware defaults and immediately applying it to the actuator. Since the mirror steers the IR camera onto the user's eyes during biometric capture, repeated forced miscalibration is a low-effort denial-of-service against signup availability and could degrade capture quality feeding into liveness/fraud checks.
- Force a network/Wi-Fi reset (`network::reset`) at will, which is a denial-of-service vector against the orb's connectivity and disrupts the signup flow (which depends on backend calls for operator/user QR validation).

Both actions bypass the intended trust boundary that only a verified operator (one whose QR has been confirmed valid by the backend via `verify_operator_qr_code`/`backend::operator_status::request`) should be able to perform maintenance actions on the device.

### Likelihood Explanation
Likelihood is high: the QR string format is public knowledge (visible in this open-source repository, including the exact regex and action names, and even test QR strings), requires no credentials, no operator badge, and no network access to the backend — a printed piece of paper with the right text is sufficient. The action fires unconditionally the moment the code is recognized during any signup attempt (self-serve idle scanning or normal operator-flow scanning), before any authentication call is made.

### Recommendation
- Require the same backend-verified operator authorization (`verify_operator_qr_code` / `backend::operator_status::request`) to succeed *before* dispatching `MagicResetMirror` / `MagicResetWifi`, rather than after/independently of it.
- Alternatively, sign/HMAC the magic QR payload with a secret provisioned only to legitimate operators/support tooling, and validate that signature before executing the reset actions.
- Rate-limit and audit-log magic QR code usage (already partially done via `dd_incr!`), and consider requiring physical/local confirmation (e.g. button press) in addition to QR-based triggering for destructive actions.

### Proof of Concept
1. Print or display a QR code containing the literal text `magic_action:reset_mirror_calibration` (or `magic_action:reset_wifi_credentials`).
2. Present it to the orb's camera during idle/self-serve QR scanning or at the start of a normal signup flow.
3. Observe in `handle_magic_operator_qr_code` (`src/plans/mod.rs`) that `reset_mirror_calibration`/`reset_wifi_and_ensure_network` executes immediately, with `verify_operator_qr_code` (the operator-authenticity check) never having been called for this code, as shown by the control flow in `scan_initial_qr_codes`/`scan_remaining_qr_codes`.

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

**File:** src/plans/mod.rs (L788-841)
```rust
    async fn scan_remaining_qr_codes(
        &mut self,
        orb: &mut Orb,
        qr_codes: QrCodes,
        operator_qr_expiration_time: Duration,
    ) -> Result<Option<ResolvedQrCodes>> {
        loop {
            match qr_codes {
                QrCodes::Both { operator_data, user_qr_code, user_data, user_qr_code_string }
                    if operator_data.timestamp.elapsed() < operator_qr_expiration_time =>
                {
                    break Ok(Some(ResolvedQrCodes {
                        operator_data,
                        user_qr_code,
                        user_data,
                        user_qr_code_string,
                    }));
                }
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
