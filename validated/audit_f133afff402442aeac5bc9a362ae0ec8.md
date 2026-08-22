### Title
Pupil-contraction liveness extension never breaks out of `NoSharpIris`, allowing the outer `Plan::run` loop to exit the biometric-capture objective based solely on `biometric_capture::Plan::poll_extra`, bypassing the pupil-contraction ramp entirely - ([File: src/plans/biometric_capture/pupil_contraction.rs])

### Summary
`pupil_contraction::Plan::run` drives the outer loop purely through `orb.run(&mut self)` plus `self.biometric_capture.run_check(orb).await?`, and the only way for the pupil-contraction ramp (`RampingUp`/`Waiting`) to ever start is for `handle_ir_net` to observe `self.biometric_capture.handle_ir_net(...)` return `BrokerFlow::Break`. However, `biometric_capture::Plan::handle_ir_net` (in `src/plans/biometric_capture/mod.rs`) unconditionally returns `Ok(BrokerFlow::Continue)` — it never returns `Break`. The actual "objective satisfied" signal was moved into `biometric_capture::Plan::poll_extra`, which is what `orb.run` actually breaks on via `OrbPlan::poll_extra` delegation. Because `pupil_contraction`'s state machine never leaves `State::NoSharpIris`, the liveness ramp/wait sequence never executes for any eye, and the outer loop advances/completes objectives (including the final "both eyes captured" completion) purely on `biometric_capture`'s own completion criteria.

### Finding Description
- `orb.run(&mut self)` in `pupil_contraction::Plan::run` (`src/plans/biometric_capture/pupil_contraction.rs:147-156`) polls the composed plan; `OrbPlan::poll_extra` for `pupil_contraction::Plan` (line 129-131) simply delegates to `self.biometric_capture.poll_extra(orb, cx)`, with no dependency on `self.state`.
- `biometric_capture::Plan::poll_extra` (`src/plans/biometric_capture/mod.rs:343-378`) returns `BrokerFlow::Break` once the current eye's `rgb`/`ir` slots are filled (and, for the last objective, once `self_custody_candidate_rgb` is also filled) — entirely independent of `pupil_contraction::State`. [1](#0-0) 
- The only mechanism by which `pupil_contraction::Plan` is supposed to intercept this and force a liveness ramp is in its own `handle_ir_net` (`State::NoSharpIris` branch), which checks `if let BrokerFlow::Break = self.biometric_capture.handle_ir_net(orb, output, frame)?`. [2](#0-1) 
- But `biometric_capture::Plan::handle_ir_net` never returns `Break` — it always falls through to `Ok(BrokerFlow::Continue)` at the end of the function regardless of whether a valid capture was recorded. [3](#0-2) 
- Consequently `self.state` in `pupil_contraction::Plan` can never transition out of `State::NoSharpIris` into `RampingUp`/`Waiting`, meaning the LED ramp, auto-exposure/auto-focus/eye-tracker disabling, and the `Break` at the end of `State::Waiting` (which is the intended per-eye liveness gate) are dead code paths that never execute. [4](#0-3) 
- Instead, `orb.run` in `pupil_contraction::Plan::run` breaks purely because `biometric_capture.poll_extra` fires (per-eye objective completion / final self-custody completion), and `run_check` then advances to the next objective or completes the whole biometric-capture phase — all without ever exercising the pupil-contraction liveness sequence for either eye.

This differs slightly from the race condition framed in the question (fast dual-eye capture racing a slow first-eye pupil ramp): the actual root cause is structural, not a timing race — the ramp logically can never start at all under the current code, for either eye, in any timing scenario, because the trigger condition (`Break` from `handle_ir_net`) is unreachable given `biometric_capture::Plan::handle_ir_net`'s current implementation.

### Impact Explanation
The pupil-contraction liveness check is intended to enforce that the user's pupil actually contracts under a controlled light ramp before an eye capture is accepted as part of a live signup — this is a biometric liveness/anti-presentation-attack control. Because the extension's activation trigger is broken, this liveness gate is never enforced for any signup that uses the pupil-contraction extension, for either eye. This allows a non-live presentation (e.g., a high-quality static image or replay of an iris, if it can otherwise satisfy IR-Net/RGB-Net score thresholds) to pass biometric capture without ever being subjected to the pupil-contraction liveness test, undermining the anti-spoofing/liveness control this extension exists to provide. This maps to a liveness/fraud-check bypass class of impact against Worldcoin/Orb signup integrity.

### Likelihood Explanation
No special timing or race is required — this triggers deterministically on every signup that selects the `pupil_contraction` signup extension, because `biometric_capture::Plan::handle_ir_net` never returns `Break` under any circumstance in the current code. It requires only that an attacker (or any user) triggers a signup flow where `qr_scan::user::SignupExtensionConfig` selects the pupil-contraction extension (see `src/plans/qr_scan/user.rs` and `src/plans/mod.rs` for how extension selection is wired to the QR code/session config, which are reachable from an attacker-controlled QR code per the stated threat model). No privileged access is needed.

### Recommendation
Fix the trigger condition in `pupil_contraction::Plan::handle_ir_net`'s `State::NoSharpIris` branch so it correctly detects "objective ready to complete" using the same criteria as `biometric_capture::Plan::poll_extra` (i.e., check that the current target eye's `rgb`/`ir` capture slots are populated, mirroring the logic now living in `poll_extra`), rather than relying on `handle_ir_net`'s return value which is always `Continue`. Alternatively, refactor `biometric_capture::Plan` to expose an explicit "objective satisfied" predicate that both `poll_extra` and extension plans like `pupil_contraction` can consult, and gate `poll_extra`'s `Break` in the composed extension (or in `biometric_capture` itself when wrapped by an extension) on the extension's liveness state so the outer loop cannot exit an eye's objective before `State::Waiting` completes and returns `Break`.

### Proof of Concept
Integration/unit test plan:
1. Construct `biometric_capture::Plan` with two objectives (left/right eye), wrap it into `pupil_contraction::Plan` via `From<biometric_capture::Plan>`.
2. Drive `handle_ir_net` with a sequence of `ir_net::Output::Estimate` frames for the current target eye whose `score` exceeds `IRIS_SCORE_MIN` and whose frame mean is within `IRIS_BRIGHTNESS_RANGE`, plus `valid_capture_after <= Instant::now()`, so that `biometric_capture`'s internal `left_ir`/`right_ir` slot gets populated.
3. Assert that after this, `pupil_contraction::Plan`'s internal `state` remains `State::NoSharpIris` (never transitions to `RampingUp`), proving the `if let BrokerFlow::Break = self.biometric_capture.handle_ir_net(...)` branch is unreachable.
4. Feed corresponding `rgb_net` output to populate `left_rgb`/`right_rgb`, then call `poll_extra` directly and assert it returns `BrokerFlow::Break` — demonstrating that the outer `orb.run` loop in `pupil_contraction::Plan::run` would exit the objective without the ramp/wait sequence ever running or returning its own `Break`.
5. Optionally run the full `pupil_contraction::Plan::run` loop against a mocked `Orb`/broker harness and assert that `UserLedBrightness`/`UserLedPattern` MCU inputs associated with the ramp (`RAMP_TIME`, `WAIT_TIME`) are never sent, confirming the liveness sequence is skipped end-to-end for both eyes.

### Citations

**File:** src/plans/biometric_capture/mod.rs (L216-268)
```rust
impl OrbPlan for Plan {
    fn handle_ir_net(
        &mut self,
        orb: &mut Orb,
        output: port::Output<ir_net::Model>,
        frame: Option<camera::ir::Frame>,
    ) -> Result<BrokerFlow> {
        match output.value {
            ir_net::Output::Estimate(estimate) => {
                self.update_occlusion(orb, &estimate);
                if let Some(perceived_side) = estimate.perceived_side {
                    if perceived_side != i32::from(!self.target_left_eye) {
                        tracing::debug!("Skipping frame due to target and perceived side mismatch");
                        return Ok(BrokerFlow::Continue);
                    }
                } else {
                    tracing::debug!("IRNet perceived_side=None, skipping frame");
                    return Ok(BrokerFlow::Continue);
                }

                self.update_ux(orb, estimate.sharpness);

                let frame = frame.expect("frame must be set for an estimate output");
                let valid_capture = estimate.score >= IRIS_SCORE_MIN
                    && (!orb.ir_auto_exposure.is_enabled()
                        || IRIS_BRIGHTNESS_RANGE.contains(&frame.mean()))
                    && self.valid_capture_after <= Instant::now();

                if valid_capture {
                    let slot =
                        if self.target_left_eye { &mut self.left_ir } else { &mut self.right_ir };
                    if slot.is_none() {
                        dd_incr!(
                            "main.count.signup.during.biometric_capture.\
                             first_side_sharp_iris_detected",
                            &format!(
                                "side:{}",
                                if self.target_left_eye { "left" } else { "right" }
                            )
                        );
                    }
                    tracing::debug!("Found sharp iris: {}", estimate.score);
                    *slot = Some(FrameInfoIr::new(estimate, frame));
                }
            }
            ir_net::Output::Version(_) => {}
            ir_net::Output::Error => {
                tracing::error!("IR-Net failed during biometric capture phase");
            }
            ir_net::Output::Warmup => unreachable!("IR-Net::Warmup not part biometric capture"),
        }
        Ok(BrokerFlow::Continue)
    }
```

**File:** src/plans/biometric_capture/mod.rs (L359-371)
```rust
        // Check if we have both the iris and the face.
        if let (Some(_rgb), Some(_ir)) = (rgb, ir) {
            if !self.is_last_objective() {
                // We have completed scanning one side. It's ok for us to move forward even if we don't have the
                // self-custody frame, as still have 1 more eye to capture.
                return Ok(BrokerFlow::Break);
            }
            // We are now in the last objective and we have completed scanning both sides. We Just need to make sure
            // we have an self-custody frame before we completely exit the biometric capture phase.
            if self.self_custody_candidate_rgb.is_some() {
                return Ok(BrokerFlow::Break);
            }
        }
```

**File:** src/plans/biometric_capture/pupil_contraction.rs (L60-80)
```rust
        match self.state {
            State::NoSharpIris => {
                if let BrokerFlow::Break =
                    self.biometric_capture.handle_ir_net(orb, output, frame)?
                {
                    tracing::info!("Pupil Contraction extension: ramping up");
                    self.state = State::RampingUp { start_time: Instant::now() };
                    orb.main_mcu.send_now(mcu::main::Input::UserLedPattern(
                        mcu::main::UserLedControl {
                            pattern: mcu::main::UserLedPattern::AllWhite,
                            start_angle: Some(0),
                            angle_length: Some(100.),
                        },
                    ))?;
                    orb.main_mcu.send_now(mcu::main::Input::UserLedBrightness(0))?;
                    orb.disable_ir_auto_exposure();
                    orb.disable_ir_auto_focus();
                    orb.disable_eye_tracker();
                    orb.disable_eye_pid_controller();
                    orb.ir_eye_save_fps_override = Some(FPS);
                }
```

**File:** src/plans/biometric_capture/pupil_contraction.rs (L82-118)
```rust
            State::RampingUp { start_time } => {
                let now = Instant::now();
                let elapsed = now - start_time;
                let brightness = (elapsed.as_secs_f32() / RAMP_TIME.as_secs_f32()
                    * f32::from(u8::MAX))
                .clamp(0.0, u8::MAX.into()) as u8;
                orb.main_mcu.send_now(mcu::main::Input::UserLedPattern(
                    mcu::main::UserLedControl {
                        pattern: mcu::main::UserLedPattern::AllWhite,
                        start_angle: Some(0),
                        angle_length: Some(100.),
                    },
                ))?;
                orb.main_mcu.send_now(mcu::main::Input::UserLedBrightness(brightness))?;
                if elapsed >= RAMP_TIME {
                    tracing::info!("Pupil Contraction extension: waiting");
                    self.state = State::Waiting { start_time: now };
                }
            }
            State::Waiting { start_time } => {
                if start_time.elapsed() >= WAIT_TIME {
                    tracing::info!("Pupil Contraction extension: complete");
                    self.state = State::NoSharpIris;
                    orb.try_enable_ir_auto_exposure();
                    orb.try_enable_ir_auto_focus();
                    orb.try_enable_eye_tracker();
                    orb.try_enable_eye_pid_controller();
                    orb.ir_eye_save_fps_override = None;
                    orb.main_mcu.send_now(mcu::main::Input::UserLedBrightness(
                        USER_LED_DEFAULT_BRIGHTNESS,
                    ))?;
                    return Ok(BrokerFlow::Break);
                }
            }
        }
        Ok(BrokerFlow::Continue)
    }
```
