### Title
Signup-extension flag in operator QR-code fully bypasses backend authorization check - ([File: src/plans/mod.rs])

### Summary
`verify_operator_qr_code` skips the entire backend legitimacy check for an operator QR-code whenever the *scanned QR-code payload itself* claims to be a "signup extension" code (`qr_code.signup_extension()`), mirroring the reported Uniswap-pool bug pattern where legitimacy was inferred from self-reported/unauthenticated data instead of an independent authority.

### Finding Description
`verify_operator_qr_code` is supposed to authenticate the operator QR-code against the backend before proceeding with a signup: [1](#0-0) 

However, before making the backend call, it contains a short-circuit:
```rust
if qr_code.signup_extension() || self.operator_qr_code_override.is_some() {
    return Ok(Some((0, backend::operator_status::LocationData {
        team_operating_country: "DEV".to_string(),
        ...
    })));
}
```
`qr_code.signup_extension()` is a boolean flag that is derived purely from parsing the text of the scanned QR-code, with no cryptographic signature or backend cross-check — analogous to `IUniswapV3Pool(_marketPool).token0()`/`token1()` being trusted at face value in the reported bug instead of being verified through an authoritative registry (`UniswapV3Factory.getPool()`). [2](#0-1) 
The regex-driven parser (`QR_CODE_SIGNUP_EXTENSION`) that sets `signup_extension = true` operates purely on the content of the presented QR code string; there is no separate authenticity check tying this flag to an actual authorized data-acquisition session, and it directly controls whether the operator-authorization backend call is performed at all.

### Impact Explanation
If this code path can be reached with attacker-supplied QR-code content (e.g., an unprivileged individual presenting a crafted QR code formatted as a signup-extension code to a physical Orb), the Orb will treat the code as a validly-authorized operator without ever contacting `SIGNUP_BACKEND_URL` to check whether the operator/distributor ID is legitimate, revoked, or geofenced. That is a direct authorization bypass for entering the signup flow — the same root cause class as the reported bug (trusting self-reported, unverified data as proof of legitimacy) — and could enable unauthorized signup sessions to be initiated under a fabricated "DEV"/(0,0) location context.

### Likelihood Explanation
Exploitability depends on whether the `internal-data-acquisition` feature (which gates the `signup_extension_config`-based QR parsing) is compiled into the fielded production firmware and whether `self.data_acquisition` mode is otherwise gated to trusted operators only; this repo snapshot does not let me confirm the exact production feature-flag configuration or all downstream gating in `handle_user_qr_code`/`idle.rs`, so likelihood is uncertain and should be verified in the full build configuration.

### Recommendation
- Do not let a self-reported flag parsed directly from the scanned QR-code payload (`signup_extension()`) bypass the backend operator-authorization check.
- If a signup-extension/data-acquisition mode is legitimately meant to skip backend calls, gate it behind an independently verified, backend-issued or cryptographically-signed credential (or a build-time / device-provisioning trust flag), not a value parsed straight out of untrusted QR-code text.
- Audit all other locations using `qr_code.signup_extension()`/`operator_data.qr_code.signup_extension()` as an authorization decision input to ensure they can't be triggered by crafted QR-code content presented by an unprivileged party.

### Proof of Concept
Not fully constructible from the indexed code alone: exploitation requires confirming (1) that `internal-data-acquisition` is enabled in the deployed build and (2) that no additional runtime gate (outside what was retrieved) prevents an arbitrary bystander from placing the Orb into a state where `verify_operator_qr_code` is called with a crafted signup-extension-formatted QR code. Conceptually: an attacker crafts a QR-code string matching `QR_CODE_SIGNUP_EXTENSION`'s expected format (`userid:<id>:<policy>:<mode>[:<params>]`), presents it to the Orb's camera as the "operator" QR-code; `Data::try_parse` sets `signup_extension = true`; `verify_operator_qr_code` then returns `Ok(Some(...))` with a hardcoded "DEV" location without ever calling `backend::operator_status::request`, bypassing the intended backend-side legitimacy check entirely. [3](#0-2)

### Citations

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

**File:** src/plans/qr_scan/user.rs (L142-157)
```rust
    #[cfg(feature = "internal-data-acquisition")]
    #[must_use]
    fn from_signup_extension(captures: &Captures) -> Self {
        let v2_data = Self::from_v2(captures);
        let mode = SignupMode::parse(captures.name("mode").map(|mode_group| mode_group.as_str()));
        let parameters = captures
            .name("parameters")
            .map(|parameters_group| parameters_group.as_str().to_string());

        Self {
            user_id: v2_data.user_id,
            signup_extension: true,
            signup_extension_config: mode.map(|mode| SignupExtensionConfig { mode, parameters }),
            user_data_hash: None,
        }
    }
```
