This confirms the vulnerability described exists exactly as stated. The `Upstream::new` binds to `0.0.0.0:9201` [1](#0-0) , accepting any TCP connection from the network with no authentication or IP allowlist check on `poll_accept` [2](#0-1) . The accepted `SocketAddr` flows directly into `Event::Connected(addr)` and then `Downstream::new(addr.ip())`, which sets the `udpsink` `host` property to `addr.to_string()` verbatim [3](#0-2) [4](#0-3) . Once `State::Playing` is set, the broker pushes raw `IrEyeFrame`, `IrFaceFrame`, `RgbFrame`, `ThermalFrame`, and `DepthFrame` camera data into the GPU compositor which is streamed via this UDP sink to whatever `host`/`port` was set from the untrusted TCP peer address [5](#0-4) [6](#0-5) . There is no validation of `addr` against an operator/backend allowlist anywhere in this path.

### Title
Unauthenticated TCP connection to port 9201 causes biometric camera livestream to be sent via UDP to attacker-controlled IP - (File: src/agents/livestream/downstream.rs)

### Summary
`Upstream::new` listens on `0.0.0.0:9201` and accepts any TCP connection without authentication. The connecting peer's IP address (`addr.ip()`) is passed unchecked into `Downstream::new`, which sets the GStreamer `udpsink` `host` property to that address and immediately starts streaming raw camera frames (IR eye/face, RGB, thermal, depth) over UDP port 9200 to whatever IP the attacker connected from.

### Finding Description
The livestream feature accepts TCP connections on port 9201 via `TcpListener::bind("0.0.0.0:{PORT}")` with no source-IP allowlist, token, or handshake check in `Upstream::new`/`poll_accept`. On acceptance, `Event::Connected(addr)` is emitted, and `orb-core`'s main livestream loop in `Agent::run` immediately calls `Downstream::new(addr.ip())`, which builds a gstreamer pipeline whose `udpsink` element's `host` property is set to `addr.to_string()` — the raw source address of the TCP client — and transitions the pipeline to `State::Playing` with no further verification. From that point, every subsequent camera frame (`IrEyeFrame`, `IrFaceFrame`, `RgbFrame`, `ThermalFrame`, `DepthFrame`) handled in `src/brokers/orb.rs` is forwarded into the livestream agent and rendered/pushed into this UDP sink, which unconditionally transmits to the attacker-supplied IP. Because UDP is connectionless and the `host` is derived purely from the TCP peer address (which an attacker fully controls by choosing their own source IP/port when initiating the connection, or by simply connecting from any host on the reachable network), there is no cryptographic or allowlist-based verification that the destination is the operator's tablet or any backend-authorized endpoint.

### Impact Explanation
An attacker with mere network reachability to port 9201 (e.g., same LAN/Wi-Fi segment as the Orb, or any network path if the port is externally reachable) can cause the device to stream a live, unencrypted video feed of the current signup subject's IR eye/face, RGB, thermal, and depth camera frames to an IP of their choosing. This is a direct disclosure of raw biometric capture data for a signup session the attacker did not initiate and has no authorization to view, matching a "sensitive biometric data disclosure" class of impact.

### Likelihood Explanation
Exploitability requires only network-level TCP connectivity to port 9201 with the `livestream` feature enabled and the `enable_livestream()` path invoked (e.g. via CLI flag) — no credentials, tokens, or operator interaction are needed. Any device on the same network segment can trivially open a TCP socket to the Orb's port 9201, at which point the streaming starts automatically per the `Event::Connected` handling with zero additional gating.

### Recommendation
Validate the connecting peer against an explicit allowlist (e.g., known operator tablet IP/subnet or a pre-shared authentication token exchanged before promoting the connection to `Event::Connected`) before calling `Downstream::new`, and/or require mutual authentication (e.g., TLS client cert or signed challenge) on the port-9201 TCP channel prior to starting the UDP sink pipeline. At minimum, bind the listener to a trusted local-only interface instead of `0.0.0.0`, and add an explicit check in `Downstream::new`/`Agent::run` rejecting any `addr` not present in a configured operator allowlist before entering `State::Playing`.

### Proof of Concept
Integration test plan (async, using `tokio::net::TcpListener`/`TcpStream`):
1. Start `Upstream::new()` bound to `127.0.0.1:9201` (or the real `0.0.0.0` binding in a test harness).
2. From a separate, unprivileged process/socket, connect via `TcpStream::connect` using an arbitrary source (simulate by supplying various `IpAddr` values, including public/non-operator IPs, directly to `Downstream::new` as the PoC unit test suggests).
3. Assert that `Downstream::new(addr)` proceeds to `pipeline.set_state(gstreamer::State::Playing)` (`Ok(Self { .. })`) without consulting any allowlist — demonstrating the missing check.
4. Expected (failing) assertion for a fixed version: `Downstream::new` or the `Event::Connected` handler in `src/agents/livestream/mod.rs` should return an error / refuse to enter `State::Playing` for any `addr` not present in a configured operator allowlist; currently no such check exists, so the test demonstrates the gap directly against `src/agents/livestream/downstream.rs:18-45` and `src/agents/livestream/mod.rs:185-188`.

### Citations

**File:** src/agents/livestream/upstream.rs (L36-39)
```rust
    pub async fn new() -> Result<Self> {
        let listener = TcpListener::bind(format!("0.0.0.0:{PORT}")).await?;
        Ok(Self { listener, stream: None })
    }
```

**File:** src/agents/livestream/upstream.rs (L64-68)
```rust
        match self.listener.poll_accept(cx) {
            Poll::Ready(Ok((stream, addr))) => {
                self.stream = Some((stream, EventReader::default()));
                Poll::Ready(Some(Ok(Event::Connected(addr))))
            }
```

**File:** src/agents/livestream/mod.rs (L185-188)
```rust
                Either::Right(Some(Ok(Event::Connected(addr)))) => {
                    tracing::info!("Accepted a new Livestream connection from {}", addr.ip());
                    downstream = Some(Arc::new(Downstream::new(addr.ip())?));
                }
```

**File:** src/agents/livestream/downstream.rs (L18-38)
```rust
    pub fn new(addr: IpAddr) -> Result<Self> {
        let video_info =
            VideoInfo::builder(VideoFormat::Bgrx, LIVESTREAM_FRAME_WIDTH, LIVESTREAM_FRAME_HEIGHT)
                .build()?;
        let pipeline = Pipeline::with_name("livestream");
        let appsrc = AppSrc::builder().caps(&video_info.to_caps()?).build();
        let nvvidconv = ElementFactory::make("nvvidconv").build()?;
        let nvv4l2h264enc = ElementFactory::make("nvv4l2h264enc").build()?;
        let rtph264pay = ElementFactory::make("rtph264pay").build()?;
        let udpsink = ElementFactory::make("udpsink").build()?;
        pipeline.add_many([
            appsrc.upcast_ref(),
            &nvvidconv,
            &nvv4l2h264enc,
            &rtph264pay,
            &udpsink,
        ])?;
        nvv4l2h264enc.set_property_from_str("insert-sps-pps", "1");
        nvv4l2h264enc.set_property_from_str("insert-vui", "1");
        udpsink.set_property_from_str("host", &addr.to_string());
        udpsink.set_property_from_str("port", &PORT.to_string());
```

**File:** src/brokers/orb.rs (L1113-1123)
```rust
    fn handle_rgb_camera(
        &mut self,
        plan: &mut dyn Plan,
        output: port::Output<camera::rgb::Sensor>,
    ) -> Result<BrokerFlow> {
        #[cfg(feature = "livestream")]
        if let Some(livestream) = self.livestream.enabled() {
            livestream
                .tx
                .send_now(output.chain(livestream::Input::RgbFrame(output.value.clone())))?;
        }
```

**File:** src/brokers/orb.rs (L1276-1298)
```rust
    fn handle_thermal_camera(
        &mut self,
        plan: &mut dyn Plan,
        output: port::Output<camera::thermal::Sensor>,
    ) -> Result<BrokerFlow> {
        #[cfg(feature = "livestream")]
        if let Some(livestream) = self.livestream.enabled() {
            livestream
                .tx
                .send_now(output.chain(livestream::Input::ThermalFrame(output.value.clone())))?;
        }
        if let Some(image_notary) = self.image_notary.enabled() {
            image_notary.tx.send_now(port::Input::new(image_notary::Input::SaveThermalData(
                image_notary::SaveThermalDataInput {
                    frame: output.value.clone(),
                    wavelength: self.ir_led_wavelength,
                    fps_override: self.thermal_save_fps_override,
                    log_metadata_always: true,
                },
            )))?;
        }
        plan.handle_thermal_camera(self, output)
    }
```
