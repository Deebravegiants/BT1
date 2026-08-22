Based on my investigation, the analog vulnerability is confirmed: the `signup_extension` flag on a scanned QR-code — a value fully controlled by whoever presents the QR code to the orb, i.e. an unprivileged operator/user — is used to bypass the backend operator-identity verification call entirely.

### Title
Operator QR-code verification bypass via unvalidated `signup_extension` flag - ([File: src/plans/mod.rs])

### Summary
`verify_operator_qr_code` in `src/plans/mod.rs` is meant to validate an operator's identity against the backend before a signup session is allowed to proceed. However, if the scanned QR-code sets `signup_extension() == true` (a boolean fully derived from attacker-controlled QR-code text, parsed in `src/plans/qr_scan/user.rs`), the function short-circuits and returns a synthetic "valid" result with hardcoded `DEV` location data, never calling `backend::operator_status::request`.

### Finding Description
`verify_operator_qr_code` [1](#0-0)  checks `qr_code.signup_extension() || self.operator_qr_code_override.is_some()` and, if true, immediately returns `Ok(Some((0, LocationData { team_operating_country: "DEV", ... })))` without contacting the backend at all. Only in the `else` branch does it call `backend::operator_status::request(qr_code)` to perform real authorization.

`signup_extension` is set from parsing the raw QR-code string itself: `Data::from_signup_extension` sets `signup_extension: true` whenever the QR text matches the `QR_CODE_SIGNUP_EXTENSION` regex (`userid:<id>:<policy>::<mode>[:<params>]::`) [2](#0-1) , and the parsing entry point `try_parse` dispatches to this constructor whenever the "internal-data-acquisition" feature is compiled in [3](#0-2) . This means the flag that disables backend validation is derived purely from the content of the physical QR-code being scanned — data supplied by whoever is standing in front of the orb, not from any signed/authenticated source.

This is a direct analog to the reported "unsafe initialization" bug class: the initialization/validation gate (`verify_operator_qr_code`, which is architecturally supposed to be the "gatekeeper" analogous to a contract `initialize()` function establishing trusted state before further calls) accepts an untrusted, self-declared parameter (`signup_extension`) as a bypass condition instead of validating the caller/data against a trusted authority.

### Impact Explanation
If reachable in a production configuration with `internal-data-acquisition` enabled, any operator-position QR-code crafted with the `signup_extension` marker skips the operator authorization/location check performed against `SIGNUP_BACKEND_URL`. Downstream, `scan_remaining_qr_codes`/`scan_initial_qr_codes` use the resulting `OperatorData` (with fabricated `DEV` location) to gate the rest of the signup flow, including biometric capture and enrollment [4](#0-3) . This allows an unauthorized/unregistered "operator" to initiate and complete signups, misattributing them with fake location/authorization data, i.e. unauthorized signup and cross-signup data bleed of the operator-identity trust boundary.

### Likelihood Explanation
Likelihood depends entirely on whether the `internal-data-acquisition` feature is compiled into the fielded orb-core binary; the `#[cfg(feature = "internal-data-acquisition")]` gate on `QR_CODE_SIGNUP_EXTENSION`/`from_signup_extension` means this path is dead code in builds without that feature. I was not able to determine from the index whether production orb builds ship with this feature enabled — this needs to be verified directly against the build configuration/Cargo feature flags used for production images, which is outside what the code index can confirm.

### Recommendation
Do not let a value derived from the scanned QR-code text itself (`signup_extension`) bypass the backend operator-authorization call. If the "data acquisition/signup extension" mode is intended only for internal test rigs, gate the bypass behind an explicit, separately-authenticated internal-only flag (e.g., a build-time secret or a CLI-only override that cannot be triggered by physical QR-code content), and always require `backend::operator_status::request` to succeed for any operator-initiated signup in the field.

### Proof of Concept
1. Build orb-core with the `internal-data-acquisition` feature enabled.
2. Present a QR-code as operator matching the `QR_CODE_SIGNUP_EXTENSION` pattern, e.g. `userid:11111111-1111-1111-1111-111111111111:1::0::` (valid UUID, data-policy, mode `0`=Basic, terminator `::`).
3. `Data::try_parse` parses this via `from_signup_extension`, setting `signup_extension = true` [5](#0-4) .
4. `verify_operator_qr_code` sees `qr_code.signup_extension() == true` and returns `Ok(Some(...))` with fabricated `DEV` location data, skipping the `backend::operator_status::request` call entirely [6](#0-5) .
5. The signup flow proceeds treating this as a verified operator, without any backend-side authorization check having occurred.

### Citations

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

**File:** src/plans/qr_scan/user.rs (L106-123)
```rust
    fn try_parse(code: &str) -> Option<Self> {
        if let Ok((user_id, user_data_hash)) = decode_qr(code) {
            return Some(Self {
                user_id: user_id.hyphenated().to_string(),
                signup_extension: false,
                signup_extension_config: None,
                user_data_hash: Some(user_data_hash),
            });
        }
        if let Some(captures) = QR_CODE_V2.captures(code) {
            return Some(Data::from_v2(&captures));
        }
        #[cfg(feature = "internal-data-acquisition")]
        if let Some(captures) = QR_CODE_SIGNUP_EXTENSION.captures(code) {
            return Some(Data::from_signup_extension(&captures));
        }
        None
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
