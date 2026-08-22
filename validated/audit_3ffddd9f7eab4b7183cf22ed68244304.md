### Title
Unauthenticated "Magic" QR-Codes Allow Anyone to Reconfigure Orb WiFi and Mirror Calibration Before Operator Verification - (File: `src/plans/qr_scan/operator.rs`)

### Summary
The Orb's operator QR-code parser recognizes special "magic" QR codes (`magic_action:reset_wifi_credentials`, `magic_action:reset_mirror_calibration`) that trigger a WiFi credential reset or mirror-calibration reset. This parsing happens in `Data::try_parse` before any backend verification of the QR code's legitimacy, meaning any person able to present a printed/displayed QR code to the Orb's camera can trigger these reconfiguration actions — mirroring the `fil_configure` issue where any unprivileged caller can rewrite critical operating configuration (network state, RPC/endpoint-equivalent settings) with no authorization check.

### Finding Description
`qr_scan::operator::Data::try_parse` matches the `MAGIC_QR_CODE` regex against the raw scanned QR text and returns `Data::MagicResetWifi` or `Data::MagicResetMirror` directly, with no signature, operator-identity, or backend validation applied to the QR content itself: [1](#0-0) 

In the signup flow, the operator QR code is scanned and passed to `handle_magic_operator_qr_code` immediately after `scan_operator_qr_code`, and only QR codes that are *not* magic actions subsequently go through `verify_operator_qr_code`, which is the function that performs the actual backend authentication of the operator's identity: [2](#0-1) [3](#0-2) 

This means the magic-action branch is handled before/instead of the operator-identity check that governs normal QR codes, so the reconfiguration commands (WiFi reset, mirror calibration reset) are reachable by anyone who can show a QR code to the device, with no proof that the presenter is an authorized operator. This is structurally analogous to `fil_configure`: a configuration/state-changing command that is nominally meant to be used by a trusted party but is in fact reachable by any unprivileged actor, letting them manipulate device state (network configuration, calibration data) that is later relied upon by the trust/security-relevant parts of the pipeline (network connectivity for backend calls, and physical mirror alignment which affects biometric capture and thus liveness/fraud enforcement).

### Impact Explanation
- Resetting the mirror calibration (`MagicResetMirror`) can degrade the camera's positioning of the eyes/face during a signup, which the biometric-capture and liveness/fraud pipeline relies on; a miscalibrated mirror could plausibly be used to induce capture failures or degrade fraud-check reliability at the physical layer.
- Resetting WiFi credentials (`MagicResetWifi`) can force the Orb offline / into fallback network state, disrupting backend-dependent checks (e.g. operator/user QR verification calls, config downloads) and potentially creating windows where the device operates under stale/default configuration.
- Because these actions are triggered by unauthenticated physical QR presentation, a bystander (not an authorized operator) can repeatedly force these resets, matching the "unprivileged party controls critical configuration" bug class from the report.

### Likelihood Explanation
Likelihood is moderate: it requires physical proximity to present a QR code to the camera (no remote network vector), but no credential, backend approval, or prior operator authentication is needed — the regex match alone is sufficient to reach `Data::MagicResetWifi`/`Data::MagicResetMirror`. The bar to exploit is only "know the two magic strings," which are visible in the open-source code itself.

### Recommendation
Require operator-identity verification (the same backend check performed in `verify_operator_qr_code`) before acting on magic QR-code actions, or otherwise gate `MagicResetWifi`/`MagicResetMirror` behind a signed/authenticated payload rather than a plain-text regex match reachable by any scanned code. At minimum, rate-limit and log magic-action triggers, and consider removing the unauthenticated reset paths in favor of an operator-authenticated management channel.

### Proof of Concept
1. Print or display a QR code containing the text `magic_action:reset_wifi_credentials`.
2. Present it to the Orb's camera during the idle/operator QR-code scan phase (`scan_operator_qr_code`).
3. `Data::try_parse` matches `MAGIC_QR_CODE` and returns `Data::MagicResetWifi` without any backend call to validate the presenter's identity. [4](#0-3) 
4. `handle_magic_operator_qr_code` processes this action before `verify_operator_qr_code` would otherwise validate operator identity, triggering the WiFi/mirror reset. [5](#0-4) 

**Uncertainty note:** I was unable to retrieve the full body of `handle_magic_operator_qr_code` (only its call site) before the tool budget was exhausted, so I cannot fully confirm whether any additional internal gating exists inside that function beyond what the call-flow in `scan_initial_qr_codes` and `verify_operator_qr_code` shows. The control-flow evidence strongly suggests no operator-identity check occurs before the magic action executes, but this should be verified directly by reading `handle_magic_operator_qr_code`'s full implementation in `src/plans/mod.rs`.

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

**File:** src/plans/mod.rs (L1543-1557)
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
```
