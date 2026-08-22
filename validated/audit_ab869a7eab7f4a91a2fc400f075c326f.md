### Title
Unauthenticated TCP listener on `0.0.0.0:9201` allows any network-adjacent client to receive the live biometric camera/QR overlay stream during an in-progress signup - ([File: src/agents/livestream/upstream.rs])

### Summary
`Upstream::new` binds an unauthenticated TCP listener on `0.0.0.0:{PORT}` (port 9201) with no per-connection identity, token, or TLS check. Any client that connects during `Event::Connected` causes a `Downstream` to be created and bound to that peer's IP, after which `gpu.render` streams `IrEyeFrame`/`IrFaceFrame`/`RgbFrame`/`QrCode`/depth/thermal-derived overlay video to that peer over UDP via `Downstream::push`, with no verification that the connecting party is the authorized operator or is tied to the active `SignupId`.

### Finding Description
`Upstream::new` binds `TcpListener::bind(format!("0.0.0.0:{PORT}"))` with `PORT = 9201`, with no TLS, no auth handshake, no allow-list [1](#0-0) . `poll_next` accepts any connection and immediately emits `Event::Connected(addr)` — the only information retained about the peer is its socket address, there is no identity check [2](#0-1) .

In the livestream agent's main loop, `Event::Connected(addr)` unconditionally creates `Downstream::new(addr.ip())` and stores it, then on every subsequent GPU render call streams video to that IP over UDP via `Downstream::push` regardless of who the accepted TCP peer actually is [3](#0-2) . The rendered content includes `Input::IrEyeFrame`, `Input::IrFaceFrame`, `Input::RgbFrame`, `Input::QrCode` points, and other camera/overlay data fed from the broker whenever the corresponding camera is enabled during signup capture [4](#0-3) . `Downstream::new`/`push` simply pipes raw video frames to a `udpsink` bound to the attacker-supplied `addr.ip()` on UDP port 9200, with no encryption [5](#0-4) .

The broker (`src/brokers/orb.rs`) forwards live IR/RGB/QR frames to the livestream agent whenever the `livestream` agent cell is enabled, independent of any specific requester identity or `SignupId` binding [6](#0-5) [7](#0-6) . There is no code path anywhere in `upstream.rs`, `mod.rs`, or `downstream.rs` that checks a token, certificate, or any credential tied to the operator app or the active `SignupId` before accepting a connection or before starting to push frames.

However, this is gated by the `livestream` cargo feature (`#[cfg(feature = "livestream")]`) throughout the broker and agent registration code [8](#0-7) . This feature appears intended as an internal/debug capability (referenced from developer tools like `manual-mirror-calibration.rs` and `health-check.rs`) rather than a feature enabled in standard production builds; I was unable to confirm from the available index whether the `livestream` feature is compiled into the units actually deployed to the field (default feature set in `Cargo.toml` could not be fully verified from the tool output — this is a genuine gap in what I was able to confirm).

### Impact Explanation
If this code path is compiled into a production-deployed Orb (feature `livestream` enabled), any device on the same network segment as the Orb (LAN/local network access, no credentials needed) could open a raw TCP connection to port 9201 during an active signup and receive the operator's/subject's live IR eye, IR face, RGB, and QR-derived video stream on UDP port 9200 without any authorization. This is a biometric data confidentiality bypass — live camera imagery of the person mid-enrollment is disclosed to an arbitrary local network attacker, matching a "sensitive/biometric data disclosure to unauthorized party" impact category.

### Likelihood Explanation
Exploitability requires: (1) the `livestream` feature to be compiled/enabled on the target unit, (2) network adjacency to the Orb (e.g. same Wi-Fi/LAN segment) during an in-progress signup, and (3) no additional network-layer protections (e.g., firewall) blocking port 9201/9200. Given these preconditions, the attack is trivial and fully repeatable — a bare `TcpStream::connect` to port 9201 is sufficient to trigger `Event::Connected` and begin receiving frames; no cryptographic material or race condition is needed.

### Recommendation
Require mutual authentication (e.g., TLS with pinned/operator certificate, or a pre-shared token validated in the TCP handshake) before transitioning to `Event::Connected` and creating a `Downstream`. Bind the listener to a loopback/localhost interface or a controlled interface instead of `0.0.0.0` unless remote streaming is explicitly required, and bind `Downstream`'s UDP sink only after verifying the connecting identity is the authorized operator session tied to the current `SignupId`.

### Proof of Concept
Integration test plan (in `src/agents/livestream` test module):
1. Start `Upstream::new().await` bound to test port; assert listener is on `0.0.0.0:{PORT}`.
2. From a plain unauthenticated `TcpStream::connect` (simulating an attacker with no operator credentials), connect to the listener while the livestream agent loop is running with an active signup pushing `Input::RgbFrame`/`Input::IrEyeFrame`/`Input::QrCode` inputs.
3. Assert that `poll_next` yields `Event::Connected(addr)` for this connection with no rejection.
4. Assert that a `Downstream` is subsequently constructed with `addr.ip()` (mock/replace `Downstream::push` to capture calls) and that `push` is invoked with frame data derived from the in-progress signup's `Input::IrEyeFrame`/`Input::RgbFrame`/`Input::QrCode`.
5. Expected (failing) assertion: frame data reaches `Downstream::push` for the unauthenticated connection without any check against a `SignupId` or operator credential — demonstrating the disclosure.

### Citations

**File:** src/agents/livestream/upstream.rs (L14-39)
```rust
const PORT: u16 = 9201;

pub struct Upstream {
    listener: TcpListener,
    stream: Option<(TcpStream, EventReader)>,
}

pub enum Event {
    Connected(SocketAddr),
    Closed,
    UiEvents(Vec<livestream_event::Event>),
}

#[derive(Default)]
struct EventReader {
    len: [u8; 4],
    len_read: usize,
    buf: Vec<u8>,
    buf_read: usize,
}

impl Upstream {
    pub async fn new() -> Result<Self> {
        let listener = TcpListener::bind(format!("0.0.0.0:{PORT}")).await?;
        Ok(Self { listener, stream: None })
    }
```

**File:** src/agents/livestream/upstream.rs (L64-74)
```rust
        match self.listener.poll_accept(cx) {
            Poll::Ready(Ok((stream, addr))) => {
                self.stream = Some((stream, EventReader::default()));
                Poll::Ready(Some(Ok(Event::Connected(addr))))
            }
            Poll::Ready(Err(err)) => {
                Poll::Ready(Some(Err(eyre!("Error accepting connection: {err}"))))
            }
            Poll::Pending => Poll::Pending,
        }
    }
```

**File:** src/agents/livestream/mod.rs (L118-171)
```rust
                    Input::IrEyeFrame(frame) => {
                        gpu.update_camera_ir_eye(&frame);
                    }
                    Input::IrFaceFrame(frame) => {
                        gpu.update_camera_ir_face(&frame);
                    }
                    Input::RgbFrame(frame) => {
                        gpu.update_camera_rgb(frame.as_bytes(), frame.width(), frame.height());
                    }
                    Input::ThermalFrame(frame) => {
                        gpu.update_camera_thermal(&frame);
                    }
                    Input::DepthFrame(frame) => {
                        gpu.update_camera_depth(&frame);
                    }
                    Input::Phase(name) => {
                        gpu.app.set_phase(name);
                    }
                    Input::IrEyeState(ir_eye_state) => {
                        gpu.app.set_ir_eye_state(ir_eye_state);
                        continue;
                    }
                    Input::IrFaceState(ir_face_state) => {
                        gpu.app.set_ir_face_state(ir_face_state);
                        continue;
                    }
                    Input::RgbState(rgb_state) => {
                        gpu.app.set_rgb_state(rgb_state);
                        continue;
                    }
                    Input::ThermalState(thermal_state) => {
                        gpu.app.set_thermal_state(thermal_state);
                        continue;
                    }
                    Input::DepthState(depth_state) => {
                        gpu.app.set_depth_state(depth_state);
                        continue;
                    }
                    Input::IrNetEstimate(ir_net_estimate) => {
                        gpu.app.set_ir_net_estimate(ir_net_estimate);
                        continue;
                    }
                    Input::RgbNetEstimate(rgb_net_estimate) => {
                        gpu.app.set_rgb_net_estimate(rgb_net_estimate);
                        continue;
                    }
                    Input::SetMirrorPoint(point) => {
                        gpu.app.set_mirror_point(point);
                        continue;
                    }
                    Input::QrCode(points) => {
                        gpu.app.set_qr_code_points(points);
                        continue;
                    }
```

**File:** src/agents/livestream/mod.rs (L185-200)
```rust
                Either::Right(Some(Ok(Event::Connected(addr)))) => {
                    tracing::info!("Accepted a new Livestream connection from {}", addr.ip());
                    downstream = Some(Arc::new(Downstream::new(addr.ip())?));
                }
                Either::Right(Some(Ok(Event::Closed))) => {
                    tracing::info!("Livestream connection closed by client");
                    downstream = None;
                }
                Either::Right(Some(Ok(Event::UiEvents(ui_events)))) => {
                    events = ui_events.into_iter().map(Into::into).collect();
                }
            };
            if let Some(downstream) = &downstream {
                let downstream = Arc::clone(downstream);
                gpu.render(events, move |buffer| downstream.push(&buffer));
            }
```

**File:** src/agents/livestream/downstream.rs (L16-62)
```rust
impl Downstream {
    #[allow(clippy::cast_possible_truncation)]
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
        appsrc.link(&nvvidconv)?;
        nvvidconv.link(&nvv4l2h264enc)?;
        nvv4l2h264enc.link(&rtph264pay)?;
        rtph264pay.link(&udpsink)?;
        pipeline.set_state(gstreamer::State::Playing)?;
        appsrc.set_block(true);
        Ok(Self { pipeline, appsrc, video_info })
    }

    pub fn push(&self, frame: &[u8]) -> Result<()> {
        let mut buffer = gstreamer::Buffer::with_size(self.video_info.size())
            .expect("failed to create a new gstreamer buffer");
        {
            let buffer = buffer.get_mut().unwrap();
            let mut video_frame =
                VideoFrameRef::from_buffer_ref_writable(buffer, &self.video_info).unwrap();
            let plane_data = video_frame.plane_data_mut(0).unwrap();
            unsafe {
                ptr::copy_nonoverlapping(frame.as_ptr(), plane_data.as_mut_ptr(), frame.len());
            }
        }
        self.appsrc.push_buffer(buffer)?;
        Ok(())
    }
```

**File:** src/brokers/orb.rs (L221-223)
```rust
    #[cfg(feature = "livestream")]
    #[agent(thread)]
    pub livestream: agent::Cell<livestream::Agent>,
```

**File:** src/brokers/orb.rs (L1113-1126)
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
        if let Some(qr_code) = self.qr_code.enabled() {
            qr_code.tx.send_now(output.chain(qr_code::Input::Frame(output.value.clone())))?;
        }
```

**File:** src/brokers/orb.rs (L1543-1555)
```rust
    fn handle_qr_code(
        &mut self,
        plan: &mut dyn Plan,
        output: port::Output<qr_code::Agent>,
    ) -> Result<BrokerFlow> {
        #[cfg(feature = "livestream")]
        if let Some(livestream) = self.livestream.enabled() {
            livestream.tx.send_now(port::Input::new(livestream::Input::QrCode(
                output.value.points.clone(),
            )))?;
        }
        plan.handle_qr_code(self, output)
    }
```
