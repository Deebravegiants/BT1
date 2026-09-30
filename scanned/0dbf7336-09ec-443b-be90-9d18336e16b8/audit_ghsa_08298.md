# [H] russh: Post-decompression SSH packet size was not bounded, allowing remote oversized compressed packets

## Summary
Severity: High
Advisory: GHSA-wwx6-x28x-8259
CVE: CVE-2026-46702
CWE: CWE-770
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-05-29
Source: https://github.com/advisories/GHSA-wwx6-x28x-8259
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0.34.0 <0.61.1

## Details
### Summary

When SSH compression is enabled, `russh` accepted compressed packets whose on-wire size passed the normal transport packet-length checks but whose decompressed size was much larger. This allowed a remote peer to send oversized post-decompression packets that should have been rejected.

In current releases, this is a remote denial-of-service / resource-exhaustion issue in the post-decompression receive path.

In older releases before `0.58.0`, the same remote decompression path used `CryptoVec`, which appears to make the historical impact worse.

### Details

The normal SSH transport read path enforces a packet-length limit before the packet body is read:

- `russh/src/cipher/mod.rs`

However, RFC 4253 compression is applied to the SSH `payload` field only. The `packet_length` field and MAC are computed over the compressed payload, so a packet that is reasonably sized on the wire can still expand to a much larger message body after decompression.

In `russh`, compressed packet bodies are later decompressed in:

- `russh/src/compression.rs`
- `russh/src/client/mod.rs`
- `russh/src/server/session.rs`

Before the fix, `Decompress::decompress()` grew its output buffer by repeated doubling and did not enforce a separate post-decompression ceiling. That meant a peer could send a small compressed packet that passed the normal on-wire transport length checks and then inflate it into a much larger packet after decompression.

It was verified that an attacker-crafted compressed payload can stay below the normal `256 KiB` implementation transport packet cap while still inflating above the intended post-decompression bound. In other words, this is not only a "large on-wire packet" issue.

Version detail:

- The underlying post-decompression bounds bug appears to affect `russh` as far back as `0.34.0`.
- In historical releases `>= 0.34.0, < 0.58.0`, the remote decompression path still used `CryptoVec`. Remote compressed SSH traffic could drive that path, and under constrained memory that historical code path could abort the process.
- In current-style releases `>= 0.58.0`, non-secret packet/decompression buffers were moved off `CryptoVec` and onto `Vec<u8>`, but the post-decompression size still remained unbounded. So the bug class remained reachable remotely, but the maintained-line impact is a current remote DoS / oversized-packet-acceptance issue rather than the older `CryptoVec`-based abort story.
- The maintained-line fix was verified against `0.60.2`.

Compression is not selected in a default-vs-default `russh` session because the default preference order puts `none` first. However, the default server configuration still advertises `zlib` and `zlib@openssh.com`, and server-side negotiation follows the client's preference order for common algorithms. A client that prefers compression can therefore negotiate it with a default `russh` server.

OpenSSH portable was checked at `/home/mjc/projects/openssh-portable` commit `45b30e0a5`. OpenSSH enforces a `256 KiB` transport packet cap before decompression, but it does not reuse that cap after decompression. Instead, decompression writes to an `sshbuf`, which is indirectly bounded by OpenSSH's `SSHBUF_SIZE_MAX` hard maximum of `0x8000000` bytes (`128 MiB`).

The patch direction should follow that model: add an explicit post-decompression ceiling of `128 MiB`, rather than assuming the compressed transport packet cap also bounds decompressed payload size.

Relevant OpenSSH reference points:

- `/home/mjc/projects/openssh-portable/packet.c`: `PACKET_MAX_SIZE (256 * 1024)`
- `/home/mjc/projects/openssh-portable/packet.c`: `uncompress_buffer()` inflates into `compression_buffer`
- `/home/mjc/projects/openssh-portable/sshbuf.h`: `SSHBUF_SIZE_MAX 0x8000000`

### RFC / OpenSSH Comparison

RFC 4253 section 6 defines the binary packet format:

- `packet_length`
- `padding_length`
- `payload`
- random padding
- MAC

RFC 4253 section 6.2 says that, when compression is negotiated, the `payload` field is compressed, and that `packet_length` and MAC are computed from the compressed payload. The RFC also says implementations should check that packet length is reasonable to avoid denial-of-service and buffer-overflow attacks.

That means the pre-decompression transport packet length check is necessary but not sufficient. A correct implementation still needs a reasonable bound on the decompressed payload that becomes parser input.

OpenSSH provides such a bound indirectly through `sshbuf`'s hard maximum. The `russh` fix should make the corresponding post-decompression bound explicit.

### PoC

There were two kinds of proof:

- a wire-cap sanity test showing an attacker-crafted best-compressed `DEBUG` payload can stay below the normal SSH transport packet cap while still inflating beyond the intended post-decompression bound
- direct client and server receive-path tests that exercise the oversized post-decompression behavior itself

The current in-tree regression tests are:

- `tests::compress::oversized_debug_payload_can_stay_below_wire_cap`
- `compression::tests::oversized_decompressed_packet_is_rejected`
- `client::tests::compressed_debug_is_ignored_after_client_parses_it`
- `client::tests::oversized_compressed_debug_is_rejected_before_client_ignores_it`
- `server::session::tests::compressed_debug_is_ignored_after_server_parses_it`
- `server::session::tests::oversized_compressed_debug_is_rejected_before_server_ignores_it`

The important behavior is:

1. An attacker-crafted best-compressed `DEBUG` payload can stay below the normal `256 KiB` transport packet cap while still inflating beyond `128 MiB`.
2. In the direct client and server receive paths, small compressed `DEBUG` packets are still ignored normally after parsing.
3. In the direct client and server receive paths, oversized compressed `DEBUG` packets are rejected before the implementation reaches the normal "ignore DEBUG" behavior.

The strongest PoC for severity is the unauthenticated server-side case. A malicious client can choose `zlib` in the initial key exchange, because the default server advertises it and server-side negotiation follows the client's preference order for common algorithms. After `NEWKEYS`, but before authentication, the client can send a transport-layer `SSH_MSG_DEBUG` packet whose compressed body is below the transport packet cap but whose decompressed body exceeds the post-decompression cap.

That demonstrates the `AV:N/AC:L/PR:N/UI:N` case directly: the attacker is a remote SSH client and does not need a successfully authenticated session.

```rust
fn compressed_debug_payload(payload_len: usize) -> Vec<u8> {
    let mut payload = vec![b'A'; payload_len];
    payload[0] = crate::msg::DEBUG;

    let mut encoder =
        flate2::write::ZlibEncoder::new(Vec::new(), flate2::Compression::best());
    encoder.write_all(&payload).unwrap();
    let compressed = encoder.finish().unwrap();

    assert!(
        compressed.len() < 256 * 1024,
        "oversized post-decompression payload still fits under the wire cap"
    );
    compressed
}

fn incoming_packet(compressed: Vec<u8>) -> SSHBuffer {
    let mut buffer = SSHBuffer::new();
    // maybe_decompress() receives the clear SSHBuffer after packet framing,
    // and decompresses bytes after packet_length + padding_length.
    buffer.buffer.extend_from_slice(&[0; 5]);
    buffer.buffer.extend_from_slice(&compressed);
    buffer
}

#[test]
fn unauthenticated_client_zlib_debug_is_rejected_by_server_before_auth() {
    let mut server = preauth_server_session_after_newkeys_with_zlib_decompressor();
    let oversized = MAXIMUM_DECOMPRESSED_PACKET_LEN + 1024;
    let buffer = incoming_packet(compressed_debug_payload(oversized));

    let err = server.maybe_decompress(&buffer).unwrap_err();
    assert!(
        matches!(err, crate::Error::PacketSize(len) if len > MAXIMUM_DECOMPRESSED_PACKET_LEN)
    );
}
```

The equivalent wire-level attack shape is:

```text
1. Connect to a russh server using the default compression advertisement.
2. Send SSH_MSG_KEXINIT with compression client-to-server preference:
   zlib,zlib@openssh.com,none
3. Complete key exchange and send SSH_MSG_NEWKEYS.
4. Before any SSH_MSG_USERAUTH_REQUEST, send a compressed SSH_MSG_DEBUG packet:
   - compressed packet body: < 256 KiB
   - decompressed packet body: > 128 MiB
5. Vulnerable behavior: russh accepts and inflates the packet, then reaches the
   normal DEBUG ignore path.
6. Fixed behavior: russh rejects during decompression with Error::PacketSize.
```

The direct receive-path client/server regression tests are still useful because they isolate the bug precisely. They construct the post-decryption compressed packet body passed to `maybe_decompress()` and prove that the oversized packet is rejected before normal `DEBUG` ignore handling. The server-side pre-auth variant above is the one that justifies the highest CVSS framing for this bug.

The most important targeted checks are:

```bash
cargo test -p russh oversized_debug_payload_can_stay_below_wire_cap -- --nocapture
cargo test -p russh oversized_compressed_debug_is_rejected_before_client_ignores_it -- --nocapture
cargo test -p russh oversized_compressed_debug_is_rejected_before_server_ignores_it -- --nocapture
```

Before the fix, both the direct client and direct server receive-path oversized checks went red because the compressed payload was accepted and decompressed instead of being rejected at the post-decompression boundary. After the fix, they pass.

### Impact

Suggested CVSS v3.1 for current maintained releases:

- `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`
- Score: `7.5`

Reasoning:

- `AV:N`: reachable by a remote SSH peer
- `AC:L`: straightforward once compression is enabled
- `PR:N`, `UI:N`: no prior auth or user interaction required
- `C:N`, `I:N`: confidentiality or integrity impact was not demonstrated
- `A:H`: remote peer can cause oversized post-decompression packet processing and disconnect / denial of service

Affected versions:

- historical stronger case: `russh >= 0.34.0, < 0.58.0`
- current maintained remote DoS case: `russh >= 0.58.0`, including `0.60.3`

### Fix / Patch Direction

Add an explicit maximum decompressed SSH packet size and enforce it inside `Decompress::decompress()` before returning decompressed bytes to the client or server packet parser.

The intended ceiling is `128 MiB`, matching OpenSSH portable's effective `sshbuf` hard maximum for post-decompression packet storage. The fix should reject decompression output larger than that bound with a packet-size error before normal message dispatch.

The fix should preserve normal compressed packet behavior below the cap, including `DEBUG` packets that are decompressed and then ignored through the existing normal path.

Patch branch:

```text
fix/zlib-decompression-cap
```

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-wwx6-x28x-8259
- https://nvd.nist.gov/vuln/detail/CVE-2026-46702
- https://github.com/Eugeny/russh
