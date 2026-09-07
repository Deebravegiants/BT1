# [M] Russh: SSH identification parsing accepted non-canonical client banners and did not bound pre-banner input

## Summary
Severity: Medium
Advisory: GHSA-76r6-x97p-67vr
CVE: CVE-2026-48108
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-76r6-x97p-67vr
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0.34.0-beta.1 <0.61.0

## Details
### Summary

`russh` did not enforce the SSH identification-string rules as deliberately as OpenSSH. In particular, the server-side identification reader used the same permissive path as the client, allowing pre-banner lines from clients, and the reader did not enforce a bounded number of pre-banner lines.

For a library server built on `russh`, this could allow a remote peer to hold connection setup resources in the cleartext pre-authentication phase with malformed identification input that should have been rejected early.

### Details

RFC 4253 section 4.2 defines the SSH protocol version exchange. The identification string is a single line terminated by CR LF, must fit within 255 characters including CR LF, and clients should not send pre-banner lines before their SSH identification string.

Before the fix, `russh`'s identification reader lived in:

- `russh/src/ssh_read.rs`
- `russh/src/server/mod.rs`

The same `read_ssh_id()` behavior was used for both client and server contexts. That allowed server-side parsing to accept preliminary banner lines from clients, even though RFC 4253 only describes server-side pre-identification text. The reader also discarded preliminary lines without a line-count cap, so a peer could repeatedly send short non-SSH lines and keep the connection in identification parsing until an application-level timeout or external resource limit intervened.

This also creates a remotely observable parser-state oracle inside a single connection. A client can send candidate identification lines one after another: lines not recognized as SSH identification are discarded as pre-banner text, while an accepted identification string terminates banner parsing and advances the connection into key exchange. A strict server would reject the first invalid client pre-banner line and force a reconnect for each probe. This can disclose server-side parser acceptance behavior and make fingerprinting cheaper, though it does not disclose application secrets, credentials, keys, or authenticated user data.

The patch splits the behavior between generic/server-banner-tolerant reading and stricter client-identification reading. It also adds explicit limits for line length and pre-banner line count.

Relevant branch commit:

- `3de4a68 Harden SSH identification parsing`

### RFC / OpenSSH Comparison

RFC 4253 section 4.2 says each side sends an identification string of the form `SSH-protoversion-softwareversion SP comments CR LF`. It allows a server to send other lines before its identification string, but says a client must be able to process such lines. It does not grant the same pre-banner allowance to clients.

OpenSSH portable enforces explicit identification limits:

- `/home/mjc/projects/openssh-portable/ssh.h`: `SSH_MAX_BANNER_LEN`
- `/home/mjc/projects/openssh-portable/ssh.h`: `SSH_MAX_PRE_BANNER_LINES`
- `/home/mjc/projects/openssh-portable/kex.c`: client-side handling of server pre-banner lines
- `/home/mjc/projects/openssh-portable/ssh_api.c`: rejects pre-banner lines when acting as a server

I checked `/home/mjc/projects/openssh-portable` at `45b30e0a5`. OpenSSH uses an implementation banner line limit of `8192` bytes and a pre-banner line cap of `1024`, which is more permissive than RFC 4253's 255-character identification-string limit. The relevant alignment is the parser shape: OpenSSH permits bounded pre-banner lines when reading a server banner as a client, but rejects pre-banner lines when acting as a server and reading a client identification string.

The `russh` fix follows that shape: accept bounded pre-banner lines only where the protocol allows them, and reject malformed or excessive identification input early.

### PoC

Inline highest-CVSS PoC: unauthenticated remote client pre-banner input to the server identification parser. This demonstrates `AV:N/AC:L/PR:N/UI:N`.

```rust
#[tokio::test]
async fn poc_server_accepts_client_pre_banner_before_ssh_id() {
    use russh::server;
    use tokio::io::{AsyncReadExt, AsyncWriteExt};

    let config = std::sync::Arc::new(server::Config::default());
    let (mut client, server_stream) = tokio::io::duplex(4096);

    let server = tokio::spawn(async move {
        server::run_stream(config, server_stream, NoAuthHandler).await
    });

    let mut server_id = Vec::new();
    client.read_until(b'\n', &mut server_id).await.unwrap();

    client
        .write_all(b"attacker-controlled pre-banner\r\nSSH-2.0-poc\r\n")
        .await
        .unwrap();

    let result = tokio::time::timeout(std::time::Duration::from_millis(250), server).await;

    assert!(
        result.is_err(),
        "vulnerable code keeps processing after accepting a client pre-banner before SSH identification"
    );
}
```

On vulnerable code, the server-side reader accepts the client pre-banner line and continues instead of rejecting the malformed identification input promptly. The fixed parser rejects client pre-banner lines on the server path.

### Impact

Suggested CVSS v3.1:

- `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L`
- Score: `5.3`

Reasoning:

- `AV:N`: reachable over the SSH transport connection
- `AC:L`: no special race or unusual setup is required
- `PR:N`, `UI:N`: occurs before authentication and needs no user interaction
- `C:N`, `I:N`: no confidentiality or integrity impact demonstrated
- `A:L`: malformed identification input can consume connection setup resources until rejected by timeout or external limits

Additional impact investigation did not identify a stronger confidentiality, integrity, downgrade, or code-execution primitive. The accepted client pre-banner line is discarded before key exchange and does not become part of `remote_sshid`; the final client identification string is what feeds the key-exchange transcript. `remote_sshid` is otherwise exposed to library handlers and debug formatting, but the discarded pre-banner text does not influence authentication state, strict-kex negotiation, KEX algorithm selection, or later packet framing.

One parser-boundary nuance on vulnerable code is that behavior can depend on read chunking: if a client pre-banner line and the real SSH identification line are delivered in the same read, the old parser can discard the buffered identification line and then wait or disconnect; if delivered separately, the old server path can accept the pre-banner and continue. This supports malformed pre-authentication availability impact, but not a demonstrated confidentiality or integrity impact.

### Fix / Patch Direction

Use a stricter server-side client-identification reader, enforce the RFC identification-line length, and cap preliminary banner lines. The server path should reject client pre-banner lines instead of treating them like allowed server pre-identification text.

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-76r6-x97p-67vr
- https://nvd.nist.gov/vuln/detail/CVE-2026-48108
- https://github.com/Eugeny/russh
