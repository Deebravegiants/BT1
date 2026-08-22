### Title
Unauthenticated TCP length-prefix in `EventReader::poll_stream` allows unbounded memory allocation / DoS of the orb-core process - (File: `src/agents/livestream/upstream.rs`)

### Summary
`Upstream::new` binds an unauthenticated, unencrypted TCP listener on port 9201 with no peer verification. `EventReader::poll_stream` reads a 4-byte length prefix directly into `u32::from_be_bytes(self.len)` and immediately allocates `self.buf = vec![0; len]` with no upper bound check, letting any network-reachable client force an allocation of up to ~4 GiB per connection before a single payload byte is validated.

### Finding Description
The listener is created with `TcpListener::bind(format!("0.0.0.0:{PORT}"))` with no TLS, token, or peer-address filtering. [1](#0-0) 
When a connection is accepted, `poll_stream` reads 4 bytes into `self.len` and, once complete, immediately does `self.buf = vec![0; u32::from_be_bytes(self.len) as usize]` with no sanity/size cap and before any of the payload bytes (or any authentication) are read. [2](#0-1) 
This code runs inside the `livestream` agent, which executes as an `agentwire::agent::Thread` — i.e., in the same OS process/address space as other agents/pipeline logic in orb-core, not an isolated process. [3](#0-2)  A failed or excessive allocation (`vec![0; ~4GiB]`) can exhaust process memory or trigger Rust's global allocator abort path (`handle_alloc_error`), which aborts the entire process — not just the livestream thread — impacting any concurrently running signup/capture pipeline in the same process.

### Impact Explanation
This is a resource-exhaustion / denial-of-service vector on the orb-core process reachable by any host with plain TCP connectivity to port 9201, with no credentials required. Because the `livestream` agent runs as a thread within the main orb-core process rather than an isolated subprocess, a triggered allocation failure/abort can crash or stall the whole process, including any concurrently-running signup/capture pipeline, matching a resource-exhaustion / fail-closed-invariant violation rather than a biometric-forgery or identity-binding compromise. It does not, by itself, provide unauthorized signup, wrong-identity binding, biometric disclosure, liveness bypass, or attestation forgery — the actual reachable damage is DoS/crash, and impact should be scoped as such rather than as attestation/biometric forgery.

### Likelihood Explanation
Highly feasible and repeatable given only network reachability to port 9201: no auth, no TLS, no rate limiting, and no length cap exist in `poll_stream`. This requires only the stated precondition (network reachability), matching the "unprivileged attacker" constraint. Note: `livestream` is compiled only when the `livestream` cargo feature is enabled (`#[cfg(feature = "livestream")] pub mod livestream;` in `src/agents/mod.rs`); whether this feature is enabled in the shipped/production orb-core binary could not be confirmed from the available files and should be verified before treating this as always-reachable in production.

### Recommendation
- Enforce a maximum accepted payload length (e.g., reject/close the connection if `len` exceeds a small protocol-defined bound such as a few KB) before allocating `self.buf`.
- Consider using `try_reserve`/`try_reserve_exact` instead of `vec![0; len]` so allocation failures return an `Err` instead of aborting the process.
- Add authentication/authorization (token or mTLS) to the listener, and bind to a loopback/local interface instead of `0.0.0.0` if remote access is not required.
- Isolate the livestream agent in its own process (as done for other privilege-sensitive agents) so a crash/OOM there cannot take down the pipeline handling signups.

### Proof of Concept
Integration/fuzz test plan:
1. Start `Upstream::new()` (or the `livestream` agent) in a test harness.
2. From a plain `TcpStream::connect`, write a 4-byte big-endian value close to `u32::MAX` (e.g., `0xFFFF_FFF0`) and do not send further payload bytes.
3. Assert that either (a) the connection is rejected/closed before any large allocation occurs, or (b) memory usage of the process stays bounded (e.g., via `/proc/self/status` VmRSS sampling) — the current code fails this assertion because `vec![0; len]` is executed unconditionally once the 4-byte prefix is read.
4. Repeat the connection multiple times to show repeatable resource pressure/DoS without needing to send any complete payload.

### Citations

**File:** src/agents/livestream/upstream.rs (L36-39)
```rust
    pub async fn new() -> Result<Self> {
        let listener = TcpListener::bind(format!("0.0.0.0:{PORT}")).await?;
        Ok(Self { listener, stream: None })
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

**File:** src/agents/livestream/mod.rs (L86-94)
```rust
impl agentwire::agent::Thread for Agent {
    type Error = Error;

    #[allow(clippy::too_many_lines)]
    fn run(self, mut port: port::Inner<Self>) -> Result<(), Self::Error> {
        let rt = runtime::Builder::new_current_thread().enable_all().build()?;
        let mut upstream = rt.block_on(Upstream::new())?;
        let mut downstream = None;
        let mut gpu = rt.block_on(Gpu::new())?;
```
