### Title
Unhandled parameter parsing assumption in `SweepConfiguration::parse_configuration_value`/`Configuration::parse_wavelength_configuration` causes signup process panic (DoS) - (File: `src/plans/biometric_capture/mirror_sweep.rs`, `src/plans/biometric_capture/focus_sweep.rs`, `src/plans/biometric_capture/overcapture.rs`)

### Summary
Similar to the `safeSymbol()` bug, where the code assumed a fixed return format (`string`) from untrusted external input and `abi.decode()` panicked/reverted when that assumption was violated, the orb-core signup-extension configuration parser assumes a QR-code-supplied parameter always decodes to a value representable in exactly 3 bits, and hard-panics via `assert_eq!` when that assumption is violated.

### Finding Description
When a user/operator scans a QR code that enables a `SignupExtension` (`internal-data-acquisition` feature), the `parameters` field is taken verbatim from the QR code text and parsed with `u8::from_str_radix(parameter, 8)` [1](#0-0) . This call only validates that the string consists of valid octal digits — it does not bound the resulting numeric value to 3 bits (0–7). A two-digit octal string such as `"10"` parses successfully to `u8` value `8`.

That value is then fed into `parse_configuration_value`, which formats it as a binary string padded to a *minimum* width of 3 and asserts the resulting string is exactly 3 characters long: [2](#0-1) 

Because `format!("{:0>3b}", 8)` produces `"1000"` (4 characters, since `{:0>3b}` only pads up to a *minimum* width and does not truncate), the `assert_eq!` fails and the process panics. The identical pattern exists in `Configuration::parse_wavelength_configuration` in `overcapture.rs` [3](#0-2) , fed from `parse_u8_octal` on attacker-controlled QR text [4](#0-3) .

The root cause mirrors the report: the parser assumes the decoded value will always fit the expected shape (3-bit octal digit ↔ string return), and when a malformed/oversized value is supplied, the code fails with a hard, unhandled panic instead of validating/rejecting gracefully — exactly analogous to `abi.decode()` reverting instead of tolerating unexpected return data.

The QR-code text reaches this code through the ordinary, unauthenticated `qr_scan::user::Data::try_parse` flow via the `QR_CODE_SIGNUP_EXTENSION` regex, which explicitly allows multi-character parameter strings (`[a-z0-9:]+`) [5](#0-4) , and is only lightly regex-validated before being handed to `SignupMode::parse`/`from_signup_extension`, with no bounds-check on the resulting octal-decoded configuration byte [6](#0-5) .

### Impact Explanation
A `panic!`/failed `assert_eq!` in the orb-core process during signup causes the process to crash/abort, denying service to the orb for that signup session (and potentially any in-progress state), consistent with a DoS analog of the referenced `safeSymbol()` revert. Because this code path is only compiled with the `internal-data-acquisition` feature, the practical impact is limited to builds/deployments where that feature is enabled; standard production builds without that feature are not affected by this exact code path.

### Likelihood Explanation
Reachability requires: (1) the `internal-data-acquisition` feature enabled at compile time, (2) an operator QR code that itself carries a signup-extension config, and (3) a user (or attacker with a crafted QR code) supplying a `mirror_sweep`/`focus_sweep`/`overcapture` mode with a parameter string that decodes (via `u8::from_str_radix(_, 8)`) to a value ≥ 8. Given the regex permits multi-digit octal parameter strings and there is no explicit range check before the `assert_eq!`, triggering the panic is straightforward for anyone who can present a QR code to the orb in this configuration. Whether `internal-data-acquisition` is compiled into field/production units could not be confirmed from the available index and would need to be verified in an actual build configuration.

### Recommendation
Replace the `assert_eq!`-based invariant checks with graceful validation that clamps or rejects out-of-range configuration values (e.g., mask the parsed value to 3 bits, or return an error/`None` from `SignupMode::parse`/parameter parsing when the octal value exceeds the expected range), so malformed or oversized signup-extension parameters from QR codes cannot crash the orb-core process. Apply the same masking/validation in `mirror_sweep.rs`, `focus_sweep.rs`, and `overcapture.rs`.

### Proof of Concept
1. Enable the `internal-data-acquisition` feature.
2. Present an operator QR code enabling a signup extension, then a user QR code of the form `userid:<uuid>:1::3:10::` (mode `3` = `MirrorSweepExtension`, parameter `"10"`).
3. `SignupMode::parse` accepts mode `3`; `parameters` becomes `Some("10")`.
4. In `mirror_sweep::Plan::from`, `u8::from_str_radix("10", 8)` returns `Ok(8)`.
5. `SweepConfiguration::new(8)` calls `parse_configuration_value(8)`, producing `format!("{:0>3b}", 8) == "1000"` (4 chars).
6. `assert_eq!(4, 3, "Mirror Sweep configuration value needs to be octal (<=3 bit)!")` panics, crashing the orb-core process during signup.

### Citations

**File:** src/plans/biometric_capture/mirror_sweep.rs (L160-167)
```rust
        } else {
            Ok(BrokerFlow::Continue)
        }
    }
}

impl From<biometric_capture::Plan> for Plan {
    fn from(biometric_capture: biometric_capture::Plan) -> Self {
```

**File:** src/plans/biometric_capture/mirror_sweep.rs (L332-338)
```rust
    fn parse_configuration_value(configuration_value: u8) -> VecDeque<IrLed> {
        let binary_repr = format!("{configuration_value:0>3b}");
        assert_eq!(
            binary_repr.chars().count(),
            3,
            "Mirror Sweep configuration value needs to be octal (<=3 bit)!"
        );
```

**File:** src/plans/biometric_capture/overcapture.rs (L107-127)
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

**File:** src/plans/qr_scan/user.rs (L39-60)
```rust
static QR_CODE_SIGNUP_EXTENSION: Lazy<Regex> = Lazy::new(|| {
    Regex::new(
        r"(?x)
            ^
            userid
            :
            (?P<user_id>
                [a-z0-9_-]+
            )
            :
            (?P<data_policy>\d{1,10})
            (::
                (?P<mode>[a-z0-9]+)
                (:
                    (?P<parameters>[a-z0-9:]+)
                )?
            )?
            ::$
        ",
    )
    .expect("bad regex")
});
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
