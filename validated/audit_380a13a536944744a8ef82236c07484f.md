### Title
Attacker-controlled octal `SignupExtensionConfig.parameters` overrides operator config via `.or()` precedence and panics `focus_sweep::SweepConfiguration::parse_configuration_value` - ([File: src/plans/biometric_capture/focus_sweep.rs])

### Summary
`DebugReport::builder` and `handle_user_qr_code` both resolve the effective `SignupExtensionConfig` with `user_qr_code.signup_extension_config.as_ref().or(operator_data.qr_code.signup_extension_config.as_ref())`, giving the user-presented QR precedence over the operator's when both are present. If the attacker's user QR encodes `mode=focus_sweep` (or `mirror_sweep`) with a multi-digit octal `parameters` value such as `"10"` (parsed as octal 8), `focus_sweep::Plan::from` computes a `u8` configuration value of 8, whose 3-bit binary formatting assertion in `SweepConfiguration::parse_configuration_value` panics.

### Finding Description
`DebugReport::builder` computes the effective extension config as: [1](#0-0) 
using `.or()`, so whenever the user QR carries a `Some(SignupExtensionConfig)`, it wins over the operator's, regardless of what mode/parameters the operator intended. The same precedence is used in `handle_user_qr_code`: [2](#0-1) 
That code path is only reachable when **both** operator and user QR set `signup_extension()==true` (an internal data-acquisition QR format), gated by the `internal-data-acquisition` feature and further gated by `!self.data_acquisition` rejecting such QR codes entirely when the orb is not in data-acquisition mode.

Given the mode was overridden to `FocusSweepExtension`, `biometric_capture()` in `plans/mod.rs` dispatches to `focus_sweep::Plan::from(plan)`: [3](#0-2) 
which parses `parameters` as octal into a `u8`: [4](#0-3) 
`u8::from_str_radix(parameter, 8)` accepts any octal digit string whose *decimal* value fits in `u8` (0-255), e.g. `"10"` → 8, `"20"` → 16, etc. This value is passed unchecked into `SweepConfiguration::new` → `parse_configuration_value`, which asserts the binary representation is exactly 3 characters: [5](#0-4) 
For any parsed value ≥ 8, `format!("{configuration_value:0>3b}")` produces 4+ characters, so `assert_eq!` panics with `"Focus Sweep configuration value needs to be octal (<=3 bit)!"`. The same bug pattern exists identically in `mirror_sweep.rs`.

### Impact Explanation
This is a crash/denial-of-service of the biometric-capture plan whenever the internal-data-acquisition path is exercised, i.e. an operator-crafted crash-prone code path can be unilaterally selected/triggered by an attacker-controlled user QR value that the attacker fully controls (`parameters` string), since the user-QR extension config takes precedence via `.or()` over the operator's config. Impact is limited to plan panic/crash of the signup session (availability), not identity binding, biometric disclosure, or authorization bypass.

### Likelihood Explanation
Exploitability requires: (1) the `internal-data-acquisition` Cargo feature to be compiled in, (2) the orb operator to have explicitly enabled data-acquisition mode (`self.data_acquisition`) — a QR is rejected outright as "invalid" if not in that mode, (3) both operator and user present signup-extension formatted QR codes (the operator QR must also declare `signup_extension()==true`, though its `mode`/`parameters` can differ). This is not a normal production signup flow: `internal-data-acquisition` is an internal/testing feature, and `self.data_acquisition` mode requires deliberate operator/backend enablement, which is outside the "unprivileged attacker with only user-QR control" threat model assumed reachable in ordinary consumer signups. I was unable to fully confirm within the available tool budget whether `internal-data-acquisition` is a default-enabled feature in production release builds or the exact authorization mechanism that flips `self.data_acquisition` to true — this needs further verification (e.g., checking `Cargo.toml` default-features list and `cli.rs`/backend config wiring for `data_acquisition`).

### Recommendation
1. Validate `SignupExtensionConfig.parameters` at QR-parse time (`SignupMode::parse`/regex capture) rather than at `Plan::from`, rejecting any value whose octal parse yields ≥ 8, and return a parse error instead of silently defaulting or panicking later.
2. Replace the `assert_eq!` panic in `parse_configuration_value` with a graceful fallback (e.g. clamp/return `Result`/default to `1`) so malformed configuration values cannot abort the signup process.
3. Reconsider the `.or()` precedence itself: since this is meant to be an operator-authorized data-acquisition mode, the operator-provided config should take precedence over (or be the sole source of truth for) `mode`/`parameters`, with the user QR only supplying identity, not overriding pipeline behavior.

### Proof of Concept
Integration test in `src/plans/biometric_capture/focus_sweep.rs` (with `internal-data-acquisition` feature enabled):
1. Construct `biometric_capture::Plan` with `signup_extension_config = Some(SignupExtensionConfig { mode: SignupMode::FocusSweepExtension, parameters: Some("10".to_string()) })` (simulating the resolved config after `.or()` picked the user QR's value over an operator config of `Basic`).
2. Call `focus_sweep::Plan::from(plan)`.
3. Assert this panics with `"Focus Sweep configuration value needs to be octal (<=3 bit)!"` (or, after the fix, assert no panic and that the resulting configuration defaults gracefully).
4. Separately, add an integration test around `DebugReport::builder` with an operator QR `SignupExtensionConfig{mode: Basic, ..}` and user QR `SignupExtensionConfig{mode: FocusSweepExtension, parameters: Some("10")}`; assert that the effective `combined_signup_extension_config` used downstream matches the operator-authorized value (post-fix), and that no single user-supplied parameter can crash `biometric_capture()`.

### Citations

**File:** src/debug_report.rs (L808-812)
```rust
        let combined_signup_extension_config = user_qr_code
            .signup_extension_config
            .as_ref()
            .or(operator_data.qr_code.signup_extension_config.as_ref())
            .cloned();
```

**File:** src/plans/mod.rs (L1060-1074)
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
```

**File:** src/plans/mod.rs (L1192-1195)
```rust
                qr_scan::user::SignupMode::FocusSweepExtension => {
                    tracing::info!("Focus Sweep extension: activated");
                    biometric_capture::focus_sweep::Plan::from(plan).run(orb).await?
                }
```

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
