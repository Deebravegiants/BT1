### Title
Unbounded memory allocation from unauthenticated TCP length prefix in `EventReader::poll_stream` - (File: src/agents/livestream/upstream.rs)

### Summary
`EventReader::poll_stream` reads a 4-byte big-endian length prefix from any TCP client that connects to the livestream listener on `0.0.0.0:9201`, and directly allocates `vec![0; u32::from_be_bytes(self.len) as usize]` with no upper-bound check. A remote, unauthenticated peer can send `0xFFFFFFFF` as the length prefix and force the orb process to attempt an allocation of up to ~4 GiB.

### Finding Description
`Upstream::new` binds a `TcpListener` on all interfaces (`0.0.0.0:{PORT}` with `PORT = 9201`) with no authentication, TLS, or peer restriction [1](#0-0) . Once a connection is accepted, `EventReader::poll_stream` reads exactly 4 bytes into `self.len`, and as soon as those 4 bytes are fully read, immediately allocates a buffer sized directly from the untrusted value with no sanity/maximum check: `self.buf = vec![0; u32::from_be_bytes(self.len) as usize];` [2](#0-1) . There is no cap comparing this size against a reasonable maximum message size, and the subsequent read loop at `self.buf_read < u32::from_be_bytes(self.len) as usize` simply keeps trying to fill that (potentially multi-gigabyte) buffer [3](#0-2) . Nothing upstream in `Upstream::poll_next` (`src/agents/livestream/upstream.rs:42-75`) or in the `livestream::Agent::run` loop (`src/agents/livestream/mod.rs:86-105`) validates or bounds this length before the allocation occurs. The listener/agent is a normal in-process component of the orb binary (feature-gated by `feature = "livestream"`, wired into `src/brokers/orb.rs` alongside camera frame handling), so a successful large allocation/OOM affects the same process that holds biometric camera frame buffers (IR eye/face, RGB, thermal, depth) that are forwarded to the livestream agent by `src/brokers/orb.rs` (`handle_ir_eye_camera`, `handle_rgb_camera`, etc.).

### Impact Explanation
An unauthenticated network peer able to reach TCP port 9201 (when the livestream feature/agent is enabled) can trigger a single-connection allocation of up to ~4 GiB by sending a crafted 4-byte length prefix. Repeated connections can be used to exhaust memory/trigger an OOM kill of the orb process, denying availability of the orb (including the livestream/UI feature and, since it runs in the same process, potentially destabilizing the broker that also manages biometric capture state). This matches a denial-of-service class impact, not an unauthorized signup, identity-binding, or biometric-disclosure bypass — no code path here touches signup authorization, fraud checks, signing, or upload logic.

### Likelihood Explanation
Preconditions: the `livestream` feature must be compiled in and the livestream agent must be enabled/running, and the attacker must have network reach to TCP port 9201 on the orb (binding is `0.0.0.0`, so it is not restricted to loopback). Given those preconditions, the bug is trivially and repeatably triggerable — a single 4-byte crafted TCP payload is sufficient, requiring no valid protocol handshake, session, or credentials.

### Recommendation
Add an explicit upper bound check on the parsed length before allocating, e.g. reject/close the connection if `len > MAX_MESSAGE_SIZE` (choose a size appropriate for the largest legitimate `livestream_event::Event` payload), and consider using `try_reserve`/streaming reads instead of eagerly allocating the full buffer up front.

### Proof of Concept
Add a unit/fuzz test for `EventReader::poll_stream` (or an integration test against `Upstream`) that:
1. Opens a TCP connection to the listener.
2. Sends the 4-byte big-endian value `0xFFFF_FFFF` as the length prefix.
3. Asserts that the reader either closes the connection or returns an error instead of proceeding to `vec![0; u32::MAX as usize]`.
4. As a regression guard, assert peak process memory does not exceed a configured threshold (e.g., via `cap-std`/`ulimit`-based test harness or a mock socket that pauses before sending body bytes, observing that no multi-GB allocation occurs).

### Citations

**File:** src/agents/livestream/upstream.rs (L35-39)
```rust
impl Upstream {
    pub async fn new() -> Result<Self> {
        let listener = TcpListener::bind(format!("0.0.0.0:{PORT}")).await?;
        Ok(Self { listener, stream: None })
    }
```

**File:** src/agents/livestream/upstream.rs (L96-98)
```rust
                if self.len_read == 4 {
                    self.buf = vec![0; u32::from_be_bytes(self.len) as usize];
                }
```

**File:** src/agents/livestream/upstream.rs (L99-110)
```rust
            } else if self.buf_read < u32::from_be_bytes(self.len) as usize {
                let mut read_buf = ReadBuf::new(&mut self.buf[self.buf_read..]);
                match stream.as_mut().poll_read(cx, &mut read_buf) {
                    Poll::Ready(Ok(())) if read_buf.filled().is_empty() => {
                        return Poll::Ready(Ok(None));
                    }
                    Poll::Ready(Ok(())) => self.buf_read += read_buf.filled().len(),
                    Poll::Ready(Err(err)) => {
                        return Poll::Ready(Err(eyre!("Error reading from stream: {err}")));
                    }
                    Poll::Pending => return Poll::Pending,
                }
```
