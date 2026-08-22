Found a strong analog. The magic operator QR-code mechanism in `src/plans/qr_scan/operator.rs` allows a well-known static QR-code string (`magic_action:reset_wifi_credentials` / `magic_action:reset_mirror_calibration`) to trigger privileged Orb actions, and `MasterPlan::handle_magic_operator_qr_code` in `src/plans/mod.rs` executes those actions with zero authorization/backend validation — exactly mirroring the Rubicon bug class where a function meant only for privileged actors (there, "keepers"; here, the Orb "operator") is reachable by any unprivileged party who can simply show/print the trigger value, bypassing the normal operator-authentication path (`verify_operator_qr_code`/`backend::operator_status::request`) that legitimate operator QR-codes must pass. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) 

### Title
Unauthenticated "Magic" QR-Codes Allow Any Unprivileged Person to Trigger Privileged Orb Reset Actions - (File: src/plans/qr_scan/operator.rs, src/plans/mod.rs)

### Summary
The Orb's operator QR-code scanning path recognizes two hard-coded, publicly-known "magic" strings — `magic_action:reset_wifi_credentials` and `magic_action:reset_mirror_calibration` — and, if matched, immediately executes privileged device actions (Wi-Fi credential reset and mirror-calibration reset) without any backend authorization check, unlike normal operator QR-codes which must pass `backend::operator_status::request()` validation.

### Finding Description
`qr_scan::operator::Data::try_parse` first attempts to parse the scanned code as a normal, backend-verifiable operator QR-code (`user::Data`). If that fails, it falls back to a regex match against `magic_action:(?P<magic_action>[\w]+)` and, for two specific literal values, returns `Data::MagicResetWifi` or `Data::MagicResetMirror` with no cryptographic signature, backend call, or other authorization proof involved. [5](#0-4) 

These magic variants are consumed by `MasterPlan::handle_magic_operator_qr_code`, which is called on every operator-QR-code scan (`scan_initial_qr_codes` / `scan_remaining_qr_codes`) before the normal `verify_operator_qr_code` authorization step ever runs. When a magic action is detected, the function directly calls `self.reset_mirror_calibration(orb)` or `self.reset_wifi_and_ensure_network(orb)` and returns `None` (short-circuiting the normal signup flow), meaning these privileged actions execute unconditionally, with no operator identity check at all. [2](#0-1) [6](#0-5) 

By contrast, a normal (non-magic) operator QR-code is only accepted after `verify_operator_qr_code` calls out to the backend's `/orb/{id}/status` endpoint and receives `valid: true` plus location data — i.e., real operator authorization requires backend-issued, per-operator validation. [4](#0-3) 

This is directly analogous to the Rubicon finding: `offer(uint,ERC20,uint,ERC20)` and `insert(uint,uint)` were meant to be "keeper-only" but had no access-control gate, letting any caller invoke privileged orderbook-manipulation logic that bypassed the normal, safe matching path. Here, the "magic" QR-code strings are meant to be operator/technician-only maintenance triggers, but the code contains no gate — anyone who can show the printed/known magic string to the Orb's camera can invoke privileged device-reset logic that bypasses the normal, backend-authorized operator path.

### Impact Explanation
An unprivileged person — with no operator credentials, no backend account, and no physical/insider access — who obtains or guesses the magic string (it is a fixed literal embedded in the client binary and thus recoverable via reverse engineering or by anyone who has seen it once) can walk up to any deployed Orb and:
- Force it to reset and re-request Wi-Fi credentials (`reset_wifi_and_ensure_network`), causing denial-of-service by dropping the Orb off its network and requiring a new Wi-Fi QR-code before it can resume signups, or potentially rejoining it to an attacker-controlled network if the attacker also supplies the subsequent Wi-Fi QR-code.
- Force a mirror-calibration reset (`reset_mirror_calibration`), which can degrade or disrupt biometric capture quality/reliability for all subsequent signups on that Orb until recalibrated.

Both actions are meant to be technician/operator-restricted maintenance operations, yet are reachable by anyone in the general public.

### Likelihood Explanation
Likelihood is high: no authentication token, backend round-trip, or operator role is required — only physical presentation of a QR-code containing a fixed, guessable literal string to the Orb's camera. Because the trigger values are compiled into the client and used identically across all deployed Orbs, discovery of the string once (e.g., via firmware/binary extraction) compromises every Orb using this build.

### Recommendation
Require the same backend-mediated operator authorization for magic actions as for normal operator QR-codes (i.e., only accept `MagicResetWifi`/`MagicResetMirror` after successfully validating an authorized-operator identity/session, or embed the action in a backend-issued signed/short-lived token instead of a static string). Alternatively, remove the unauthenticated magic-QR path entirely and require these maintenance actions to be triggered exclusively through an authenticated operator/technician tool.

### Proof of Concept
1. Extract or learn the magic strings `magic_action:reset_wifi_credentials` / `magic_action:reset_mirror_calibration` (present verbatim in `src/plans/qr_scan/operator.rs`). [7](#0-6) 
2. Generate a QR-code encoding one of these strings.
3. Present the QR-code to any deployed Orb during its idle "Operator QR-code scanning" phase (`scan_operator_qr_code` → `handle_magic_operator_qr_code`). [8](#0-7) 
4. Observe the Orb immediately execute `reset_wifi_and_ensure_network` or `reset_mirror_calibration` with no backend authorization check, confirmed by the existing unit test that shows both strings parse successfully with zero validation. [9](#0-8)

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

**File:** src/plans/qr_scan/operator.rs (L74-81)
```rust
        {
            let code = "magic_action:reset_wifi_credentials";
            assert!(matches!(Data::try_parse(code), Some(Data::MagicResetWifi)));
        }
        {
            let code = "magic_action:reset_mirror_calibration";
            assert!(matches!(Data::try_parse(code), Some(Data::MagicResetMirror)));
        }
```

**File:** src/plans/mod.rs (L749-785)
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
```

**File:** src/plans/mod.rs (L874-923)
```rust
    async fn scan_operator_qr_code(
        &self,
        orb: &mut Orb,
        timeout: Option<Duration>,
    ) -> Result<Option<qr_scan::operator::Data>> {
        orb.set_phase("Operator QR-code scanning").await;
        let qr_capture_start = Instant::now();
        loop {
            dd_incr!("main.count.signup.during.general.distributor_identification_request");

            let remaining_timeout = timeout
                .map(|timeout| {
                    timeout
                        .checked_sub(qr_capture_start.elapsed())
                        .ok_or(qr_scan::ScanError::Timeout)
                })
                .transpose();
            #[cfg_attr(not(feature = "internal-data-acquisition"), allow(unused_mut))]
            let mut result = match remaining_timeout {
                Ok(timeout) => {
                    if let Some(qr) = &self.operator_qr_code_override {
                        tracing::info!("Operator QR-code provided from CLI");
                        Ok(qr.clone())
                    } else {
                        qr_scan::Plan::<qr_scan::operator::Data>::new(timeout, false)
                            .run(orb)
                            .await?
                            .map(|(qr_code, _)| qr_code)
                    }
                }
                Err(err) => Err(err),
            };
            #[cfg(feature = "internal-data-acquisition")]
            if !self.data_acquisition {
                result = result.and_then(|data| {
                    if let qr_scan::operator::Data::Normal(data) = &data {
                        if data.signup_extension {
                            return Err(qr_scan::ScanError::Invalid);
                        }
                    }
                    Ok(data)
                });
            }
            orb.reset_rgb_camera().await?;
            match result {
                Ok(qr_code) => {
                    orb.ui.qr_scan_completed(QrScanSchema::Operator);
                    dd_incr!("main.count.global.distr_code_detected");
                    return Ok(Some(qr_code));
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

**File:** src/backend/operator_status.rs (L46-66)
```rust
pub async fn request(qr_code: &qr_scan::user::Data) -> Result<Status> {
    let request = super::client()?
        .get(format!(
            "{}/api/v1/distributor/{}/orb/{}/status",
            *SIGNUP_BACKEND_URL, qr_code.user_id, *ORB_ID
        ))
        .basic_auth(&*ORB_ID, Some(get_orb_token()?));
    let status: Status = match request.send().await?.error_for_status() {
        Ok(response) => response.json().await?,
        Err(err) => {
            tracing::error!("Received error response {err:?}");
            return Err(err.into());
        }
    };
    if !status.valid {
        tracing::info!(
            "Operator QR-code invalid: {qr_code:?}, reason: {:?}",
            status.reason.as_deref().unwrap_or("<empty>")
        );
        return Ok(status);
    }
```
