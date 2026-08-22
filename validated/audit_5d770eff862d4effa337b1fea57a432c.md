### Title
Unauthenticated network client can trigger and receive a live biometric video stream from the Orb - (File: src/agents/livestream/upstream.rs)

### Summary
The Uniswap report concerns third-party apps capturing sensitive on-screen data via unauthenticated screen-capture APIs. The closest analog in orb-core is the `livestream` agent, which opens an unauthenticated TCP listener that any network peer can connect to in order to trigger a live UDP video stream of the Orb's raw biometric camera feeds (IR eye, IR face, RGB face, thermal, depth) — effectively remote "screen capture" of biometric data without any authentication or authorization check.

### Finding Description
`Upstream::new()` binds a `TcpListener` on `0.0.0.0:9201` with no authentication of any kind: [1](#0-0) 

When any client connects, the agent treats it as `Event::Connected(addr)` and immediately creates a `Downstream` that starts pushing rendered camera frames as an H.264/RTP stream over **UDP to the connecting client's IP on port 9200** — again, with no credential check: [2](#0-1) [3](#0-2) 

The frames pushed into this stream are the Orb's raw biometric sensor data — IR eye, IR face, RGB, thermal, and depth camera frames — routed directly from the camera brokers into the livestream agent whenever it is enabled: [4](#0-3) [5](#0-4) [6](#0-5) 

Critically, the `livestream` feature is compiled in by default: the crate's `default` features enable `stage`, and `stage` itself enables `livestream`: [7](#0-6) 

At runtime, the agent is only started if the `--livestream`/`-l` CLI flag is passed: [8](#0-7) [9](#0-8) 

I was unable to fully verify the exact `enable_livestream` implementation (no direct match found in search), so I cannot confirm whether additional runtime checks exist inside it beyond the CLI flag gate.

### Impact Explanation
If the livestream agent is active (e.g., left enabled during field debugging/support sessions, or if the `-l`/`--livestream` flag is ever passed in a production or field deployment), any device on the same local network segment as the Orb can:
1. Open a raw TCP connection to port 9201 (no credentials, no TLS, no pairing) — this alone signals the Orb to start streaming.
2. Receive a live UDP video feed on port 9200 containing the user's live IR eye, IR face, RGB face, thermal, and depth camera frames during biometric capture/signup — i.e., raw biometric imagery, including facial/iris data.

This is directly analogous to the reported vulnerability: instead of a malicious Android app screen-capturing wallet secrets, an unauthenticated network peer can capture the Orb's most sensitive UI/sensor content (a live view of the person's iris and face during signup) without any authorization step. This is an access-control gap in a sensitive channel, resulting in unauthorized disclosure of biometric data to any third party on the local network.

### Likelihood Explanation
Requires network adjacency to the Orb (same LAN/Wi-Fi/local segment) and the livestream agent to be running. Likelihood is reduced by the CLI-flag gate for actually starting the stream at runtime, but the feature is compiled into default/`stage` builds, and there is no authentication, allowlisting, or pairing mechanism protecting port 9201/9200 once the agent is enabled — any listener that can reach the Orb's IP can trigger and capture the stream. This mirrors the "medium severity / requires local proximity" profile of the original report, but here the trigger is a plain TCP connect rather than guessing a screenshot timing window.

### Recommendation
- **Short term:** Require mutual authentication (e.g., a pre-shared token or mTLS) before `Upstream` accepts a connection or before `Downstream` begins streaming to the requesting IP. At minimum, validate that the requesting IP is an explicitly operator-approved debug host, and restrict the listener to a loopback/VPN-only interface rather than `0.0.0.0`.
- **Long term:** Document and enforce that `livestream` must never be enabled on production/field Orbs handling real signups; add a build-time or startup assertion that blocks `--livestream` when running in a "production signup" configuration, and audit all other developer/debug interfaces (e.g., DBus interfaces in `src/dbus.rs`) for similarly unauthenticated exposure of biometric or session data.

### Proof of Concept
1. Start `orb-core` with the `livestream` feature (default in `stage` builds) and the `--livestream` CLI flag.
2. From any other device on the same network as the Orb, run `nc <orb-ip> 9201` (or any TCP client) to open a connection — no credentials required.
3. Observe the Orb agent log “Accepted a new Livestream connection from …” and begin sending an H.264/RTP stream via UDP to the attacker's IP on port 9200: [10](#0-9) 
4. Use `gst-launch-1.0 udpsrc port=9200 ! ...` (matching the `rtph264pay`/`udpsink` pipeline in `Downstream::new`) to decode and view the incoming live biometric camera feed: [11](#0-10)

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

**File:** src/agents/livestream/downstream.rs (L16-46)
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
```

**File:** src/brokers/orb.rs (L1043-1058)
```rust
    fn handle_ir_eye_camera(
        &mut self,
        plan: &mut dyn Plan,
        output: port::Output<camera::ir::Sensor>,
    ) -> Result<BrokerFlow> {
        #[cfg(feature = "livestream")]
        if let Some(livestream) = self.livestream.enabled() {
            livestream
                .tx
                .send_now(output.chain(livestream::Input::IrEyeFrame(output.value.clone())))?;
        }
        if let Some(ir_auto_exposure) = self.ir_auto_exposure.enabled() {
            ir_auto_exposure
                .tx
                .send_now(output.chain(ir_auto_exposure::Input::Frame(output.value.clone())))?;
        }
```

**File:** src/brokers/orb.rs (L1089-1111)
```rust
    fn handle_ir_face_camera(
        &mut self,
        plan: &mut dyn Plan,
        output: port::Output<camera::ir::Sensor>,
    ) -> Result<BrokerFlow> {
        #[cfg(feature = "livestream")]
        if let Some(livestream) = self.livestream.enabled() {
            livestream
                .tx
                .send_now(output.chain(livestream::Input::IrFaceFrame(output.value.clone())))?;
        }
        if let Some(image_notary) = self.image_notary.enabled() {
            image_notary.tx.send_now(port::Input::new(image_notary::Input::SaveIrFaceData(
                image_notary::SaveIrFaceDataInput {
                    frame: output.value.clone(),
                    wavelength: self.ir_led_wavelength,
                    fps_override: self.ir_face_save_fps_override,
                    log_metadata_always: true,
                },
            )))?;
        }
        plan.handle_ir_face_camera(self, output)
    }
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

**File:** Cargo.toml (L111-130)
```text
[features]
default = ["v2_x_x", "stage"]
# Orb Versioning - https://www.notion.so/Orb-Versioning-3c1f92d3efc344e9a5c35902aa6bafb5
v2_x_x = [] # EV1 and EV2
# v2_0_x DEPRECATED Proto 2
# v1_x_x DEPRECATED Proto 1
# v0_2_x DEPRECATED Proto 0 Sustaining 1
# v0_1_x DEPRECATED Proto 0 Sustaining 0
allow-plan-mods = []                                                        # Allows modifications to the plans.
cuda-test = ["orb-rgb-net/cuda-test", "orb-ir-net/cuda-test"]
debug-eye-tracker = []                                                      # Enables println outputs in eye_tracker.rs
integration_testing = []                                                    # Enable hacks for passing integration tests on CI
internal-data-acquisition = []                                              # Advanced and verbose imaging for R&D purposes.
livestream = ["dep:egui", "dep:egui-wgpu", "dep:egui-phosphor"]             # Enable livestream agent to debug cameras
log-iris-data = []                                                          # Allows logging of iris codes and mask codes
no-image-encryption = []
internal-pcp-export = []
internal-pcp-no-encryption = []
skip-user-qr-validation = ["internal-pcp-export", "internal-pcp-no-encryption"]
stage = ["dep:local-ip-address", "livestream", "agentwire/sandbox-network"] # Use staging backend
```

**File:** src/cli.rs (L14-17)
```rust
    /// Enable livestream
    #[cfg(feature = "livestream")]
    #[structopt(short = 'l', long)]
    pub livestream: bool,
```

**File:** src/bin/orb-core.rs (L92-95)
```rust
    #[cfg(feature = "livestream")]
    if cli.livestream {
        orb.enable_livestream()?;
    }
```
