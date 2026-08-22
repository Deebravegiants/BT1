### Title
MCU acknowledgement errors are silently swallowed, causing `Mcu::send` to falsely report success for hardware-dependent biometric operations - (File: `src/mcu/can.rs`)

### Summary
`Can::handle_input` in `src/mcu/can.rs` receives an `Ack` from the microcontroller for every command sent from orb-core. When the ack contains a known, non-timeout error code, the code logs the error but leaves `completion_result` at its default `Ok(())` value instead of setting it to `Err(...)`. The line that would set the error is explicitly commented out with a TODO.

### Finding Description
`Mcu::send` in `src/mcu/mod.rs` sends a message to the MCU and then awaits a `completion_rx` oneshot channel, treating `Ok(())` as confirmation that the microcontroller executed the command successfully: [1](#0-0) 

However, the value placed onto that channel is computed in `Can::handle_input`, which initializes `completion_result = Ok(())` and only overwrites it to `Err` on a *timeout* branch. When the MCU actively returns an error ack code (a real, decodable `ErrorCode`), the branch only logs `tracing::error!` and leaves the line that would set `completion_result = Err(...)` commented out: [2](#0-1) 

The same applies to unknown/incompatible error codes from a mismatched firmware version — again only logged, never surfaced as an error: [3](#0-2) 

Finally, the (unmodified, still-`Ok`) `completion_result` is sent back to the caller: [4](#0-3) 

This is structurally the same bug class as the reported `transferFrom` issue: an underlying operation's result/status code (the MCU's ack error) is not checked/propagated, so the calling code (and any state/telemetry built on top of it) believes the operation succeeded when it actually failed.

### Impact Explanation
`Mcu::send` gates numerous hardware operations that are part of the signup/biometric-capture flow (IR LED enabling for specific wavelengths, mirror gimbal positioning for eye tracking, etc. — used across `src/plans/biometric_capture/*.rs`, `src/brokers/orb.rs`). Because a real MCU-reported failure is converted into a false "success" by `can.rs`, orb-core's signup pipeline can proceed as though a hardware precondition (correct IR wavelength, correct mirror position) was met when it was not. Depending on which specific command silently fails, this can affect the reliability/integrity of illumination or mirror positioning steps used during capture, which the pipeline and fraud/liveness logic assume were correctly applied. This is a genuine state-inconsistency bug (Impact class matches "misattributed" internal state during signup), but I could not fully trace, within the given iteration budget, which specific commands (e.g., an IR LED wavelength command tied directly to a fraud/liveness check) are most exposed versus commands whose failure is comparatively benign (e.g., a cosmetic UI LED). The code comment itself (`// TODO: return Error on MCU Errors and add better Error handling for the callers`) confirms this is a known, unresolved gap rather than intentional behavior.

### Likelihood Explanation
This path is reachable on every normal signup by any unprivileged user — it does not require a malicious operator, peer, or physical hardware tampering; it triggers whenever the MCU legitimately returns an error ack (e.g., transient firmware/hardware error, out-of-range argument, protocol version mismatch) during a routine biometric-capture command. Given the comment "(f.e. on arguments out of range)" the authors acknowledge this occurs in practice, not just in edge/adversarial cases.

### Recommendation
In `src/mcu/can.rs`, uncomment/restore the `completion_result = Err(...)` assignments for both the known-error and unknown-error-code branches so that `Mcu::send` returns `Err` to its caller whenever the MCU acknowledges a command with a non-success error code. Ensure callers in `src/plans/biometric_capture/*.rs` and `src/brokers/orb.rs` that rely on `Mcu::send` succeeding for capture-critical operations (LED wavelength, mirror position) correctly handle/retry on the propagated error rather than assuming success.

### Proof of Concept
1. During a normal signup, the plan issues an MCU command (e.g., set IR LED wavelength or move mirror) via `Mcu::send`, which calls `self.tx_mut().send((input, Some(completion_tx))).await` and awaits `completion_rx`.
2. The MCU responds with an `Ack` whose `error` field is a valid, non-`Success` `ErrorCode` (for example due to an out-of-range argument or transient fault).
3. In `Can::handle_input`, the `else if let Ok(error) = ...try_from(ack.error)` branch executes `tracing::error!(...)` only; `completion_result` remains `Ok(())` [5](#0-4) .
4. `completion_tx.send(completion_result).ok()` sends `Ok(())` back to the caller [4](#0-3) .
5. `Mcu::send` in `src/mcu/mod.rs` observes `Ok(())` from `completion_rx.await?` and returns `Ok(())` to the plan, which proceeds as if the hardware command succeeded [6](#0-5) , even though the MCU explicitly reported failure.

### Citations

**File:** src/mcu/mod.rs (L86-109)
```rust
    /// Sends a message to the microcontroller and waits for the acknowledge.
    fn send(&mut self, input: I::Input) -> Pin<Box<dyn Future<Output = Result<()>> + Send + '_>> {
        Box::pin(async move {
            let mut retries = SEND_RETRY_COUNT;
            'retry: loop {
                let (completion_tx, completion_rx) = oneshot::channel();
                self.tx_mut().send((input.clone(), Some(completion_tx))).await?;
                if let Err(error) = completion_rx.await? {
                    if retries > 0 {
                        tracing::warn!("Retrying last µC message... [{}]", retries);
                        retries -= 1;
                        continue 'retry;
                    }
                    tracing::error!("Maximum µC send retries reached, aborting with Error");
                    return Err(error);
                };
                break 'retry;
            }
            if let Some(log) = self.log_mut() {
                I::log_input(log, &input);
            }
            Ok(())
        })
    }
```

**File:** src/mcu/can.rs (L116-137)
```rust
                                    } else if ack.error
                                        == orb_messages::mcu_main::ack::ErrorCode::Success as i32
                                    {
                                        #[allow(let_underscore_drop)]
                                        let _ =
                                            output_tx.send(I::success_ack_output_from_input(input));
                                    // TODO: return Error on MCU Errors and add better Error handling for the callers (f.e. on arguments out of range)
                                    } else if let Ok(error) =
                                        orb_messages::mcu_main::ack::ErrorCode::try_from(ack.error)
                                    {
                                        tracing::error!(
                                            "MCU error: {error}, original message: {message:#?}"
                                        );
                                        // completion_result = Err(Error::msg(format!("µC Error: {}", error)));
                                    } else {
                                        tracing::error!(
                                            "Unknown MCU error code: {}. Perhaps orb-core and MCU \
                                             firmware versions are not compatible",
                                            ack.error
                                        );
                                        // completion_result = Err(Error::msg("Unknown µC Error"));
                                    }
```

**File:** src/mcu/can.rs (L155-157)
```rust
                    if let Some(completion_tx) = completion_tx {
                        completion_tx.send(completion_result).ok();
                    }
```
