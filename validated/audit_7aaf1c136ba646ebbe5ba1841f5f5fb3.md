### Title
Fixed 4096-byte `SERIALIZED_OUTPUT_SIZE` for QR-code agent output can be exceeded by attacker-controlled QR payload, causing an unrecoverable IPC serialization panic during signup - (File: `src/agents/qr_code.rs`)

### Summary
The `qr_code::Agent`'s shared-memory IPC channel reserves a fixed `SERIALIZED_OUTPUT_SIZE` of `4096` bytes for the `Output` message, which contains an attacker-controlled `payload: String` decoded directly from a scanned QR code plus corner `Points`. Unlike the reported Gnosis/EasyAuction bug — where a fixed allowance/amount computation didn't account for the real resource requirement (fee) and caused `initiateAuction` to revert — this fixed-size buffer allocation doesn't account for the real size of attacker-controlled QR content, and the serializer call is followed by `.expect(...)`, turning an oversized/malicious QR code into a panic rather than a handled error.

### Finding Description
`SharedPort` requires each agent to declare compile-time constant buffer sizes for IPC messages exchanged over shared memory: ` [1](#0-0) `. For `qr_code::Agent`, `SERIALIZED_OUTPUT_SIZE` is a hard-coded `4096` bytes, while `SERIALIZED_INPUT_SIZE` is sized to accommodate a full RGB frame: ` [2](#0-1) `.

The `Output` struct directly embeds the decoded QR string with no length cap: ` [3](#0-2) `. The decode path takes the full text returned by the QR decoder (`rxing_result.getText()`) and corner points without truncation or validation before returning `Output`: ` [4](#0-3) `.

When the agent process writes this `Output` into the shared-memory buffer, `serialize_message` allocates a `BufferSerializer` over the pre-sized `4096`-byte slice and calls `serializer.serialize_value(value).expect("failed to serialize an IPC message")` — any failure (including buffer overflow because the actual serialized size exceeds the fixed capacity) causes an unconditional panic in that call path: ` [5](#0-4) `. This is invoked by `RemoteInner::send`/`try_send`, which is exactly the path the QR-code worker process uses to publish its decoded result back to the broker: ` [6](#0-5) ` and `src/agents/qr_code.rs:87` (`port.try_send(&chain(output))`).

The QR content is entirely attacker-controlled: any physical QR code printed and presented to the orb's camera during the unauthenticated pre-signup "scan user/operator/WiFi QR code" flow is decoded by this same agent and Output type — see the generic QR scanning plan that dispatches decoded payloads: ` [7](#0-6) `. Only a very shallow length check (`qr_code.len() <= 10`) filters "ghost" codes; there is no upper bound enforced anywhere before the value is serialized across the process boundary: ` [8](#0-7) `.

QR codes, especially high-density/high-version ones or ones exploiting the escaped/hex-string decoding paths used for WiFi MECARD parsing (` [9](#0-8) `), can carry several kilobytes of text, comfortably exceeding a 4096-byte archive budget once serialization overhead (rkyv archive headers, `Points` vector of `(f32,f32)` tuples for many detected corners, string length prefix, and the `usize` message-size header) is included.

### Impact Explanation
The root cause mirrors the reported bug class: a fixed capacity/allowance computed independently of the actual attacker-influenced payload size, guarded only by an `.expect()`/hard revert rather than graceful rejection. In orb-core this does not directly leak biometric data or forge attestations, but it does allow an unprivileged party (anyone who can present a QR code to the orb's camera) to crash the `qr-code` worker process mid-decode via a panic in the IPC serialization path, right at the entry point of every signup (QR-code scanning is the very first step of enrollment). Because `exit_strategy` for this agent is `ExitStrategy::Restart` for deterministic crashes on bad input (`src/agents/qr_code.rs:101-105`), a maliciously crafted, oversized QR payload is a reliable, repeatable trigger of process restarts/denial of the QR-scanning subsystem, disrupting signup/enrollment availability for legitimate users at that orb.

### Likelihood Explanation
High for an unprivileged local attacker: physically presenting a crafted QR code to the orb's camera is the exact interaction the QR-scanning flow expects from any user, no authentication or prior signup state is required, and the code path is reached unconditionally at the start of every signup attempt (`scan_user_qr_code` / WiFi/operator QR flows). The only existing guard (minimum length of 10 characters) does nothing to bound the maximum size.

### Recommendation
Bound the maximum accepted QR payload length (and number of detected corner points) before constructing `Output`, rejecting/truncating anything that would not fit within `SERIALIZED_OUTPUT_SIZE`, and replace the `.expect("failed to serialize an IPC message")` panic in `serialize_message` with a recoverable error path (e.g., drop the oversized message and log, rather than crashing the process). Additionally, size `SERIALIZED_OUTPUT_SIZE` (or validate at compile/test time) against the true maximum QR payload size supported by the decoder rather than an arbitrary constant.

### Proof of Concept
1. Generate a QR code encoding a string close to or above the ZXing/QR maximum capacity (QR codes can encode up to ~2,953 bytes of binary/alphanumeric data at version 40); combine multiple detected finder-pattern corner points if achievable, and/or use escape sequences that expand during MECARD-style parsing.
2. Present this QR code to the orb's RGB camera during the "scan user QR-code"/"scan WiFi QR-code" step of `qr_scan::Plan::run` (`src/plans/qr_scan/mod.rs`).
3. `qr_code::Agent`'s worker process decodes the frame via `decode_rxing`, producing an `Output.payload` near/above 4096 bytes once rkyv-archived.
4. `port.try_send(&chain(output))` invokes `RemoteInner::send`, which calls `serialize_message` against the fixed `4096`-byte buffer; the `serializer.serialize_value(value).expect(...)` panics because the archived value doesn't fit, crashing the `qr-code` process and forcing a restart, disrupting signup for the current and subsequent users until recovery.

### Citations

**File:** agentwire/src/port.rs (L220-230)
```rust
    /// Buffer size for input messages. Must be at least `size_of::<usize>()`
    /// for a zero-sized input.
    const SERIALIZED_INPUT_SIZE: usize;

    /// Buffer size for output messages. Must be at least `size_of::<usize>()`
    /// for a zero-sized output.
    const SERIALIZED_OUTPUT_SIZE: usize;

    /// Buffer size for initial agent state. Must be at least
    /// `size_of::<usize>()` for a zero-sized state.
    const SERIALIZED_INIT_SIZE: usize;
```

**File:** agentwire/src/port.rs (L717-740)
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

    /// Tries to send a value on this channel. This function doesn't block and
    /// do nothing if the channel is full (in which case it returns `false`).
    #[allow(clippy::missing_panics_doc)]
    pub fn try_send(&mut self, output: &Output<T>) -> bool {
        unsafe {
            if sem_getvalue(&mut (*self.shared_memory).output_tx).expect("semaphore failure") > 0 {
                self.send(output);
                true
            } else {
                false
            }
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

**File:** src/network/mecard.rs (L158-189)
```rust
fn parse_string(input: &str) -> IResult<&str, String> {
    const SPECIAL_CHARS: &[char] = &['\\', ';', ',', '"', ':'];
    let non_special = verify(anychar, |c| SPECIAL_CHARS.iter().all(|s| c != s));
    let special = pair(tag("\\"), verify(anychar, |c| SPECIAL_CHARS.iter().any(|s| c == s)));
    let unescaped = alt((non_special, map(special, |(_, c)| c)));
    let (input, quote) = opt(tag("\""))(input)?;
    let (input, string) = fold_many0(unescaped, String::new, |mut acc, item| {
        acc.push(item);
        acc
    })(input)?;
    if quote.is_some() {
        let (input, _) = tag("\"")(input)?;
        Ok((input, string))
    } else if string.len() % 2 == 0 && string.chars().all(|c| c.is_ascii_hexdigit()) {
        // The value is in hex string format.
        let string = string.as_bytes().chunks(2).fold(
            String::with_capacity(string.len() / 2),
            |mut acc, pair| {
                // The following sequence of unwraps can't fail because of the
                // condition above.
                let string = str::from_utf8(pair).unwrap();
                let octet = u8::from_str_radix(string, 16).unwrap();
                let chr = char::from_u32(octet.into()).unwrap();
                acc.push(chr);
                acc
            },
        );
        Ok((input, string))
    } else {
        Ok((input, string))
    }
}
```
