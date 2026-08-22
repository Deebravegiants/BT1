Let me look at the actual serialization write function that uses these output buffers to confirm bounds handling.This confirms the vulnerability. At line 755 in `serialize_message`, `serializer.serialize_value(value).expect("failed to serialize an IPC message")` will **panic** (not return an `Err`) if serialization exceeds the `BufferSerializer`'s fixed backing slice (`buf[mem::size_of::<usize>()..]`, sized via `SERIALIZED_OUTPUT_SIZE = 4096` for `rgb_net::Model`), since `rkyv`'s `BufferSerializer` returns an error when writing past the buffer's end, and that error is unwrapped via `.expect(...)`.

### Title
RGB-Net `EstimateOutput` with many predictions can overflow the fixed 4096-byte `SERIALIZED_OUTPUT_SIZE` IPC buffer, panicking the rgb-net process - ([File: src/agents/python/rgb_net.rs])

### Summary
`rgb_net::Model` declares `SERIALIZED_OUTPUT_SIZE = 4096` as a fixed upper bound for the rkyv-serialized `Output` (which wraps `EstimateOutput { rgbnet_version: String, predictions: Vec<EstimatePredictionOutput> }`), but `extract()` builds `predictions` with unbounded length directly from the number of face detections returned by the RGB-Net Python model, with no cap. If a captured scene yields enough simultaneous face detections (e.g., a photo collage or multiple people in frame), the serialized output can exceed 4096 bytes, causing `agentwire::port::serialize_message`'s `.expect("failed to serialize an IPC message")` to panic in the rgb-net agent process. [1](#0-0) [2](#0-1) [3](#0-2) 

### Finding Description
The call path is: Python RGB-Net model returns a `predictions` list from the camera frame → `Environment::rgb_net_estimate` calls `extract(estimation)` which allocates `Vec::with_capacity(rgbnet_predictions_len)` and pushes one `EstimatePredictionOutput` per detected face/prediction, with no upper bound check on `rgbnet_predictions_len` [2](#0-1) . This `EstimateOutput` becomes `Output::Estimate(estimate)` returned from `Environment::iterate` [4](#0-3) , which is passed via `RemoteInner::send` on the agent side into `serialize_message` [5](#0-4) .

`serialize_message` constructs a `BufferSerializer` over a fixed-length slice `buf[size_of::<usize>()..]`, where `buf` is exactly `T::SERIALIZED_OUTPUT_SIZE` bytes (4096 for `rgb_net::Model`) as defined by `unsafe fn output(&mut self)` in `SharedMemory<T>` [6](#0-5)  and the `SharedPort` impl [1](#0-0) . The serialization call `serializer.serialize_value(value).expect("failed to serialize an IPC message")` unconditionally panics if the value's serialized size exceeds the buffer, since `rkyv`'s buffer-backed serializer returns an `Err` on overflow rather than growing dynamically [7](#0-6) . There is no validation anywhere in `extract()`, `rgb_net_estimate`, or the broker's `handle_rgb_net` that caps the number of predictions or checks the serialized size against `SERIALIZED_OUTPUT_SIZE` before or during this call [8](#0-7) .

Each `EstimatePredictionOutput` contains a bbox (rectangle + bool + f64) and 5 landmark points (each 2×f64), roughly ~100+ bytes when archived. With `rgbnet_version: String` overhead plus the vector's archived representation, only a modest number of simultaneous face detections (roughly a few dozen, depending on exact archived layout) is needed to exceed the 4096-byte budget — well within what an attacker can produce by presenting a photo collage, poster, or crowd scene to the camera during signup capture.

### Impact Explanation
A panic inside the rgb-net Python-agent process (running via `run_python_process`/`agentwire::agent::Process`) crashes that agent process. Since the signup broker (`src/brokers/orb.rs::handle_rgb_net`) depends on receiving rgb-net outputs to drive `biometric_capture` plan logic (eye tracking, distance estimation, auto-focus, face-identifier fusion), losing the rgb-net agent mid-session wedges or aborts the active signup flow, since `handle_rgb_net`'s `restore_frame!` macro and downstream `plan.handle_rgb_net` calls depend on continuous, correctly-ordered output from this agent [9](#0-8) . This is a denial-of-service against the signup session (session wedge/crash), not a bypass of identity/liveness/fraud checks — matching a "signup-state wedge" / availability impact category rather than unauthorized signup or biometric bypass.

### Likelihood Explanation
Feasible and repeatable by an unprivileged attacker: presenting a photo collage, multi-face poster, or crowd scene to the orb's RGB camera during any signup attempt is a low-effort, fully attacker-controlled physical action with no special access required. The precondition (many simultaneous detectable faces in one frame) is trivially reproducible in a lab setting, and every signup attempt reaches this code path (`rgb_net_estimate` runs continuously during biometric capture).

### Recommendation
Bound the number of predictions before constructing `EstimateOutput` in `extract()` (e.g., cap or truncate `rgbnet_predictions_len` to a safe maximum, or filter to only the primary/top-N-scored predictions before allocating), and make `SharedPort::SERIALIZED_OUTPUT_SIZE` a true worst-case bound consistent with that cap. Additionally, replace `serializer.serialize_value(value).expect(...)` in `agentwire::port::serialize_message` with a graceful error path (log + drop/mark-error output) instead of panicking on serialization overflow, so any future or unforeseen oversized payload cannot crash the agent process.

### Proof of Concept
Unit/fuzz test plan (to run in `src/agents/python/rgb_net.rs` or `agentwire/src/port.rs` test modules):
1. Construct a synthetic `EstimateOutput { rgbnet_version: "x".repeat(N), predictions: vec![EstimatePredictionOutput{..}; M] }` for increasing `M` (e.g., 1, 10, 50, 100).
2. Call `agentwire::port::serialize_message` (or replicate its logic directly) with a `buf` sized exactly at `rgb_net::Model::SERIALIZED_OUTPUT_SIZE` (4096 bytes), as done in production shared-memory allocation [6](#0-5) .
3. Assert that for some `M` within realistic camera-detection range, the call panics via the `.expect("failed to serialize an IPC message")` at [10](#0-9)  instead of returning a recoverable error — demonstrating the crash is reachable from attacker-controlled camera content parsed by `extract()`.
4. Expected (fixed) behavior: `extract()` should cap `predictions.len()` such that the archived size can never exceed `SERIALIZED_OUTPUT_SIZE`, and/or `serialize_message` should return a `Result` handled gracefully by the caller instead of panicking.

### Citations

**File:** src/agents/python/rgb_net.rs (L160-166)
```rust
impl SharedPort for Model {
    const SERIALIZED_INIT_SIZE: usize =
        size_of::<usize>() + size_of::<<Model as Archive>::Archived>();
    const SERIALIZED_INPUT_SIZE: usize =
        4096 + RGB_NATIVE_HEIGHT as usize * RGB_NATIVE_WIDTH as usize * 3;
    const SERIALIZED_OUTPUT_SIZE: usize = 4096;
}
```

**File:** src/agents/python/rgb_net.rs (L172-199)
```rust
impl super::Environment<Model> for Environment<'_> {
    fn iterate(&mut self, py: Python, input: &ArchivedInput) -> Result<Output> {
        let t = Instant::now();

        let (op, res) = match input {
            ArchivedInput::Estimate { frame } => {
                ("estimate", self.rgb_net_estimate(py, frame.into_ndarray()).map(Output::Estimate))
            }
            ArchivedInput::Warmup => ("warmup", self.warmup(py).map(|()| Output::Warmup)),
        };

        dd_timing!("main.time.processing" + format!("{}.{}", Model::DD_NS, op), t);
        tracing::trace!(
            "Python agent {}::{} <benchmark>: {} ms",
            Model::NAME,
            op,
            t.elapsed().as_millis()
        );

        res.or_else(|e| {
            if let Some(pe) = e.downcast_ref::<PyErr>() {
                <Model as super::AgentPython>::report_python_exception(py, &e, pe);
                Ok(Output::Error)
            } else {
                Err(e)
            }
        })
    }
```

**File:** src/agents/python/rgb_net.rs (L297-323)
```rust
pub fn extract(estimation: &PyAny) -> Result<EstimateOutput> {
    let rgbnet_version = get_and_extract!(estimation, "rgbnet_version")?;
    let rgbnet_predictions = get_item!(estimation, "predictions")?;
    let rgbnet_predictions_len =
        rgbnet_predictions.len().wrap_err("failed to .len() 'predictions'")?;
    let mut predictions = Vec::with_capacity(rgbnet_predictions_len);
    for i in 0..rgbnet_predictions_len {
        let rgbnet_prediction = get_item!(rgbnet_predictions, &i)?;
        let rgbnet_bbox = get_item!(rgbnet_prediction, "bbox")?;
        let rgbnet_landmarks = get_item!(rgbnet_prediction, "landmarks")?;
        predictions.push(EstimatePredictionOutput {
            bbox: EstimatePredictionBboxOutput {
                coordinates: extract_rectangle(get_item!(rgbnet_bbox, "coordinates")?)?,
                is_primary: get_and_extract!(rgbnet_bbox, "is_primary")?,
                score: get_and_extract!(rgbnet_bbox, "score")?,
            },
            landmarks: EstimatePredictionLandmarksOutput {
                left_eye: extract_point(get_item!(rgbnet_landmarks, "left_eye")?)?,
                left_mouth: extract_point(get_item!(rgbnet_landmarks, "left_mouth")?)?,
                nose: extract_point(get_item!(rgbnet_landmarks, "nose")?)?,
                right_eye: extract_point(get_item!(rgbnet_landmarks, "right_eye")?)?,
                right_mouth: extract_point(get_item!(rgbnet_landmarks, "right_mouth")?)?,
            },
        });
    }
    Ok(EstimateOutput { rgbnet_version, predictions })
}
```

**File:** agentwire/src/port.rs (L605-612)
```rust
    unsafe fn output(&mut self) -> &mut [u8] {
        unsafe {
            slice::from_raw_parts_mut(
                ptr::addr_of_mut!(*self).add(1).cast::<u8>().add(T::SERIALIZED_INPUT_SIZE * 2),
                T::SERIALIZED_OUTPUT_SIZE,
            )
        }
    }
```

**File:** agentwire/src/port.rs (L717-726)
```rust
    /// Sends a value on this channel.
    #[allow(clippy::missing_panics_doc)]
    pub fn send(&mut self, output: &Output<T>) {
        unsafe {
            sem_wait(&mut (*self.shared_memory).output_tx).expect("semaphore failure");
            serialize_message((*self.shared_memory).output(), &mut self.scratch, &output.value);
            (*self.shared_memory).output_ts = output.source_ts;
            sem_post(&mut (*self.shared_memory).output_rx).expect("semaphore failure");
        }
    }
```

**File:** agentwire/src/port.rs (L743-760)
```rust
fn serialize_message<T>(
    buf: &mut [u8],
    scratch: &mut Option<FallbackScratch<HeapScratch<SCRATCH_SIZE>, AllocScratch>>,
    value: &T,
) where
    T: Archive + for<'a> Serialize<SharedSerializer<'a>> + Debug,
{
    let mut serializer = CompositeSerializer::new(
        BufferSerializer::new(&mut buf[mem::size_of::<usize>()..]),
        scratch.take().unwrap(),
        SharedSerializeMap::new(), // reuse of this map doesn't work
    );
    serializer.serialize_value(value).expect("failed to serialize an IPC message");
    let size = serializer.pos();
    let (_, c, _) = serializer.into_components();
    buf[..mem::size_of::<usize>()].copy_from_slice(&size.to_ne_bytes());
    *scratch = Some(c);
}
```

**File:** src/brokers/orb.rs (L1166-1212)
```rust
    fn handle_rgb_net(
        &mut self,
        plan: &mut dyn Plan,
        output: port::Output<rgb_net::Model>,
    ) -> Result<BrokerFlow> {
        macro_rules! restore_frame {
            () => {
                loop {
                    if let Some((frame, source_ts)) = self.rgb_net_frames.pop_front() {
                        if source_ts == output.source_ts {
                            break frame;
                        }
                    } else {
                        tracing::error!("RGB-Net frame not found");
                        return Ok(BrokerFlow::Continue);
                    }
                }
            };
        }

        let frame = if let rgb_net::Output::Estimate(estimate) = &output.value {
            let frame = restore_frame!();
            self.pre_handle_rgb_net_estimate(&output, estimate)?;
            if let Some(image_notary) = self.image_notary.enabled() {
                // Timestamps are generated in the image_notary history, so send there first.
                image_notary.tx.send_now(port::Input::new(
                    image_notary::Input::SaveRgbNetEstimate(
                        image_notary::SaveRgbNetEstimateInput {
                            estimate: estimate.clone(),
                            frame: frame.clone(),
                            log_metadata_always: true,
                            resolution_override: None,
                        },
                    ),
                ))?;
            }
            Some(frame)
        } else if let output @ rgb_net::Output::InitUndistort = &output.value {
            tracing::warn!("Unexpected output from RGB-Net: {output:#?}");
            None
        } else {
            None
        };

        plan.handle_rgb_net(self, output, frame)
    }

```
