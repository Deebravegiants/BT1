### Title
Attacker-controlled QR `signup_extension_config.parameters` causes panic in `SweepConfiguration::parse_configuration_value` via octal values >7 - ([File: src/plans/biometric_capture/focus_sweep.rs])

### Finding Description
`Plan::from<biometric_capture::Plan>` parses the QR-derived `signup_extension_config.parameters` string with `u8::from_str_radix(parameter, 8)` [1](#0-0) . Octal parsing accepts any string of digits `0-7` and returns the decimal value of that octal number — e.g. the string `"10"` is valid octal input and parses successfully to `u8` value `8`, `"11"` to `9`, up through `"377"` to `255`. None of these calls fail, so `.ok()` never falls through to the `unwrap_or(1)` default for these inputs.

The resulting `configuration_value` is passed into `SweepConfiguration::new`, which calls `SweepConfiguration::parse_configuration_value` [2](#0-1) . That function formats the value as a zero-padded 3-bit binary string and asserts its length is exactly 3: [3](#0-2) 
For any `configuration_value > 7`, `format!("{configuration_value:0>3b}")` produces 4 or more binary digits (e.g. `8` → `"1000"`), so `binary_repr.chars().count() != 3`, and the `assert_eq!` panics.

This function is invoked unconditionally during construction of the focus-sweep extension plan (`From<biometric_capture::Plan> for Plan`), which is reachable purely from attacker-supplied QR content parsed during the attacker's own signup session — no operator or privileged access is required. The code comment at line 158-159 even acknowledges this parsing should ideally happen earlier ("Move parsing of configuration flag to QR code scanning phase -> Handle/Fail early"), confirming no upstream validation currently rejects out-of-range octal strings.

### Impact Explanation
This is a reachable panic (`assert_eq!` failure) triggered entirely by attacker-controlled QR data during the attacker's own signup flow. A panic in this async task/plan will abort/crash the orb-core biometric capture pipeline for that signup session, resulting in denial of service of the signup process on the orb (and potentially the whole orb-core process depending on panic handling/unwind boundaries). This matches a signup-availability / DoS impact category rather than data disclosure or identity-binding compromise.

### Likelihood Explanation
Trivially reproducible: any unprivileged attacker can construct a QR code whose `signup_extension_config.parameters` field is an octal-digit string (using only digits 0-7) representing a value greater than 7 (e.g. `"10"`, `"77"`, `"377"`). No special privileges, tokens, or backend cooperation are needed — the attacker just needs to present the QR code to initiate their own signup with the focus-sweep extension selected. This is 100% deterministic given such input.

### Recommendation
Validate `configuration_value` is in `0..=7` before constructing `SweepConfiguration`, and reject/clamp/default invalid values instead of asserting. Specifically, replace the `assert_eq!` panic in `parse_configuration_value` with a fallible check (e.g., return `Result` or clamp to a safe default such as `1`), and/or validate the parsed parameter range immediately after `u8::from_str_radix` in the `From` impl before it reaches `SweepConfiguration::new`.

### Proof of Concept
Unit test in `focus_sweep.rs`:
```rust
#[test]
fn test_configuration_value_out_of_octal_range_does_not_panic() {
    // "10" is valid octal syntax but decodes to 8, which is > 7
    let value = u8::from_str_radix("10", 8).unwrap();
    assert_eq!(value, 8);
    // Currently this panics via assert_eq! inside parse_configuration_value
    let _ = SweepConfiguration::new(value); // expect: no panic after fix
}
```
Expected (pre-fix): test panics with `"Focus Sweep configuration value needs to be octal (<=3 bit)!"`. Expected (post-fix): function returns a safe default/wavelength set or an explicit error instead of panicking.

### Citations

**File:** src/plans/biometric_capture/focus_sweep.rs (L160-167)
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

**File:** src/plans/biometric_capture/focus_sweep.rs (L294-300)
```rust
impl SweepConfiguration {
    fn new(configuration_value: u8) -> Self {
        Self {
            configuration_value,
            sweep_wavelengths: SweepConfiguration::parse_configuration_value(configuration_value),
        }
    }
```

**File:** src/plans/biometric_capture/focus_sweep.rs (L307-313)
```rust
    fn parse_configuration_value(configuration_value: u8) -> VecDeque<IrLed> {
        let binary_repr = format!("{configuration_value:0>3b}");
        assert_eq!(
            binary_repr.chars().count(),
            3,
            "Focus Sweep configuration value needs to be octal (<=3 bit)!"
        );
```
