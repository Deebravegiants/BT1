### Title
Unauthenticated Magic-Action QR Codes Trigger Privileged Wi-Fi/Mirror Resets Without Operator Verification - (File: src/plans/mod.rs)

### Summary
`MasterPlan::handle_magic_operator_qr_code` executes `reset_wifi_and_ensure_network` or `reset_mirror_calibration` as soon as a QR string matching `magic_action:reset_wifi_credentials` / `magic_action:reset_mirror_calibration` is decoded, with no check that the presenter is an authenticated operator. Because these strings are fixed constants recognized by `qr_scan::operator::Data::try_parse`, anyone who can show a printed QR code to the Orb's camera during the idle/signup scan loop can repeatedly force a Wi-Fi disconnect/reconnect cycle or mirror recalibration.

### Finding Description
`qr_scan::operator::Data::try_parse` first tries to parse the code as a normal operator QR (`user::Data::try_parse`), and if that fails, matches it against the `MAGIC_QR_CODE` regex, returning `Data::MagicResetWifi` or `Data::MagicResetMirror` for the two known action strings — with no operator credential, signature, or session marker required. [1](#0-0) 

Both `scan_initial_qr_codes` (entered from idle) and `scan_remaining_qr_codes` immediately feed any scanned operator QR into `handle_magic_operator_qr_code` before any operator-identity verification (`verify_operator_qr_code`) occurs: [2](#0-1) [3](#0-2) 

`handle_magic_operator_qr_code` dispatches directly to the privileged actions on match, with no authorization gate: [4](#0-3) 

`reset_wifi_and_ensure_network` calls `network::reset()`, which shells out twice to the `wpa-supplicant-interface` SGID/SUID helper binary (`restore-default-config` then `reconfigure`), tearing down the current Wi-Fi connection and forcing the Orb back into hotspot-QR provisioning via `wifi::Plan.ensure_network_connection`: [5](#0-4) [6](#0-5) 

`reset_mirror_calibration` overwrites the on-disk calibration file and re-applies default mirror config values via `orb.recalibrate`: [7](#0-6) 

The two magic strings and their behavior are visible directly in the repository's own unit tests, so an attacker does not need to reverse engineer anything: [8](#0-7) 

No rate limiting, cooldown, or "already authenticated operator" state is checked before executing the magic action — the loop simply `continue`s and rescans, so the same magic QR can be re-presented indefinitely.

### Impact Explanation
Repeated presentation of `magic_action:reset_wifi_credentials` forces the Orb to disconnect from its configured Wi-Fi network and re-invoke the privileged `wpa-supplicant-interface` child process on every presentation, and then block in `wifi::Plan.ensure_network_connection` waiting for a new hotspot-QR — this is a denial-of-service against normal signup operation (network unavailability, wedged idle loop) that requires operator intervention to recover. `magic_action:reset_mirror_calibration` similarly degrades signup capture quality/availability by resetting mirror calibration to default values without any real recalibration routine being run. Both are triggerable by an unprivileged bystander with only physical line-of-sight to the Orb's camera, satisfying the "signup DoS via repeated resets" and "unauthorized state transition without operator authorization" impact classes.

### Likelihood Explanation
High feasibility and full repeatability: the magic strings are fixed, public (already present in this repo's own test file), require no cryptographic material, backend interaction, or prior session state, and both `scan_initial_qr_codes` and `scan_remaining_qr_codes` reach `handle_magic_operator_qr_code` before any operator identity is verified. The only precondition is physical presentation of a QR code to the Orb camera during idle/signup scanning, which is the normal attacker capability assumed for this class of finding.

### Recommendation
Require the magic-action QR codes to be gated behind the same operator authentication used for normal operator QR codes (e.g., only accept `MagicResetWifi`/`MagicResetMirror` when scanned together with, or signed by, a verified operator credential), and/or add a cooldown/rate-limit and audit log entry for magic-action invocations so a bystander cannot repeatedly force network/mirror resets without an authenticated operator being present.

### Proof of Concept
Integration test (extending the existing `src/plans/mod.rs` test module) that:
1. Builds a `MasterPlan`/`Orb` test harness and repeatedly feeds `"magic_action:reset_wifi_credentials"` through `scan_operator_qr_code` → `handle_magic_operator_qr_code` in a loop (simulating repeated bystander presentation), without ever supplying a verified operator QR code.
2. Asserts that `reset_wifi_and_ensure_network` (or a mock of `network::reset`) is invoked on every iteration, and that no operator/authentication marker (e.g., a "verified operator session" flag) is required or set before the call executes — demonstrating the missing authorization gate identified in `handle_magic_operator_qr_code` (`src/plans/mod.rs:978-1008`).
3. Repeats for `"magic_action:reset_mirror_calibration"`, asserting `reset_mirror_calibration` executes each time with no authorization check.

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

**File:** src/plans/qr_scan/operator.rs (L68-81)
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

**File:** src/plans/mod.rs (L761-769)
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
```

**File:** src/plans/mod.rs (L822-835)
```rust
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

**File:** src/network/mod.rs (L104-123)
```rust
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
