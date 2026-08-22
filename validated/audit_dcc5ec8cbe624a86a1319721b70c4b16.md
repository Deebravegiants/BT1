### Title
Operator QR-code authorization is bypassed using a self-declared, attacker-controlled flag instead of backend validation - (File: src/plans/mod.rs)

### Summary
`verify_operator_qr_code` is supposed to authenticate every operator QR-code against the backend before trusting the operator's identity and location. Instead, if the scanned QR-code data itself claims `signup_extension() == true` (a boolean derived purely from parsing the untrusted QR-code string), the function skips the backend call entirely and fabricates a "valid" result with hardcoded location data. This mirrors the `BribeVault` bug class where a security-relevant value is taken from unchecked user input rather than computed/validated through the trusted authority.

### Finding Description
`verify_operator_qr_code` is the sole gate that decides whether a scanned "operator" QR-code is authentic and returns real location data used for signup consistency checks: [1](#0-0) 

The very first branch trusts `qr_code.signup_extension()` — a field populated exclusively from parsing the raw QR-code string the operator/user presents to the camera — to bypass `backend::operator_status::request(qr_code)` (the actual trust-establishing call) altogether: [2](#0-1) 

`signup_extension` is set to `true` by `Data::from_signup_extension`, which is driven entirely by regex captures out of the scanned QR text (`mode`, `parameters`), with no cryptographic signature or backend round-trip involved: [3](#0-2) [4](#0-3) 

The same self-declared flag is also trusted downstream to skip the normal `handle_user_qr_code` validation flow and directly accept the operator/user pairing without calling `verify_user_qr_code`: [5](#0-4) 

In other words, the code that should establish operator authorization ("is this really a valid registered operator, and what is their verified location?") instead relies on a value taken as-is from attacker-controllable QR-code content — exactly the "fee is user input rather than a computed/validated value" pattern from the reported bug: a value that should come from a trusted/validated source (the backend `operator_status` check) is instead accepted verbatim from unauthenticated input.

### Impact Explanation
Any party able to present a crafted QR code encoding the `signup_extension` marker (`userid:<uuid>:<opt_in>::<mode>[:<parameters>]...`) can make the orb treat an arbitrary, unverified "operator" QR-code as validated, obtaining a fabricated `LocationData` (`"DEV"` country, `(0.0, 0.0)` coordinates) without ever contacting `backend::operator_status`. Since operator identity/location underpins operator-location consistency checks (`user_qr_validation_use_only_operator_location`) and gates the beginning of a signup flow, this allows an unauthorized/misattributed signup session to proceed with orb-side operator authorization effectively skipped, cross-signup state (mode/parameters) attacker-selected, and location trust assumptions violated.

### Likelihood Explanation
The attacker precondition is only the ability to physically present or emit a QR code to the orb's camera — no privileged credentials, backend access, or malicious-operator role required. This is squarely within the unprivileged-user QR-parsing/signup-authorization surface. The only open uncertainty is whether the `internal-data-acquisition` feature (which is what causes `signup_extension` to ever be set `true` at parse time) is compiled into the specific production build under review; this could not be fully confirmed from the indexed `Cargo.toml` contents alone, so likelihood should be evaluated conditional on that feature being enabled in the deployed firmware.

### Recommendation
Never let a value parsed straight from the QR-code payload (`signup_extension`) short-circuit the backend authorization/validation call. `verify_operator_qr_code` should always perform (or cryptographically justify skipping) the `backend::operator_status::request` call, and `LocationData` must always originate from the backend response, never from a hardcoded/default value gated by attacker-controlled QR content.

### Proof of Concept
1. Craft a QR-code string matching `QR_CODE_SIGNUP_EXTENSION` such that `Data::from_signup_extension` sets `signup_extension = true` and `signup_extension_config = Some(...)` (see the test vectors already in the repo, e.g. `"userid:<uuid>:1::0:param::"`) as parsed in [6](#0-5) .
2. Present this QR code to the orb during `scan_operator_qr_code`/`scan_remaining_qr_codes`.
3. Observe that `verify_operator_qr_code` short-circuits at [2](#0-1)  and returns `valid == true` with fabricated `"DEV"` location data, without ever calling the backend to authenticate the operator.

### Citations

**File:** src/plans/mod.rs (L1060-1083)
```rust
        if operator_data.qr_code.signup_extension() || user_qr_code.signup_extension() {
            if user_qr_code.signup_extension() && operator_data.qr_code.signup_extension() {
                if let Some(SignupExtensionConfig { mode, parameters: _ }) = user_qr_code
                    .signup_extension_config
                    .as_ref()
                    .or(operator_data.qr_code.signup_extension_config.as_ref())
                {
                    dd_incr!("main.count.data_acquisition.mode", &format!("mode:{mode:?}"));
                    return Ok(Some(Some((
                        user_qr_code,
                        backend::user_status::UserData::default(),
                        user_qr_code_string,
                    ))));
                }
            }
            orb.ui.qr_scan_unexpected(QrScanSchema::User, QrScanUnexpectedReason::Invalid);
            dd_incr!("main.count.data_acquisition.failure.user_qr_code", "type:invalid_qr");
            tracing::error!(
                "Invalid user QR-code format for data acquisition. User QR-code: \
                 {user_qr_code:?}. Operator QR-code: {:?}",
                operator_data.qr_code
            );
            return Ok(None);
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

**File:** src/plans/qr_scan/user.rs (L166-187)
```rust
#[cfg(feature = "internal-data-acquisition")]
impl SignupMode {
    /// Parse SignupMode enum from string
    fn parse(mode: Option<&str>) -> Option<Self> {
        if let Some(mode) = mode {
            let val = u8::from_str_radix(mode, 16).ok()?;
            let mode = match val {
                0 => Self::Basic,
                1 => Self::PupilContractionExtension,
                2 => Self::FocusSweepExtension,
                3 => Self::MirrorSweepExtension,
                4 => Self::MultiWavelength,
                5 => Self::Overcapture,
                _ => return None,
            };
            tracing::warn!("Parsed signup mode {:?} from QR code - signup flow modified!", mode);
            Some(mode)
        } else {
            None
        }
    }
}
```

**File:** src/plans/qr_scan/user.rs (L276-285)
```rust
        #[test]
        fn test_data_acquisition_mode_param() {
            let text = "userid:12345678-1234-1234-1234-123456789012:1::0:param::";
            let data =
                Data::from_signup_extension(&QR_CODE_SIGNUP_EXTENSION.captures(text).unwrap());
            assert_eq!(data.user_id, "12345678-1234-1234-1234-123456789012");
            assert!(data.signup_extension_config.is_some());
            assert_eq!(data.signup_extension_config.as_ref().unwrap().mode, SignupMode::Basic);
            assert_eq!(data.signup_extension_config.unwrap().parameters, Some("param".to_string()));
        }
```
