### Title
Unbounded Length-Prefixed Allocation in Livestream Upstream Socket Enables Memory-Exhaustion DoS - ([File: src/agents/livestream/upstream.rs])

### Summary
The `livestream` agent's `Upstream` listener binds a raw TCP socket on `0.0.0.0:9201` and reads a 4-byte length prefix from any connecting peer, then immediately allocates a buffer of that attacker-controlled size before any bounds checking or authentication. This is directly analogous to the "return bomb" class of bug in the report: an untrusted remote actor supplies a size value that forces the receiving process to perform an unbounded/oversized memory allocation, causing resource exhaustion, this time on the orb device itself rather than a relayer.

### Finding Description
`EventReader::poll_stream` reads the 4-byte big-endian length header from the socket and uses it, without any upper-bound validation, to allocate a `Vec<u8>`: [1](#0-0) 

```
if self.len_read == 4 {
    self.buf = vec![0; u32::from_be_bytes(self.len) as usize];
}
```

`u32::from_be_bytes` allows the peer to specify up to ~4.29 GB, and this value is used directly as the `Vec` allocation size with no `min()`/cap check against any maximum message size. The listener itself accepts connections from any address, not just localhost: [2](#0-1) 

The bound port constant is `PORT: u16 = 9201`, bound on `"0.0.0.0:{PORT}"`, exposing it to the local network, not just loopback: [3](#0-2) [4](#0-3) 

The read loop then attempts to fill this attacker-sized buffer chunk-by-chunk: [5](#0-4) 

This mirrors the report's root cause: return data (or here, a client-supplied payload) is unconditionally sized and loaded into memory based on an attacker-controlled length field before any sanity/size-limit check is applied, exactly the pattern `excessivelySafeCall()` was introduced to prevent in the Solidity code (checking length before allocating/copying).

### Impact Explanation
Because this parsing occurs inside the `livestream` agent thread (`agents/livestream/mod.rs`, run via `agentwire::agent::Thread::run`), a crash or an out-of-memory abort in this thread can take down the whole agent, and depending on the runtime supervision, potentially destabilize the orb-core process handling biometric signup flows. Repeated connections with a maximal length value (or many parallel connections, since a new `TcpStream`/`EventReader` is created per accepted connection) allow a network-adjacent, unprivileged actor to force large, wasteful allocations repeatedly, causing memory pressure/DoS on the orb without any authentication. Given the "no unbounded allocation should be attacker-controlled" principle from the reported bug class, this is a legitimate resource-exhaustion vector against the orb device, though it does not directly cause misattributed signups, biometric data disclosure, or attestation forgery — it is a memory/DoS-only impact vector on this specific livestream ingestion path.

### Likelihood Explanation
The listener is bound to `0.0.0.0`, so any device on the same network segment as the orb (e.g., during a livestream/companion-app session) can open a raw TCP connection to port 9201 and send an arbitrary 4-byte length prefix. No authentication, TLS, or handshake is required before the length-prefixed buffer is allocated, making exploitation straightforward for any unprivileged network peer that can reach the port.

### Recommendation
Enforce a maximum allowed message size before allocating the buffer, e.g., reject or close the connection if `u32::from_be_bytes(self.len)` exceeds a sane bound (matching the largest legitimate `livestream_event::Event` payload), similar to how `excessivelySafeCall()` bounds the return-data size before copying it into memory. Additionally, consider binding the listener to a loopback/authenticated interface only, rather than `0.0.0.0`, to reduce the reachable attack surface.

### Proof of Concept
1. Attacker on the same network as the orb connects to `orb_ip:9201`.
2. Attacker sends a 4-byte big-endian length header with value `0xFFFFFFFE` (~4.29 GB).
3. `EventReader::poll_stream` executes `self.buf = vec![0; 0xFFFFFFFE]`, forcing a huge allocation attempt in the `livestream` agent thread.
4. Attacker repeats this with multiple concurrent connections (each producing its own `EventReader`/buffer) to amplify memory pressure, causing allocation failures/aborts or severe memory exhaustion on the orb device.

### Citations

**File:** src/agents/livestream/upstream.rs (L14-14)
```rust
const PORT: u16 = 9201;
```

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
