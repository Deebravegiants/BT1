### Title
Attacker-controlled QR `parameters` octal value ≥8 causes assertion panic in `SweepConfiguration::parse_configuration_value` - ([File: src/plans/biometric_capture/mirror_sweep.rs])

### Summary
`Plan::from` for the mirror-sweep extension parses the QR-supplied `parameters` string as an octal `u8` via `u8::from_str_radix(parameter, 8)`, without validating that the resulting value fits in 3 bits (0–7). Because the QR regex allows the parameter to be any octal-digit string up to `u8::MAX` in value (e.g. `"10"`, `"11"`, ... `"377"` octal = 8..255 decimal), a value ≥ 8 reaches `SweepConfiguration::parse_configuration_value`, whose `assert_eq!(binary_repr.chars().count(), 3, ...)` panics because the binary representation of values ≥8 has more than 3 digits.

### Finding Description
The reachable path is:
1. Attacker presents a QR code matching `QR_CODE_SIGNUP_EXTENSION` regex in `src/plans/qr_scan/user.rs` [1](#0-0) , setting `mode` to the hex value `3` (`SignupMode::MirrorSweepExtension`, parsed via `u8::from_str_radix(mode, 16)` in `SignupMode::parse`) [2](#0-1) , and `parameters` to a multi-digit octal-digit string such as `"10"` (decimal digits, valid under `[a-z0-9:]+`).
2. `Data::from_signup_extension` stores this raw string unchecked into `SignupExtensionConfig.parameters` [3](#0-2) .
3. When the biometric capture plan is converted to the mirror-sweep plan, `Plan::from` calls `u8::from_str_radix(parameter, 8).ok()` [4](#0-3) . For `"10"` this successfully parses to `8u8` (valid, in-range `u8`, so `from_str_radix` does **not** error/overflow).
4. `SweepConfiguration::new(8)` calls `parse_configuration_value(8)`, which formats `8` as `format!("{:0>3b}", 8)` = `"1000"` (4 characters) and then panics on `assert_eq!(binary_repr.chars().count(), 3, "Mirror Sweep configuration value needs to be octal (<=3 bit)!")` [5](#0-4) .

No validation exists between the QR regex capture and this assertion that restricts the parsed value to the 0–7 range expected by the 3-bit wavelength LUT (`WAVELENGTH_LUT`) [6](#0-5) . The `reset()` path also re-invokes `parse_configuration_value` on the same stored `configuration_value` between eyes/sessions of a signup [7](#0-6) , but the panic already occurs at construction time in `Plan::from`, before any capture occurs, so it aborts the current signup run.

Regarding the fuzz corpus described in the question: strings that are not valid octal digits (contain letters, `8`, `9`, or `:`) will fail `from_str_radix(_, 8)` and safely fall back to `unwrap_or(1)` — this path is not exploitable. The exploitable subset is specifically octal-only digit strings (chars `0`-`7`) whose decimal value as octal is 8–255 (e.g., `"10"`–`"377"`), which are valid `u8` parses but violate the implicit "must fit in 3 bits" precondition assumed by `parse_configuration_value`.

### Impact Explanation
This is a crash/panic (Denial of Service) reachable purely from a presented QR code during the signup flow, without any special privileges — matches the "attacker-controlled DoS/panic" impact category. Depending on how panics are handled by the orb process supervisor, this could abort/restart the running signup process; because `Report`/`SweepConfiguration` in the mirror-sweep plan is constructed before the panic and per-plan state isn't yet fully committed anywhere shared, the primary confirmed impact is a crash of the current signup rather than a demonstrated persistent state-bleed into a subsequent session — that broader claim in the question (partially-initialized shared Orb/report state carried into next session) is not directly substantiated by the code reviewed; it would require further investigation of the process supervisor/restart behavior, which is outside what's visible in this file.

### Likelihood Explanation
This requires: (a) the orb built with the `internal-data-acquisition` feature enabled (this code and the `QR_CODE_SIGNUP_EXTENSION` regex are gated behind `#[cfg(feature = "internal-data-acquisition")]` in `src/plans/qr_scan/user.rs`), and (b) the attacker being able to present a signup-extension-formatted QR code that the orb accepts as a signup-extension code. Given those preconditions, the exploit is fully deterministic and repeatable — any octal-digit `parameters` string with value ≥ 8 (up to 255, i.e., `"10"` through `"377"`) reliably triggers the panic in `Plan::from`.

### Recommendation
In `src/plans/biometric_capture/mirror_sweep.rs`, validate the parsed configuration value to the range 0–7 before constructing `SweepConfiguration`, e.g. replace `.and_then(|parameter| u8::from_str_radix(parameter, 8).ok())` with a parse-then-range-check (`.filter(|v| *v <= 7)`) and fall back to the default (`1`) otherwise, removing the panicking `assert_eq!` in `parse_configuration_value` in favor of returning a `Result`/graceful fallback so that no attacker-controlled QR value can crash the process.

### Proof of Concept
```rust
// tests placed in src/plans/biometric_capture/mirror_sweep.rs test module
// (or an integration test invoking the qr_scan -> biometric_capture -> mirror_sweep pipeline)

#[test]
#[should_panic(expected = "Mirror Sweep configuration value needs to be octal (<=3 bit)!")]
fn parameters_octal_overflow_panics() {
    // "10" is valid under regex class [a-z0-9:]+ and parses successfully
    // via u8::from_str_radix("10", 8) == 8u8, but 8 has a 4-bit binary
    // representation, triggering the assert_eq! panic.
    let value = u8::from_str_radix("10", 8).unwrap();
    let _ = crate::plans::biometric_capture::mirror_sweep::SweepConfiguration::new(value);
}

// Fuzz target (proof-of-concept sketch):
// for each candidate string s in corpus (chars limited to '0'..='7', arbitrary length):
//     if let Ok(v) = u8::from_str_radix(&s, 8) {
//         // any v in 8..=255 will panic when fed into parse_configuration_value
//         assert!(std::panic::catch_unwind(|| SweepConfiguration::new(v)).is_ok(),
//                 "panic triggered by parameters = {s:?} -> value {v}");
//     }
```
Expected result: the test panics/fuzzer finds a crash for any octal-digit `parameters` string whose value is ≥ 8, confirming the unchecked-range assertion is reachable from attacker-controlled QR input.

### Citations

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

**File:** src/plans/qr_scan/user.rs (L144-157)
```rust
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

**File:** src/plans/qr_scan/user.rs (L169-186)
```rust
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
```

**File:** src/plans/biometric_capture/mirror_sweep.rs (L45-47)
```rust
/// Lookup table for mapping 3-bit configuration value to IR LED
/// configurations to use for extension. Order maps to digit positions.
pub const WAVELENGTH_LUT: [IrLed; 3] = [IrLed::L740, IrLed::L940, IrLed::L850];
```

**File:** src/plans/biometric_capture/mirror_sweep.rs (L170-177)
```rust
        let configuration = SweepConfiguration::new(
            biometric_capture
                .signup_extension_config
                .as_ref()
                .and_then(|config| config.parameters.as_ref())
                .and_then(|parameter| u8::from_str_radix(parameter, 8).ok())
                .unwrap_or(1),
        );
```

**File:** src/plans/biometric_capture/mirror_sweep.rs (L327-330)
```rust
    fn reset(&mut self) {
        self.sweep_wavelengths =
            SweepConfiguration::parse_configuration_value(self.configuration_value);
    }
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
