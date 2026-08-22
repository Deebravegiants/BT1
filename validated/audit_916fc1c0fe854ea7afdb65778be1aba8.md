### Title
Unvalidated QR-code signup-extension parameter causes `assert_eq!` panic and orb-core crash (DoS) - (File: `src/plans/biometric_capture/overcapture.rs`)

### Summary
The Timeswap report describes `safeName()` reverting when it blindly assumes an external, attacker/third-party-controlled value conforms to an expected format (`string` vs `bytes32`), causing a DoS in a function that must never fail. The analogous root cause exists in orb-core's overcapture signup extension: `Configuration::parse_wavelength_configuration()` assumes a user-supplied QR-code parameter, after a narrow parse step, always decodes to a 3-bit octal value, and enforces that assumption with `assert_eq!` instead of gracefully rejecting the malformed value. A crafted QR code can violate that assumption and panic the process.

### Finding Description
When the `internal-data-acquisition` feature is enabled, a scanned user QR code can request the "Overcapture" signup extension mode with an attacker-controlled `parameters` string, per the QR schema parsed in `Data::from_signup_extension`/`SignupMode::parse`: [1](#0-0) [2](#0-1) 

That untrusted `parameters` string is converted into `wavelength_parameter: u8` via `parse_u8_octal`, which only guards against outright parse failure (falling back to a default), not against in-range values that are semantically invalid for the downstream assumption: [3](#0-2) [4](#0-3) 

`Configuration::new`/`parse_wavelength_configuration` then formats the value as a 3-character binary string and asserts the result is exactly 3 characters — but any octal-parseable string decoding to a decimal value ≥ 8 (e.g. the octal digit string `"10"`, which decodes to `8`) produces a 4+ character binary representation, tripping the `assert_eq!` and panicking: [5](#0-4) 

This mirrors the root cause in the External Report: code assumes an external input always conforms to a specific, narrower format ("3-bit octal" here vs. "string" for `safeName()`), and instead of handling the out-of-range case, uses an operation that aborts (`assert_eq!` panic here vs. `abi.decode()` revert there).

### Impact Explanation
A panic in orb-core's plan-execution task, triggered while processing untrusted, unauthenticated data from a scanned QR code, crashes/DoSes the signup flow analogous to how a reverting `name()` breaks ERC20 compliance for the caller. Depending on process supervision, this can abort an in-progress signup and force operator intervention, denying service to legitimate users attempting to sign up, similar in class/severity to the referenced finding (a DoS caused by an unguarded assumption about external input format).

### Likelihood Explanation
The trigger requires only presenting a QR code matching the `QR_CODE_SIGNUP_EXTENSION` regex with mode `5` (Overcapture) and a wavelength parameter that is valid octal-digit text but decodes to a value ≥ 8 (e.g., `"10"`), which is trivial for anyone able to present a QR code to the scanner. It is gated behind the `internal-data-acquisition` build feature, so likelihood depends on that feature being enabled in the deployed build; on such builds it is fully reachable by an unprivileged party presenting a crafted QR code, with no signature/authentication requirement on the extension parameters.

### Recommendation
Replace the `assert_eq!` panic in `Configuration::parse_wavelength_configuration` with a graceful validation/fallback path (e.g., reject/clamp values outside `0..=7` and fall back to the default configuration or reject the QR code), mirroring how `parse_u8_octal`/`parse_duration` already fall back to defaults on outright parse errors. More generally, any parsing of externally supplied QR-code parameters that feeds into logic with format assumptions should validate the full value range before use rather than relying on panicking assertions.

### Proof of Concept
1. Enable the `internal-data-acquisition` feature build.
2. Present a QR code with contents matching `QR_CODE_SIGNUP_EXTENSION`, e.g. `userid:12345678-1234-1234-1234-123456789012:1::5:10::` (mode `5` = Overcapture, parameter `"10"`).
3. `SignupExtensionConfig { mode: Overcapture, parameters: Some("10") }` is produced by `Data::from_signup_extension`.
4. During biometric capture, `overcapture::Plan::from(biometric_capture::Plan)` calls `parse_u8_octal("10", 1)` → `u8::from_str_radix("10", 8)` → `Ok(8)`.
5. `Configuration::new(8, ...)` → `parse_wavelength_configuration(8)` → `format!("{8:0>3b}")` = `"1000"` (4 chars) → `assert_eq!(4, 3, ...)` panics, crashing the signup task.

### Citations

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

**File:** src/plans/biometric_capture/overcapture.rs (L107-132)
```rust
impl From<biometric_capture::Plan> for Plan {
    fn from(biometric_capture: biometric_capture::Plan) -> Self {
        let config = biometric_capture
            .signup_extension_config
            .as_ref()
            .and_then(|config| config.parameters.as_ref());
        let (wavelength_parameter, duration_parameter) =
            config.map_or((1, Duration::from_millis(DEFAULT_OVERCAPTURE_DURATION)), |parameters| {
                parameters.split_once(':').map_or(
                    (
                        parse_u8_octal(parameters, 1),
                        Duration::from_millis(DEFAULT_OVERCAPTURE_DURATION),
                    ),
                    |(wavelength, duration)| {
                        (
                            parse_u8_octal(wavelength, 1),
                            parse_duration(duration, DEFAULT_OVERCAPTURE_DURATION),
                        )
                    },
                )
            });
        let configuration = Configuration::new(wavelength_parameter, duration_parameter);
        let report = Report { overcapture_configuration: configuration.clone() };
        Self { biometric_capture, state: State::NoSharpIris, configuration, report }
    }
}
```

**File:** src/plans/biometric_capture/overcapture.rs (L214-220)
```rust
    fn parse_wavelength_configuration(configuration_value: u8) -> VecDeque<IrLed> {
        let binary_repr = format!("{configuration_value:0>3b}");
        assert_eq!(
            binary_repr.chars().count(),
            3,
            "Overcapture wavelength parameter needs to be octal (<=3 bit)!"
        );
```

**File:** src/plans/biometric_capture/overcapture.rs (L231-233)
```rust
fn parse_u8_octal(src: &str, default: u8) -> u8 {
    u8::from_str_radix(src, 8).unwrap_or(default)
}
```
