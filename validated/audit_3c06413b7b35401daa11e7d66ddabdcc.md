### Title
Unbounded allocation via untrusted 4-byte length prefix in livestream `EventReader::poll_stream` - (src/agents/livestream/upstream.rs)

### Finding Description
`EventReader::poll_stream` reads a 4-byte big-endian length prefix from a raw, unauthenticated TCP connection to port 9201 and immediately allocates a buffer of that size with `self.buf = vec![0; u32::from_be_bytes(self.len) as usize]` at line 97, without any upper bound check against the wire-supplied length. [1](#0-0)  The listener binds to `0.0.0.0:{PORT}` (port 9201) with no authentication before accepting a connection and instantiating a fresh `EventReader::default()`. [2](#0-1) [3](#0-2)  An attacker who can reach this port can send `[0xFF,0xFF,0xFF,0xFF]`, causing `len_read == 4` and an immediate ~4 GiB allocation attempt, with no subsequent validation against a maximum payload size before the buffer is read into. The `Upstream::poll_next` loop drives this via `event_reader.poll_stream`, and on error it resets the reader but the allocation still executes synchronously before any error path is reached. [4](#0-3) 

However, this code path only exists when the crate is built with the `livestream` feature: the `livestream` agent field on the `Orb` broker, its inclusion in `src/plans/mod.rs`, `src/agents/mod.rs`, `src/cli.rs`, and `src/bin/orb-core.rs` are all gated behind `#[cfg(feature = "livestream")]`. [5](#0-4)  I was unable to confirm from the available Cargo.toml contents whether this feature is enabled by default in production orb builds; this needs to be verified directly against the build configuration/flake used for shipped orb-core binaries, since the answer changes the real-world reachability of this bug.

### Impact Explanation
If the `livestream` feature is compiled into production firmware and port 9201 is reachable from the network the orb is on, an unauthenticated attacker can trigger a large one-shot allocation (up to ~4 GiB) or a big enough allocation to cause an OOM/abort of the livestream agent thread. Because `start_signup` in `src/plans/mod.rs` awaits `livestream.send(port::Input::new(livestream::Input::Clear)).await?` synchronously, a wedged/crashed livestream agent thread could stall or fail the signup flow, which matches a signup-availability/denial-of-service impact rather than a data-disclosure or authorization-bypass impact.

### Likelihood Explanation
Exploitation requires: (1) the `livestream` feature being compiled into the deployed binary, and (2) network-level reachability to TCP port 9201 on the orb (e.g., same LAN/USB-network segment as the orb, depending on deployment). Given the code binds to `0.0.0.0`, if the feature is enabled and the interface is exposed, the attack is trivial and fully repeatable — a single 4-byte packet suffices, no auth or state manipulation required. I could not confirm the default feature-flag state for shipped/production builds from what's indexed, which is the key remaining uncertainty for real-world likelihood.

### Recommendation
Cap the length prefix against a fixed maximum UI-event payload size (e.g. a few KB, matching the actual `livestream_event::Event` payload sizes) before allocating `self.buf`, and terminate/reset the connection if the declared length exceeds that bound, rather than trusting the wire-supplied `u32` unconditionally at line 97.

### Proof of Concept
Add a unit/fuzz test for `EventReader::poll_stream` (or a wrapper testable function) that:
1. Constructs an `EventReader::default()`.
2. Feeds it a mocked/duplex `AsyncRead` stream that yields bytes `[0xFF, 0xFF, 0xFF, 0xFF]` as the length prefix.
3. Polls `poll_stream` and asserts that either (a) the resulting allocation is capped to a defined `MAX_EVENT_PAYLOAD_SIZE` constant, or (b) the connection is rejected/reset with an error, rather than allocating `usize::from(u32::MAX)` bytes.
4. A fuzz harness feeding random 4-byte prefixes should assert `self.buf.len() <= MAX_EVENT_PAYLOAD_SIZE` always holds after the length-prefix branch executes. [6](#0-5)

### Citations

**File:** src/agents/livestream/upstream.rs (L35-39)
```rust
impl Upstream {
    pub async fn new() -> Result<Self> {
        let listener = TcpListener::bind(format!("0.0.0.0:{PORT}")).await?;
        Ok(Self { listener, stream: None })
    }
```

**File:** src/agents/livestream/upstream.rs (L45-63)
```rust
    fn poll_next(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        if let Some((stream, event_reader)) = &mut self.stream {
            match event_reader.poll_stream(cx, Pin::new(stream)) {
                Poll::Ready(events) => {
                    *event_reader = EventReader::default();
                    match events {
                        Ok(Some(events)) => {
                            return Poll::Ready(Some(Ok(Event::UiEvents(events))));
                        }
                        Ok(None) => {
                            self.stream = None;
                            return Poll::Ready(Some(Ok(Event::Closed)));
                        }
                        Err(err) => return Poll::Ready(Some(Err(err))),
                    }
                }
                Poll::Pending => {}
            }
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

**File:** src/agents/livestream/upstream.rs (L84-98)
```rust
            if self.len_read < 4 {
                let mut read_buf = ReadBuf::new(&mut self.len[self.len_read..]);
                match stream.as_mut().poll_read(cx, &mut read_buf) {
                    Poll::Ready(Ok(())) if read_buf.filled().is_empty() => {
                        return Poll::Ready(Ok(None));
                    }
                    Poll::Ready(Ok(())) => self.len_read += read_buf.filled().len(),
                    Poll::Ready(Err(err)) => {
                        return Poll::Ready(Err(eyre!("Error reading from stream: {err}")));
                    }
                    Poll::Pending => return Poll::Pending,
                }
                if self.len_read == 4 {
                    self.buf = vec![0; u32::from_be_bytes(self.len) as usize];
                }
```

**File:** src/brokers/orb.rs (L221-223)
```rust
    #[cfg(feature = "livestream")]
    #[agent(thread)]
    pub livestream: agent::Cell<livestream::Agent>,
```
