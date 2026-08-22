### Title
Magic operator QR codes bypass backend operator authorization, letting any unprivileged user trigger privileged Orb actions - ([File: src/plans/mod.rs])

### Summary
The reported `flexGovernanceAdapater` bug is a missing-authorization pattern: privileged operations are executed without checking that the caller is a whitelisted/authorized party. The same pattern is reachable in `orb-core`'s QR-code parsing flow for "magic" operator QR codes: `handle_magic_operator_qr_code` executes privileged device actions (Wi-Fi credential reset, mirror-calibration reset) purely on the basis of a regex-matched string, before the code path that authenticates the operator against the backend (`verify_operator_qr_code`) ever runs.

### Finding Description
During signup, the Orb repeatedly scans for an "operator" QR code and normally validates it against the signup backend via `verify_operator_qr_code`, which calls `backend::operator_status::request` (an authenticated, backend-controlled whitelist check) [1](#0-0) .

However, in both `scan_initial_qr_codes`/`scan_remaining_qr_codes`, the raw scanned QR string is first passed to `handle_magic_operator_qr_code` — and only if that returns `Some` (i.e., the code was a "Normal" operator code, not a magic action) does the flow proceed to `verify_operator_qr_code`: [2](#0-1) 

`handle_magic_operator_qr_code` itself performs no authorization/whitelist check at all — it pattern-matches the QR payload and, for `MagicResetWifi`/`MagicResetMirror`, immediately executes `reset_wifi_and_ensure_network` or `reset_mirror_calibration` and returns, short-circuiting before any backend validation: [3](#0-2) 

The only gate preceding this is `check_signup_conditions`, which merely checks internet connectivity — not caller identity or authorization: [4](#0-3) 

The QR-code parser recognizes these magic strings via a public, fixed regex (`magic_action:reset_wifi_credentials`, `magic_action:reset_mirror_calibration`), with no secret, signature, or backend round-trip involved: [5](#0-4) 

This mirrors the reported bug class exactly: a function that performs a privileged action (`flexGovernanceAdapater`'s proposal creation / here, network and calibration reset) is reachable without any modifier/check restricting it to a whitelisted caller (there, whitelisted addresses; here, a backend-validated operator).

### Impact Explanation
Any person able to present a QR code to the Orb's camera — not just a backend-authorized/whitelisted operator — can force a Wi-Fi credential reset. `reset_wifi_and_ensure_network` calls `network::reset()` and then `wifi::Plan.ensure_network_connection`, which (per the module structure in `src/plans/wifi/mod.rs`) re-triggers the Orb's Wi-Fi (re)configuration/join flow. Forcing this outside of the legitimate operator's control lets an unprivileged attacker disrupt or redirect the Orb's network connectivity at will during any signup attempt, and repeatedly interrupt/deny signups (denial of service against the signup flow) without needing operator credentials. Because the Orb's operator/user QR verification and biometric-package upload depend on network reachability to the signup backend (`backend::operator_status::request`, `backend::user_status::request`, `backend::signup_post::request`), unauthorized control over the Orb's network state is a plausible vector to disrupt or manipulate the trust boundary that normally gates which "operator" is allowed to run a signup — the same trust boundary the reported governance bug violates (unauthorized control of a function meant to be gated to authorized parties).

I was not able to fully verify what `network::reset()` and `wifi::Plan.ensure_network_connection` do internally (e.g., whether reset falls back to an attacker-joinable state, such as re-opening WPS/AP mode or clearing to an insecure default), because I could not retrieve the full contents of `src/plans/wifi/mod.rs` / `src/network.rs` — this is a limitation of the available index, and a full assessment of whether this enables backend-response spoofing (and thus signup misattribution/fraud bypass) would need direct inspection of those files.

### Likelihood Explanation
The precondition is minimal: physical/visual access to the Orb's camera during the operator-QR scanning phase, which is the exact same surface a legitimate operator uses. The magic strings are static and documented in the shipped code and its tests (`src/plans/qr_scan/operator.rs`), so any bystander could reproduce a working QR code with no credentials, tokens, or backend interaction. This is a realistic "malicious normal user abusing valid product/protocol flows" scenario.

### Recommendation
Require the magic-action QR codes to go through the same operator-authorization path as normal operator QR codes (i.e., call `verify_operator_qr_code`/backend `operator_status::request` and confirm the presenting party is a whitelisted/valid operator) before dispatching `reset_mirror_calibration` or `reset_wifi_and_ensure_network`. Alternatively, replace the static magic strings with a backend-issued, time-limited, signed token bound to a specific authorized operator/session, and reject the action if verification fails, consistent with the reported recommendation of restricting privileged calls to whitelisted callers.

### Proof of Concept
1. Generate a QR code containing the literal string `magic_action:reset_wifi_credentials` (or `magic_action:reset_mirror_calibration`), as validated by the existing unit test in `src/plans/qr_scan/operator.rs` (`test_qr_code_variants`).
2. Present this QR code to the Orb during the "Operator QR-code scanning" phase (before any button press by a legitimate operator, or during the loop in `scan_remaining_qr_codes`).
3. Observe that `handle_magic_operator_qr_code` matches `Data::MagicResetWifi`/`Data::MagicResetMirror` and immediately calls `reset_wifi_and_ensure_network`/`reset_mirror_calibration`, returning `Ok(None)` without ever calling `verify_operator_qr_code` or any backend authorization check — confirming the action executes for an unauthenticated/unwhitelisted presenter.

### Citations

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

**File:** src/plans/mod.rs (L1543-1560)
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
```

**File:** src/plans/mod.rs (L2050-2066)
```rust
async fn check_signup_conditions(orb: &mut Orb) -> Result<bool> {
    if let Some(report) = orb.net_monitor.last_report()? {
        // Drop the mutex lock fast.
        let Config { block_signup_when_no_internet, .. } = *orb.config.lock().await;
        if block_signup_when_no_internet && report.is_no_internet() {
            orb.ui.no_internet_for_signup();
            dd_incr!("main.count.signup.result.failure.internet_check", "type:too_slow_to_start");
            return Ok(false);
        }
        if report.is_slow_internet() {
            orb.ui.slow_internet_for_signup();
            dd_incr!("main.count.signup.result.failure.internet_check", "type:too_slow_to_start");
            return Ok(true);
        }
    }
    Ok(true)
}
```

**File:** src/plans/qr_scan/operator.rs (L8-61)
```rust
/// An opt-in operator qr code for testing purposes.
pub const DUMMY_OPERATOR_QR_CODE: &str = "userid:66ad4897-0ca7-4727-8365-ca808348e3cd:1";

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
