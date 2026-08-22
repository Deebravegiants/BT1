### Title
MCU Acknowledge Errors Are Silently Discarded, Causing Commands That Gate Iris/Face Capture Hardware (IR LEDs, Camera Triggering) to Be Reported as Successful Despite Failure - (File: src/mcu/can.rs)

### Summary
The external report describes a Denial-of-Service pattern in which the return/acknowledgment of a critical operation (an ERC-20 `transfer`) is not checked, so a failed operation is silently treated as if it succeeded. The closest analog in `orb-core` is in the CAN MCU driver: when the microcontroller returns a non-`Success` acknowledgment (an actual hardware error), the code that would propagate that failure to the caller is commented out, so `completion_result` remains `Ok(())` and is returned to the caller regardless of the real error.

### Finding Description
In `Can::<I>::handle_input`, each outbound MCU command is paired with a `completion_tx: Option<ResultSender>` that the caller awaits to learn whether the microcontroller actually executed the command [1](#0-0) . When an acknowledgment with a real MCU error code is received, the code only logs the error and explicitly leaves the corresponding "set result to Err" statement commented out:

```
} else if let Ok(error) =
    orb_messages::mcu_main::ack::ErrorCode::try_from(ack.error)
{
    tracing::error!(
        "MCU error: {error}, original message: {message:#?}"
    );
    // completion_result = Err(Error::msg(format!("µC Error: {}", error)));
} else {
    tracing::error!(
        "Unknown MCU error code: {}...",
        ack.error
    );
    // completion_result = Err(Error::msg("Unknown µC Error"));
}
``` [2](#0-1) 

Only the timeout branch actually sets `completion_result = Err(...)` [3](#0-2) . The (unchanged) `Ok(())` value is then unconditionally sent back to the caller: `completion_tx.send(completion_result).ok();` [4](#0-3) .

The generic `Mcu::send` trait method — used throughout the broker to drive hardware that gates biometric capture, such as enabling the IR LEDs and triggering the IR eye/face cameras — awaits exactly this channel and only retries/aborts on an `Err`, since a returned `Ok(())` is treated as confirmation that the microcontroller executed the command [5](#0-4) . Call sites rely on this contract to believe the physical LED/camera trigger state matches software state, e.g. `set_ir_wavelength` and `start_ir_eye_camera`/`start_ir_face_camera` [6](#0-5) [7](#0-6) [8](#0-7) .

This mirrors the reported bug class exactly: a known-failure signal from a critical operation (MCU ack error, analogous to an ERC‑20 `transfer` returning `false`) is deliberately not propagated, so the caller proceeds under the false assumption that the operation succeeded.

### Impact Explanation
Because the failure path is disabled, `orb-core` can believe IR LED activation, IR wavelength selection, or IR eye/face camera triggering commands succeeded on the microcontroller when they in fact failed (out-of-range values, hardware fault, firmware rejection, etc., all reported via the MCU error ack). Since these commands directly control the illumination and camera-triggering hardware that the iris/face biometric-capture pipeline depends on for genuine, live captures, a genuine hardware failure could be masked, letting the signup/capture flow continue as though the correct illumination/camera state was established. This weakens the assurance that captured images used for enrollment reflect the intended live-capture conditions, i.e., it degrades the integrity of the biometric capture step that upstream fraud/liveness assumptions depend on. The developer-left `TODO` comment confirms this is a known, unresolved gap: `// TODO: return Error on MCU Errors and add better Error handling for the callers` [9](#0-8) .

### Likelihood Explanation
This does not require a malicious peer/operator/node and does not depend on hardware access beyond normal orb operation — it triggers on any legitimate MCU error acknowledgment (e.g., out-of-range parameter, transient firmware fault) that occurs during standard signup flows, since `Mcu::send` is used pervasively for IR LED and camera-trigger control in the capture path. The bug is deterministic given any non-Success, non-timeout ack, making it moderately likely to occur under real-world hardware fault conditions, though it requires an actual MCU-side error/fault to manifest (not attacker-controlled input).

### Recommendation
- Uncomment and enable the `completion_result = Err(...)` assignments for both the known-error and unknown-error-code branches in `handle_input`, so the true MCU error is propagated back through `completion_tx` [10](#0-9) .
- Ensure callers of `Mcu::send` (e.g., `set_ir_wavelength`, `start_ir_eye_camera`, `start_ir_face_camera`) correctly abort or fail the capture/signup flow when such an error is returned, rather than silently continuing.
- Add unit/integration test coverage that injects MCU error acks and asserts that `Mcu::send` returns an `Err` and that dependent capture logic reacts appropriately (retry, abort signup, or surface a hardware fault), closing the loophole implied by the existing `TODO`.

### Proof of Concept
Not applicable as a transactional PoC (no financial primitive is at stake here); the root cause is demonstrable purely by code inspection: any code path that reaches the `else if let Ok(error) = ...` or the final `else` branch in `handle_input` leaves `completion_result` at its initial `Ok(())`, and that same `Ok(())` is what gets sent through `completion_tx` to the awaiting caller in `Mcu::send`, causing the caller to treat a hardware-reported error as success [11](#0-10) [12](#0-11) .

### Citations

**File:** src/mcu/can.rs (L71-157)
```rust
    async fn handle_input(
        mcu_tx: tokio::sync::mpsc::Sender<orb_messages::mcu_main::mcu_message::Message>,
        mut input_rx: mpsc::Receiver<(I::Input, Option<ResultSender>)>,
        mut ack_rx: mpsc::Receiver<orb_messages::mcu_main::Ack>,
        output_tx: broadcast::Sender<I::Output>,
    ) -> Result<()> {
        let mut counter: u16 = 0;
        loop {
            match future::select(input_rx.next(), ack_rx.next()).await {
                Either::Left((None, _)) | Either::Right((None, _)) => break,
                Either::Left((Some((input, completion_tx)), _)) => {
                    let mut completion_result = Ok(());
                    let ack_number = create_ack(counter);
                    counter += 1;
                    if let Some(message) = I::input_to_message(&input, ack_number) {
                        mcu_tx.send(message.clone()).await?;
                        let time_start = std::time::Instant::now();
                        'ack_number_match: loop {
                            // decrease timeout each iteration
                            let time_until_timeout = TIMEOUT - time_start.elapsed();
                            match timeout(time_until_timeout, ack_rx.next()).await {
                                Ok(Some(ack)) => {
                                    if ack_number != ack.ack_number {
                                        // let's detect weird acks:
                                        // - ack_number for this process
                                        // - with higher counter than the one expected
                                        // (can happen when counter wraps around but should be rare)
                                        if is_ack_for_us(ack.ack_number)
                                            && ack_number < ack.ack_number
                                        {
                                            tracing::warn!(
                                                "Acknowledge number mismatch: Jetson {} <> MCU \
                                                 {}.\nMessage: {}\nDiscarding acknowledge..",
                                                ack_number,
                                                ack.ack_number,
                                                orb_messages::mcu_main::ack::ErrorCode::try_from(
                                                    ack.error
                                                )
                                                .map_or_else(
                                                    |_| ack.error.to_string(),
                                                    |error| error.to_string()
                                                )
                                            );
                                        }
                                        continue 'ack_number_match;
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
                                }
                                Ok(None) => {
                                    bail!("ack_rx ended unexpectedly");
                                }
                                Err(_) => {
                                    tracing::error!(
                                        "Timed out waiting response from µC with acknowledge \
                                         number: {}",
                                        ack_number
                                    );
                                    completion_result = Err(Error::msg("µC Timeout"));
                                }
                            }
                            // Default is to not match next incoming ack_number
                            break 'ack_number_match;
                        }
                    }
                    if let Some(completion_tx) = completion_tx {
                        completion_tx.send(completion_result).ok();
                    }
```

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

**File:** src/brokers/orb.rs (L459-472)
```rust
    /// Sets active IR LED wavelength.
    pub async fn set_ir_wavelength(&mut self, ir_led_wavelength: IrLed) -> Result<()> {
        self.main_mcu.send(mcu::main::Input::IrLed(ir_led_wavelength)).await?;
        self.ir_led_wavelength = ir_led_wavelength;
        let exposure_range = self.exposure_range();
        if let Some(ir_auto_exposure) = self.ir_auto_exposure.enabled() {
            ir_auto_exposure
                .send_unjam(port::Input::new(ir_auto_exposure::Input::SetExposureRange(
                    exposure_range,
                )))
                .await?;
        }
        Ok(())
    }
```

**File:** src/brokers/orb.rs (L529-545)
```rust
    /// Starts eye IR camera.
    pub async fn start_ir_eye_camera(&mut self) -> Result<()> {
        #[cfg(feature = "livestream")]
        if let Some(livestream) = self.livestream.enabled() {
            livestream.send(port::Input::new(livestream::Input::IrEyeState(true))).await?;
        }
        self.main_mcu.send(mcu::main::Input::TriggeringIrEyeCamera(true)).await?;
        self.main_mcu.send(mcu::main::Input::FrameRate(IR_CAMERA_FRAME_RATE)).await?;
        self.enable_ir_eye_camera()?;
        self.enable_ir_led().await?;
        self.ir_eye_camera
            .enabled()
            .unwrap()
            .send(port::Input::new(camera::ir::Command::Start))
            .await?;
        Ok(())
    }
```

**File:** src/brokers/orb.rs (L569-585)
```rust
    /// Starts face IR camera.
    pub async fn start_ir_face_camera(&mut self) -> Result<()> {
        #[cfg(feature = "livestream")]
        if let Some(livestream) = self.livestream.enabled() {
            livestream.send(port::Input::new(livestream::Input::IrFaceState(true))).await?;
        }
        self.main_mcu.send(mcu::main::Input::TriggeringIrFaceCamera(true)).await?;
        self.main_mcu.send(mcu::main::Input::FrameRate(IR_CAMERA_FRAME_RATE)).await?;
        self.enable_ir_face_camera()?;
        self.enable_ir_led().await?;
        self.ir_face_camera
            .enabled()
            .unwrap()
            .send(port::Input::new(camera::ir::Command::Start))
            .await?;
        Ok(())
    }
```
