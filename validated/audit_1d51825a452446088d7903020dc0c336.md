### Title
Fixed-size IPC buffer for QR-code output causes agent crash on oversized QR/MECARD payloads - ([File: src/agents/qr_code.rs])

### Summary
The `TRST-M-10` bug class describes an on-chain fee estimator that computed a message size using the wrong (smaller) payload schema than what was actually sent, causing the real payload to exceed the size the code accounted for and the operation to fail. The equivalent pattern exists in orb-core's shared-memory agent-IPC layer: the `qr_code::Agent` `SharedPort` implementation hard-codes `SERIALIZED_OUTPUT_SIZE = 4096` bytes for the decoded QR-code `Output` (`payload: String` + `points: Points`), but the actual size of `payload` is attacker/user controlled (any physical QR code scanned by an unauthenticated person) and is not bounded to fit within that constant. When the true serialized size exceeds the declared buffer, the shared-memory serializer panics.

### Finding Description
`qr_code::Agent`'s `SharedPort` implementation declares a fixed output buffer: [1](#0-0) 

The `Output` struct stores the raw decoded QR text verbatim, with no length validation or truncation: [2](#0-1) [3](#0-2) 

This `Output` is produced directly from whatever text is embedded in a scanned QR code — including the WiFi/MECARD-style codes consumed by `mecard::Credentials::parse` and the generic `qr_scan` plan used for operator, user, and WiFi QR flows: [4](#0-3) [5](#0-4) 

The value is then handed to the shared-memory IPC transport, which serializes it into a caller-declared fixed-size buffer (`SERIALIZED_OUTPUT_SIZE`) and unconditionally panics if the archived size does not fit: [6](#0-5) [7](#0-6) 

The 4096-byte buffer was sized assuming a "normal" QR payload (short user/operator IDs, short WiFi credentials), analogous to the LayerZero bug where the fee-estimation code assumed only the message-type discriminant would be encoded rather than the full struct. A standard QR code can encode far more text than 4096 bytes (QR Version 40 can hold up to ~4296 alphanumeric characters / ~2953 binary bytes), so a maliciously or accidentally oversized QR code presented to the Orb's camera can produce an `Output.payload` whose archived representation (payload string + corner `points: Vec<(f32,f32)>` + rkyv archive overhead) exceeds the declared 4096-byte constant.

### Impact Explanation
When the actual serialized size overruns the pre-declared shared-memory slot, `serializer.serialize_value(value).expect(...)` in `serialize_message` panics, crashing the `qr-code` agent subprocess. This is triggered purely by presenting a crafted QR code to the Orb's RGB camera during any QR-scanning phase (operator QR, user QR, or WiFi-configuration QR) — a step performed by unauthenticated/unprivileged users/operators before any identity verification takes place. Repeated presentation of such a QR code can be used to reliably crash/restart the QR-scanning subsystem, disrupting the signup or WiFi-configuration flow (denial of service against the biometric-enrollment pipeline). This does not directly leak biometric data or forge an attestation, but it is a concrete availability/robustness defect stemming from the same root cause class as TRST-M-10: an under-estimated fixed size for a variable-length, externally-controlled payload used in a critical send/serialize path.

### Likelihood Explanation
High likelihood of occurrence: any operator or bystander can generate and print a QR code containing more than ~4KB of text (trivial with any QR generator supporting version ≥30) and present it to the Orb during the QR-scan UX step, which is reached before any authentication or liveness check. The agent process comment even acknowledges crashes are expected to be deterministic for bad inputs ("Because crashes are deterministic for this agent, we will not retry bad inputs"), confirming the developers were aware the agent can crash on certain inputs, though the mitigation (restart strategy) does not address the unbounded-size root cause. Full end-to-end verification of the process restart/exit-strategy behavior after such a crash (whether the Orb aborts the whole signup or silently recovers) could not be completed within the available investigation and is noted as unverified.

### Recommendation
Bound the decoded QR payload length before constructing `Output` (reject/truncate strings whose archived size, together with `points`, would exceed `SERIALIZED_OUTPUT_SIZE`), and/or increase `SERIALIZED_OUTPUT_SIZE` to safely cover the maximum possible QR payload size (worst-case QR capacity plus rkyv/archive overhead), and make `serialize_message` return a recoverable error instead of `.expect(...)`-panicking so an oversized payload degrades gracefully (e.g., is dropped/logged) rather than crashing the agent process.

### Proof of Concept
1. Generate a QR code encoding a string of ~4200+ ASCII characters (e.g. `"WIFI:S:" + "A".repeat(4200) + ";;"` or any long arbitrary text), which is within the physical capacity of a standard QR code.
2. During any Orb flow that invokes `qr_scan::Plan` (operator scan, user scan, or WiFi-configuration scan — see `src/plans/qr_scan/mod.rs`), present the QR code to the RGB camera.
3. `qr_code::Agent::run` decodes it via `decode_rxing`, producing an `Output { payload: <4200+ byte string>, points }`.
4. `port.try_send(&chain(output))` → `Sender::send` → `serialize_message` attempts to serialize into the fixed 4096-byte shared-memory buffer declared by `SharedPort::SERIALIZED_OUTPUT_SIZE`; serialization fails and `.expect("failed to serialize an IPC message")` panics, crashing the `qr-code` agent process.

### Citations

**File:** src/agents/qr_code.rs (L28-35)
```rust
/// Qr-code reader output.
#[derive(Debug, Archive, Serialize, Deserialize)]
pub struct Output {
    /// Detected QR-code value.
    pub payload: String,
    /// QR-code corner coordinates.
    pub points: Points,
}
```

**File:** src/agents/qr_code.rs (L57-63)
```rust
impl SharedPort for Agent {
    const SERIALIZED_INIT_SIZE: usize =
        size_of::<usize>() + size_of::<<Agent as Archive>::Archived>();
    const SERIALIZED_INPUT_SIZE: usize =
        4096 + RGB_NATIVE_HEIGHT as usize * RGB_NATIVE_WIDTH as usize * 3;
    const SERIALIZED_OUTPUT_SIZE: usize = 4096;
}
```

**File:** src/agents/qr_code.rs (L112-134)
```rust
#[allow(clippy::cast_precision_loss)]
fn decode_rxing(
    qr_scanner: &mut QrReader,
    image: Vec<u8>,
    width: u32,
    height: u32,
) -> Result<Output, rxing::Exceptions> {
    let mut binarized_image = BinaryBitmap::new(HybridBinarizer::new(
        BufferedImageLuminanceSource::new(DynamicImage::ImageRgb8(
            RgbImage::from_vec(width, height, image)
                .expect("image size to be at least 3*width*height"),
        )),
    ));
    let rxing_result = qr_scanner.decode(&mut binarized_image)?;
    Ok(Output {
        payload: rxing_result.getText().to_owned(),
        points: rxing_result
            .getPoints()
            .iter()
            .map(|p| (p.x / width as f32, p.y / height as f32))
            .collect(),
    })
}
```

**File:** src/plans/qr_scan/mod.rs (L56-73)
```rust
impl<S: Schema> OrbPlan for Plan<S> {
    fn handle_qr_code(
        &mut self,
        orb: &mut Orb,
        output: port::Output<qr_code::Agent>,
    ) -> Result<BrokerFlow> {
        let qr_code = output.value.payload;
        // The underlying library sometimes detects ghost QR codes of a few characters. This
        // prevents a voice to be played in those cases.
        if qr_code.len() <= 10 {
            tracing::warn!("Small, potentially ghost, QR code detected, skipping: {qr_code:?}");
            return Ok(BrokerFlow::Continue);
        }
        orb.ui.qr_scan_capture();
        self.qr_code =
            S::try_parse(&qr_code).map(|parsed| (parsed, qr_code)).ok_or(ScanError::Invalid);
        Ok(BrokerFlow::Break)
    }
```

**File:** src/network/mecard.rs (L77-127)
```rust
impl Credentials {
    /// Parses WiFi credentials encoded in MECARD format.
    pub fn parse(input: &str) -> IResult<&str, Self> {
        let (mut input, _) = tag("WIFI:")(input)?;

        // Parses a set of fields with the following requirements:
        // 1. A field is parsed no more than once.
        // 2. Fields are parsed in arbitrary order.
        // 3. Each field is optional.
        macro_rules! parse_fields {
            ($($parse:path => $opt:ident,)*) => {
                $(let mut $opt = None;)*
                loop {
                    $(
                        if $opt.is_none() {
                            if let Ok((next_input, parsed)) = $parse(input) {
                                $opt = Some(parsed);
                                input = next_input;
                                continue;
                            }
                        }
                    )*
                    break;
                }
            };
        }
        parse_fields! {
            AuthType::parse => auth_type,
            parse_ssid => ssid,
            parse_password => password,
            parse_hidden => hidden,
        }

        let ssid = ssid.filter(|ssid| !ssid.is_empty());
        let (password, auth_type) = password
            .filter(|pwd| !pwd.is_empty())
            .map_or((None, Some(AuthType::Nopass)), |pwd| (Some(Password(pwd)), auth_type));

        // ssid is actually not optional.
        if ssid.is_none() {
            let (_, ()) = fail(input)?;
        }

        let (input, _) = tag(";")(input)?;
        let (input, _) = eof(input)?;

        let auth_type = auth_type.unwrap_or_default();
        let ssid = ssid.unwrap_or_default();
        let hidden = hidden.unwrap_or_default();
        Ok((input, Self { auth_type, ssid, password, hidden }))
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
