### Title
Unbounded `overcapture_duration` from unvalidated QR `parameters` string causes indefinite excessive biometric frame capture - ([File: src/plans/biometric_capture/overcapture.rs])

### Finding Description
When the `internal-data-acquisition` feature is enabled, an attacker-controlled QR code is parsed by `qr_scan::user::Data::from_signup_extension` (`src/plans/qr_scan/user.rs:144-157`), which extracts a free-form `parameters` string matched only against the very permissive regex `[a-z0-9:]+` (`src/plans/qr_scan/user.rs:53`), with no length or value bound. This string flows unchanged into `biometric_capture::Plan::signup_extension_config` and then into `overcapture::Plan::from` (`src/plans/biometric_capture/overcapture.rs:107-131`), where it is split on the first `:` and the second half is passed to `parse_duration`:

```rust
fn parse_duration(src: &str, default: u64) -> Duration {
    Duration::from_millis(src.parse::<u64>().unwrap_or(default))
}
```
(`src/plans/biometric_capture/overcapture.rs:235-237`)

There is no upper-bound clamp on the parsed value — any numeric string up to `u64::MAX` (e.g. `"18446744073709551615"`) parses successfully and produces a `Duration` of roughly 584 million years, assigned to `Configuration.overcapture_duration` (`overcapture.rs:66-70`, `202-207`). This duration is only checked for a *lower* bound implicitly via `poll_extra`:

```rust
State::Overcapturing { start_time } => {
    if start_time.elapsed() > self.configuration.overcapture_duration {
        ...
        Ok(BrokerFlow::Break)
    } else {
        Ok(BrokerFlow::Continue)
    }
}
```
(`overcapture.rs:94-102`)

With an effectively infinite `overcapture_duration`, this condition never becomes true, so `perform_overcapture` (`overcapture.rs:156-183`) never returns control after `orb.run(self).await?` — the loop in `Plan::run` (`overcapture.rs:136-154`) stays inside `perform_overcapture` indefinitely while `orb.ir_eye_save_fps_override = Some(f32::INFINITY)`, `orb.ir_face_save_fps_override = Some(f32::INFINITY)`, and `orb.thermal_save_fps_override = Some(f32::INFINITY)` remain active (`overcapture.rs:166-168`), continuously persisting IR eye/face/thermal frames at up to `CAPTURE_FPS = 60` (`overcapture.rs:30`). No other layer in `src/plans/biometric_capture/mod.rs` enforces a hard ceiling on capture duration or frame count for this extension path. The `parse_u8_octal` wavelength parsing (`overcapture.rs:231-233`) is separately bounded by the octal `u8::from_str_radix` combined with the `assert_eq!` in `Configuration::parse_wavelength_configuration` (`overcapture.rs:214-220`), so the primary unbounded vector is the duration field, not the wavelength field.

### Impact Explanation
An attacker who can present such a QR code (precondition: `internal-data-acquisition` feature compiled in and QR-parsing path reachable) can force the orb to remain in an effectively unbounded overcapture state for their own signup session, saving every IR eye/face/thermal frame at 60 FPS with no time or frame-count ceiling. This breaches the "bounded capture volume per signup" containment invariant — it does not grant unauthorized signup or cross-user data exposure, but causes gross over-retention/over-upload of the presenting user's own biometric imagery well beyond intended policy limits, and can also wedge the signup flow / consume device storage and processing resources for the extension's lifetime.

### Likelihood Explanation
The attack requires the `internal-data-acquisition` Cargo feature to be enabled (confirmed present in `Cargo.toml`) and the ability to present a crafted QR code matching `QR_CODE_SIGNUP_EXTENSION` with mode `5` (`Overcapture`, per `SignupMode::parse` in `src/plans/qr_scan/user.rs:169-186`) and a `parameters` field like `7:18446744073709551615`. Given this precondition is met, exploitation is trivial and fully deterministic — no race conditions, timing, or privileged access needed; it's a straightforward missing-bound parsing bug in production Rust code (not a test-only path).

### Recommendation
Clamp the parsed duration to a hard-coded maximum (e.g. a small multiple of `DEFAULT_OVERCAPTURE_DURATION`) in `parse_duration`, such as `Duration::from_millis(src.parse::<u64>().unwrap_or(default).min(MAX_OVERCAPTURE_DURATION_MS))`, and add an analogous explicit maximum-frame-count/time guard inside `Plan::run`/`perform_overcapture` independent of the parsed configuration, so a malformed or adversarial `parameters` string cannot extend capture beyond a fixed policy bound regardless of parsing outcome.

### Proof of Concept
Add a unit test in `src/plans/biometric_capture/overcapture.rs` (or a fuzz target) that constructs a `biometric_capture::Plan` with `signup_extension_config.parameters = Some("7:18446744073709551615".to_string())`, invokes `overcapture::Plan::from`, and asserts:
```rust
assert!(plan.configuration.overcapture_duration <= Duration::from_millis(MAX_OVERCAPTURE_DURATION_MS));
```
This assertion currently fails because `parse_duration` has no upper clamp, demonstrating the unbounded duration is accepted; a fuzz harness over arbitrary `parameters` strings (varying digit counts before/after `:`) should likewise assert the resulting `overcapture_duration` and any downstream frame counter never exceed the intended hard maximum. [1](#0-0) [2](#0-1) [3](#0-2) [4](#0-3) [5](#0-4) [6](#0-5)

### Citations

**File:** src/plans/biometric_capture/overcapture.rs (L91-104)
```rust
    fn poll_extra(&mut self, orb: &mut Orb, cx: &mut Context<'_>) -> Result<BrokerFlow> {
        match self.state {
            State::NoSharpIris => self.biometric_capture.poll_extra(orb, cx),
            State::Overcapturing { start_time } => {
                if start_time.elapsed() > self.configuration.overcapture_duration {
                    tracing::info!("Overcapture extension: Finished capture");
                    self.state = State::NoSharpIris;
                    Ok(BrokerFlow::Break)
                } else {
                    Ok(BrokerFlow::Continue)
                }
            }
        }
    }
```

**File:** src/plans/biometric_capture/overcapture.rs (L107-131)
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
```

**File:** src/plans/biometric_capture/overcapture.rs (L136-183)
```rust
    pub async fn run(mut self, orb: &mut Orb) -> Result<Output> {
        self.biometric_capture.run_pre(orb).await?;
        self.reset_extension();
        // NOTE: Disabling the distance agent to prevent signup UX sound loops from interfering
        // with the "start" and "end" sounds
        orb.disable_distance();
        loop {
            orb.run(&mut self).await?;
            sleep(Duration::from_millis(1000)).await;
            while !self.extension_finished(orb).await? {
                self.perform_overcapture(orb).await?;
            }
            if self.biometric_capture.run_check(orb).await? {
                break;
            }
        }
        orb.enable_distance()?;
        self.biometric_capture.run_post(orb, Some(ExtensionReport::Overcapture(self.report))).await
    }

    async fn perform_overcapture(&mut self, orb: &mut Orb) -> Result<()> {
        tracing::info!("Overcapture extension: Beginning capture");
        self.state = State::Overcapturing { start_time: Instant::now() };

        orb.main_mcu.send(mcu::main::Input::FrameRate(CAPTURE_FPS)).await?;
        orb.disable_ir_net();
        orb.disable_ir_auto_focus();
        orb.disable_mirror();
        orb.disable_eye_tracker();
        orb.disable_eye_pid_controller();
        orb.ir_eye_save_fps_override = Some(f32::INFINITY);
        orb.ir_face_save_fps_override = Some(f32::INFINITY);
        orb.thermal_save_fps_override = Some(f32::INFINITY);

        orb.run(self).await?;

        orb.main_mcu.send(mcu::main::Input::FrameRate(IR_CAMERA_FRAME_RATE)).await?;
        orb.enable_ir_net().await?;
        orb.enable_ir_auto_focus()?;
        orb.enable_mirror()?;
        orb.enable_eye_tracker()?;
        orb.enable_eye_pid_controller()?;
        orb.ir_eye_save_fps_override = None;
        orb.ir_face_save_fps_override = None;
        orb.thermal_save_fps_override = None;

        Ok(())
    }
```

**File:** src/plans/biometric_capture/overcapture.rs (L231-237)
```rust
fn parse_u8_octal(src: &str, default: u8) -> u8 {
    u8::from_str_radix(src, 8).unwrap_or(default)
}

fn parse_duration(src: &str, default: u64) -> Duration {
    Duration::from_millis(src.parse::<u64>().unwrap_or(default))
}
```

**File:** src/plans/qr_scan/user.rs (L38-60)
```rust
#[cfg(any(feature = "internal-data-acquisition", test))]
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

**File:** src/plans/qr_scan/user.rs (L142-187)
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

    /// Returns true if qr code specifies signup extension mode.
    #[must_use]
    pub fn signup_extension(&self) -> bool {
        self.signup_extension
    }
}

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
