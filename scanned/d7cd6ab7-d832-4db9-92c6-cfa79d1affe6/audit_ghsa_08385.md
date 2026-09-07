# [H] Russh: Unchecked CryptoVec allocation and growth handling is reachable

## Summary
Severity: High
Advisory: GHSA-g9f8-wqj9-fjw5
CVE: CVE-2026-46673
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-21
Source: https://github.com/advisories/GHSA-g9f8-wqj9-fjw5
Type: github-advisory

## Affected
- crates.io: `russh-cryptovec` — affected >=0 <0.60.3
- crates.io: `russh` — affected >=0 <0.60.3

## Details
### Title
Unchecked `CryptoVec` allocation and growth handling was reachable from local agent inputs in current `russh` releases and from remote SSH traffic in historical pre-`0.58.0` releases

### Summary
`CryptoVec` used unchecked capacity growth, unchecked length arithmetic, and unsafe allocation/locking paths. In current `russh` releases, local SSH agent peers could still feed attacker-controlled frame lengths into buffer growth before validation. In older `russh` releases before `0.58.0`, remote SSH traffic also reached `CryptoVec` through transport and compression buffers.

### Details
The underlying unsafe paths were in `CryptoVec`:

- `cryptovec/src/cryptovec.rs`
  - unchecked capacity growth
  - unchecked length arithmetic in growth callers
  - raw allocation and reallocation paths coupled to those sizes
- `cryptovec/src/platform/unix.rs`
  - `mlock` / `munlock` previously accepted zero-length calls and performed null-pointer validation inside the `unsafe` OS-call path

There are two relevant reachability stories:

1. current local reachability in `russh`

- `russh/src/keys/agent/client.rs`
  - `AgentClient::read_response()` read a peer-supplied `u32` length and then resized `self.buf` to that value before reading the payload
- `russh/src/keys/agent/server.rs`
  - `Connection::run()` read a peer-supplied `u32` length and then resized `self.buf` to that value before reading the payload

This is the path that still existed in current `0.60.x` releases before the fix, although by then those buffers were no longer `CryptoVec`.

2. historical remote reachability in older `russh`

- before commit `712e32b` (first released in `v0.58.0`), non-secret transport and compression buffers in `russh` still used `CryptoVec`
- I verified this in a detached pre-`712e32b` worktree by adding and running:
  - `cipher::tests::remote_packet_length_grows_transport_cryptovec_buffer`
  - `compression::tests::remote_compressed_payload_expands_cryptovec_output`
- those tests show that remote SSH traffic could grow `CryptoVec` through:
  - transport packet reads
  - zlib decompression output

Also added a constrained-memory reproduction in that historical worktree:

- `compression::tests::remote_compressed_payload_can_crash_under_memory_limit`

That test re-execs the test binary under `prlimit --as=134217728`, decompresses a highly compressible payload that expands to `96 MiB`, and reliably aborts in the old Unix `CryptoVec` path when `NonNull::new_unchecked()` receives a null pointer after allocation failure.

The prepared patch does two things:

1. hardens `CryptoVec` itself
   - checked capacity growth
   - checked length arithmetic
   - immediate allocation-failure handling
   - zero-length `mlock` / `munlock` no-ops
   - explicit null-pointer validation before entering the Unix `unsafe` locking calls

2. hardens the real untrusted-input path
   - caps agent frame lengths at `256 * 1024` on both client and server before resizing buffers

This cap matches OpenSSH’s agent framing guardrail.

### PoC
The following end-to-end tests demonstrate the real untrusted-input path by feeding oversized peer-controlled agent frame lengths into the public client and server flows and asserting that they are rejected before buffer growth.

Client-side agent reply path:

```rust
#[test]
fn oversized_agent_response_is_rejected_before_allocation() -> std::io::Result<()> {
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()?;

    runtime.block_on(async {
        let (mut writer, reader) = tokio::io::duplex(64);
        let server = tokio::spawn(async move {
            let mut frame = [0u8; 4];
            writer.read_exact(&mut frame).await?;
            let len = BigEndian::read_u32(&frame) as usize;
            let mut body = vec![0; len];
            writer.read_exact(&mut body).await?;

            BigEndian::write_u32(&mut frame, (MAX_AGENT_FRAME_LEN + 1) as u32);
            writer.write_all(&frame).await?;
            Ok::<(), std::io::Error>(())
        });

        let mut client = AgentClient::connect(reader);
        let err = client.request_identities().await.unwrap_err();
        assert!(matches!(err, Error::AgentProtocolError));
        server.await.expect("server task")?;
        Ok::<(), std::io::Error>(())
    })?;

    Ok(())
}
```

Server-side agent request path:

```rust
#[test]
fn oversized_agent_request_is_rejected_before_allocation() -> std::io::Result<()> {
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()?;

    runtime.block_on(async {
        let (server, mut client) = tokio::io::duplex(64);
        let connection = Connection {
            lock: Lock(std::sync::Arc::new(std::sync::RwLock::new(crate::CryptoVec::new()))),
            keys: KeyStore(std::sync::Arc::new(std::sync::RwLock::new(
                std::collections::HashMap::new(),
            ))),
            agent: Some(()),
            s: server,
            buf: Vec::new(),
        };
        let server = tokio::spawn(async move { connection.run().await });

        let mut frame = [0u8; 4];
        BigEndian::write_u32(&mut frame, (MAX_AGENT_FRAME_LEN + 1) as u32);
        client.write_all(&frame).await?;
        drop(client);

        let err = server.await.expect("server task").unwrap_err();
        assert!(matches!(err, Error::AgentProtocolError));
        Ok::<(), std::io::Error>(())
    })?;

    Ok(())
}
```

These tests pass on the fixed branch and fail on unfixed `v0.60.2`, where oversized agent frame lengths are not rejected at the framing boundary.

For historical `russh < 0.58.0`, I also verified remote reachability into `CryptoVec` in a detached pre-`712e32b` worktree (`91d431d`, package version `0.57.1`).

Transport packet read path:

```rust
#[test]
fn remote_packet_length_grows_transport_cryptovec_buffer() -> std::io::Result<()> {
    let runtime = tokio::runtime::Builder::new_current_thread()
        .enable_all()
        .build()?;

    runtime.block_on(async {
        let packet_len = MAXIMUM_PACKET_LEN;
        let (mut writer, mut reader) = tokio::io::duplex(packet_len + 4);
        let writer_task = tokio::spawn(async move {
            let mut packet = vec![0u8; packet_len + 4];
            packet[..4].copy_from_slice(&(packet_len as u32).to_be_bytes());
            writer.write_all(&packet).await?;
            Ok::<(), std::io::Error>(())
        });

        let mut buffer = SSHBuffer::new();
        let mut cipher = clear::Key;
        let n = read(&mut reader, &mut buffer, &mut cipher).await.unwrap();

        assert_eq!(n, packet_len + 4);
        assert_eq!(buffer.buffer.len(), packet_len + 4);
        assert_eq!(&buffer.buffer[..4], &(packet_len as u32).to_be_bytes());

        writer_task.await.expect("writer task")?;
        Ok::<(), std::io::Error>(())
    })?;

    Ok(())
}
```

Compression growth path:

```rust
#[test]
fn remote_compressed_payload_expands_cryptovec_output() {
    let payload = vec![b'A'; 64 * 1024];

    let compression = Compression::new(&ZLIB);
    let mut compressor = Compress::None;
    let mut decompressor = Decompress::None;
    compression.init_compress(&mut compressor);
    compression.init_decompress(&mut decompressor);

    let mut compressed = CryptoVec::new();
    let encoded = compressor
        .compress(&payload, &mut compressed)
        .expect("compress")
        .to_vec();

    let mut output = CryptoVec::new();
    let decoded = decompressor
        .decompress(&encoded, &mut output)
        .expect("decompress");

    assert_eq!(decoded.len(), payload.len());
    assert_eq!(decoded, payload.as_slice());
    assert!(encoded.len() < output.len());
}
```

Constrained-memory crash reproduction for the historical remote compression path:

```rust
#[test]
fn remote_compressed_payload_can_crash_under_memory_limit() {
    const CHILD_ENV: &str = "RUSSH_REMOTE_COMPRESS_CRASH_CHILD";

    if std::env::var_os(CHILD_ENV).is_some() {
        let payload = vec![b'A'; 96 * 1024 * 1024];

        let compression = Compression::new(&ZLIB);
        let mut compressor = Compress::None;
        let mut decompressor = Decompress::None;
        compression.init_compress(&mut compressor);
        compression.init_decompress(&mut decompressor);

        let mut compressed = CryptoVec::new();
        let encoded = compressor
            .compress(&payload, &mut compressed)
            .expect("compress")
            .to_vec();

        let mut output = CryptoVec::new();
        let decoded = decompressor
            .decompress(&encoded, &mut output)
            .expect("decompress");
        assert_eq!(decoded.len(), payload.len());
        return;
    }

    let exe = std::env::current_exe().expect("current exe");
    let status = Command::new("prlimit")
        .args([
            "--as=134217728",
            "--",
            exe.to_str().expect("utf8 exe path"),
            "--exact",
            "compression::tests::remote_compressed_payload_can_crash_under_memory_limit",
            "--nocapture",
        ])
        .env(CHILD_ENV, "1")
        .status()
        .expect("spawn child");

    assert!(
        !status.success(),
        "expected child to fail under constrained address space"
    );
}
```

On that historical worktree, the constrained-memory child aborts in the old Unix `CryptoVec` path with:

```text
unsafe precondition(s) violated: NonNull::new_unchecked requires that the pointer is non-null
thread caused non-unwinding panic. aborting.
```

To run the reproduced checks:

```bash
cargo test -p russh oversized_agent_response_is_rejected_before_allocation -- --nocapture
cargo test -p russh oversized_agent_request_is_rejected_before_allocation -- --nocapture
cargo test -p russh-cryptovec
```

Historical pre-`0.58.0` checks were run from the detached `91d431d` worktree with:

```bash
cargo test --offline -p russh remote_packet_length_grows_transport_cryptovec_buffer -- --nocapture
cargo test --offline -p russh remote_compressed_payload_expands_cryptovec_output -- --nocapture
cargo test --offline -p russh remote_compressed_payload_can_crash_under_memory_limit -- --nocapture
```

### Impact
This is a memory-safety hardening issue with demonstrated untrusted-input reachability.

What is demonstrated:

- current local agent peers could previously reach allocation growth directly from attacker-controlled frame lengths
- historical remote SSH traffic could previously reach `CryptoVec` through transport and compression buffers in `russh < 0.58.0`
- under constrained memory, the historical remote compression path can be turned into a process abort in the old Unix `CryptoVec` code
- the fixed code now rejects oversized agent frames early and hardens the underlying allocation paths

What is not demonstrated:

- practical code execution
- a demonstrated integrity or confidentiality break

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-g9f8-wqj9-fjw5
- https://nvd.nist.gov/vuln/detail/CVE-2026-46673
- https://github.com/Eugeny/russh
- https://rustsec.org/advisories/RUSTSEC-2026-0153.html
- https://rustsec.org/advisories/RUSTSEC-2026-0154.html
