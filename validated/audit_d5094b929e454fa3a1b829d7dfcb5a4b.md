### Title
Unauthenticated "magic" QR codes let anyone reset WiFi credentials or mirror calibration on an idle Orb - ([File: src/plans/qr_scan/operator.rs])

### Summary
`Data::try_parse` in `src/plans/qr_scan/operator.rs` accepts any QR code matching `magic_action:reset_wifi_credentials` or `magic_action:reset_mirror_calibration` and returns `Data::MagicResetWifi`/`Data::MagicResetMirror`. `handle_magic_operator_qr_code` in `src/plans/mod.rs` executes the corresponding privileged action (`reset_wifi_and_ensure_network` / `reset_mirror_calibration`) immediately, with no operator identity check, since these magic variants bypass `verify_operator_qr_code` entirely.

### Finding Description
The operator QR scan loop in `scan_remaining_qr_codes`/`scan_initial_qr_codes` calls `scan_operator_qr_code`, which parses the raw QR string via `qr_scan::operator::Data::try_parse` [1](#0-0) . The regex `MAGIC_QR_CODE` matches any string of the shape `magic_action:<word>` and maps `reset_wifi_credentials`/`reset_mirror_calibration` directly to enum variants, with no cryptographic signature, HMAC, or backend authorization check tied to these variants [2](#0-1) .

The result flows straight into `handle_magic_operator_qr_code`, which pattern-matches on the variant and, for `MagicResetMirror`/`MagicResetWifi`, calls `self.reset_mirror_calibration(orb)` or `self.reset_wifi_and_ensure_network(orb)` unconditionally [3](#0-2) . Crucially, `verify_operator_qr_code` — which is presumably where the operator's identity/badge/permissions would be checked against the backend — is only invoked for the `Data::Normal` branch and only *after* `handle_magic_operator_qr_code` has already returned; magic actions return `Ok(None)` and `continue`, so `verify_operator_qr_code` is never reached for them [4](#0-3) . There is no session/operator-role gate anywhere in this path — the sole check is "does the QR text match this regex."

`reset_wifi_and_ensure_network` calls `network::reset()` (restores default wpa_supplicant config and disconnects) then `wifi::Plan.ensure_network_connection`, which — if the Orb is left disconnected — prompts for a hotspot QR scan and joins whatever network credentials are presented next [5](#0-4) [6](#0-5) . `reset_mirror_calibration` overwrites the calibration file and re-runs the mirror recalibration routine, changing the camera/mirror geometry used for subsequent signups [7](#0-6) .

### Impact Explanation
An unprivileged person standing in front of an idle Orb can, by presenting a printed QR code with the text `magic_action:reset_wifi_credentials`, force the Orb to drop its WiFi network and then present a follow-up hotspot QR to join it to an attacker-controlled network — a network-takeover primitive that can enable interception/manipulation of backend responses for subsequent signups. Alternatively, presenting `magic_action:reset_mirror_calibration` forces a mirror recalibration cycle that alters the camera geometry used for the *next* legitimate signup, potentially degrading or manipulating biometric capture quality/positioning. Both are denial-of-service / integrity-disruption impacts reachable purely from a QR shape, matching a "state manipulation without authorization" bounty class.

### Likelihood Explanation
Fully feasible and repeatable: it requires only printing a static string as a QR code and holding it in front of an idle Orb during the normal operator-scan phase — no operator credentials, tokens, or backend access are needed. The regex and dispatch logic are deterministic and always reachable in this state.

### Recommendation
Gate `MagicResetWifi`/`MagicResetMirror` execution behind an actual operator-authorization check (e.g., require these actions be nested inside/derived from an already-verified operator QR/session, or require a signed/HMAC'd payload validated against a backend-issued secret) rather than accepting them as free-standing, unauthenticated strings recognized before `verify_operator_qr_code` runs.

### Proof of Concept
Integration test in `src/plans/mod.rs` (or a new test module) mirroring the existing pattern used at `src/plans/mod.rs:2169-2281`:
1. Build a `MasterPlan` with `operator_qr_code_override` set to `Some(Some("magic_action:reset_mirror_calibration"))`, with no prior operator verification/session state (fresh `Orb::builder().build()`).
2. Call `ms.scan_operator_qr_code(&mut fake_orb, None)` then `ms.handle_magic_operator_qr_code(&mut fake_orb, op_code)`.
3. Assert that `reset_mirror_calibration` was invoked (e.g., via a mock/spy on `Orb::recalibrate` or by checking `orb.ui` received `magic_qr_action_completed`) **without** any call to `verify_operator_qr_code` or backend operator-status check having occurred first.
4. Expected (fixed) behavior: the call should fail/no-op unless a valid operator authorization context is established; currently it succeeds unconditionally, confirming the bypass.

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

**File:** src/plans/wifi/mod.rs (L43-68)
```rust
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
```
