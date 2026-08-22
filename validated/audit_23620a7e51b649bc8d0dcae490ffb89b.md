## Title
Cross-signup state bleed and stale QR/phase/sensor overlay disclosure on Livestream reconnect - (File: src/agents/livestream/mod.rs)

## Finding Description
The livestream TCP listener on port 9201 [1](#0-0)  accepts any client and emits `Event::Connected`/`Event::Closed` independent of the signup lifecycle. In the agent loop, `Event::Closed` only resets the local `downstream` variable to `None`; it does **not** touch `gpu.app` state or clear GPU textures [2](#0-1) . `Event::Connected` likewise only re-creates `downstream`, without clearing anything [3](#0-2) .

The only paths that reset `gpu.app`/textures are `Input::Clear` (calls `gpu.clear_textures()` and `gpu.app.clear()`) and startup [4](#0-3) . Critically, `App::clear()` itself does not reset all fields — it leaves `phase`, `ir_eye_state`, `ir_face_state`, `rgb_state`, `thermal_state`, `depth_state` untouched [5](#0-4) , so even a legitimate `Clear` doesn't fully wipe UI/fraud-relevant state such as the last displayed phase name or capture-state indicators.

Exploit flow: after `Event::Connected(addr)` sets `downstream = Some(...)`, execution falls through to the post-match block, which immediately calls `gpu.render(events, ...)` with an empty `events` vec and pushes a frame built from whatever `gpu.app`/texture state is currently in memory [6](#0-5) . Since that state was last populated by the previous signup's `Input::Phase`, `Input::QrCode`, camera frame, and net-estimate updates (and never cleared on `Closed`), a newly-connected client instantly receives a rendered frame containing the prior signup's QR overlay, phase text, and last camera texture, before any new `Input` for the new session arrives.

## Impact Explanation
This is an information-disclosure/state-bleed issue across distinct livestream client sessions: an unprivileged network client that can reach TCP port 9201 (e.g., on the local network) can observe residual UI/debug state (phase name, QR overlay coordinates, last captured camera frame texture, capture booleans) belonging to a different, unrelated signup session that has already ended, simply by connecting after that signup finished and before the next `Input::Clear`/new frame data arrives. This is a session-isolation violation, not a signup-authorization or biometric-signing bypass — it does not let the attacker forge identity, bypass fraud checks, or affect the victim's own signup outcome, since the leaked data is only ever what was already rendered for debug/live-monitoring purposes.

## Likelihood Explanation
Requires network reachability to the orb's livestream TCP port (9201) and no additional privileges are enforced by `Upstream::new`/`TcpListener` — any TCP client can connect. The race window (between `Closed` and the next signup's first `Input` after a fresh `Connected`) is real and reproducible: it exists whenever a livestream client reconnects between the end of one signup and the start of meaningful new input for the next. However, whether livestream is actually enabled/reachable in production builds and whether real "victim signup" biometric imagery would already have been cleared by an explicit `Input::Clear` sent by the orchestrator at signup boundaries (in `src/brokers/orb.rs`) could not be fully confirmed from the available context — this affects the practical severity/likelihood.

## Recommendation
Send `Input::Clear` (or an equivalent full reset covering `phase`, `*_state` booleans, and textures) on every `Event::Closed`, and again defensively on `Event::Connected`, so no downstream consumer ever renders leftover state from a previous connection/signup. Also extend `App::clear()` to reset `phase` and all `*_state` fields, not just estimates/QR/mirror data.

## Proof of Concept
Unit/integration test plan (in `src/agents/livestream/mod.rs` or a new test module):
1. Construct the agent loop state (`gpu`, `downstream = None`) directly or via a test harness that can inject `Input`/`Event` values.
2. Simulate: `Event::Connected(A)` → `Input::Phase("iris_capture")` → `Input::QrCode(points_A)` → `Input::RgbFrame(frame_A)`.
3. Simulate: `Event::Closed`.
4. Simulate: `Event::Connected(B)` (a different socket address/session).
5. Assert, before any `Input` for B is delivered, that the frame pushed to B's `Downstream` (or `gpu.app` snapshot) still contains `phase == Some("iris_capture")`, `qr_code_points == points_A`, and the RGB texture from `frame_A` — demonstrating cross-session bleed.
6. Expected fix behavior: after adding a reset on `Closed`/`Connected`, the same assertions should show `phase == None`, `qr_code_points` empty, and textures cleared for B until B's own `Input` events arrive.

### Citations

**File:** src/agents/livestream/upstream.rs (L14-18)
```rust
const PORT: u16 = 9201;

pub struct Upstream {
    listener: TcpListener,
    stream: Option<(TcpStream, EventReader)>,
```

**File:** src/agents/livestream/mod.rs (L94-117)
```rust
        let mut gpu = rt.block_on(Gpu::new())?;
        gpu.clear_textures();
        loop {
            let input = rt.block_on(future::poll_fn(|cx| {
                if let Poll::Ready(input) = port.poll_next_unpin(cx) {
                    return Poll::Ready(Either::Left(input));
                }
                if let Poll::Ready(event) = upstream.poll_next_unpin(cx) {
                    return Poll::Ready(Either::Right(event));
                }
                Poll::Pending
            }));
            let mut events = Vec::new();
            match input {
                Either::Left(None) | Either::Right(None) => break,
                Either::Right(Some(Err(err))) => {
                    tracing::error!("Livestream upstream error: {err}");
                    continue;
                }
                Either::Left(Some(input)) => match input.value {
                    Input::Clear => {
                        gpu.clear_textures();
                        gpu.app.clear();
                    }
```

**File:** src/agents/livestream/mod.rs (L185-188)
```rust
                Either::Right(Some(Ok(Event::Connected(addr)))) => {
                    tracing::info!("Accepted a new Livestream connection from {}", addr.ip());
                    downstream = Some(Arc::new(Downstream::new(addr.ip())?));
                }
```

**File:** src/agents/livestream/mod.rs (L189-192)
```rust
                Either::Right(Some(Ok(Event::Closed))) => {
                    tracing::info!("Livestream connection closed by client");
                    downstream = None;
                }
```

**File:** src/agents/livestream/mod.rs (L197-200)
```rust
            if let Some(downstream) = &downstream {
                let downstream = Arc::clone(downstream);
                gpu.render(events, move |buffer| downstream.push(&buffer));
            }
```

**File:** src/agents/livestream/app.rs (L51-59)
```rust
    pub fn clear(&mut self) {
        self.rgb_net_estimate = None;
        self.ir_net_estimate = None;
        self.ir_focus = None;
        self.ir_exposure = None;
        self.mirror_points = VecDeque::new();
        self.qr_code_points = Vec::new();
        self.target_left_eye = false;
    }
```
