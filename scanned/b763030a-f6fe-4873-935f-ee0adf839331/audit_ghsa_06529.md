# [M] Russh: client wrong-length X25519 `clone_from_slice` panic (pre-auth DoS)

## Summary
Severity: Medium
Advisory: GHSA-g9hv-x236-4qp3
CVE: CVE-2026-73429
CWE: CWE-704, CWE-754
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L (CVSS_V3)
Published: 2026-07-24
Source: https://github.com/advisories/GHSA-g9hv-x236-4qp3
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0 <0.62.4

## Details
### Summary
A malicious SSH server can crash a `russh` client session with a single
malformed key-exchange reply, causing a pre-authentication Denial-of-Service
before the server host key is verified. The embedding process itself stays
up, but the connection is killed deterministically.

### Details
Every *other* kex path in `russh` validates the peer ephemeral length before
cloning:

- `Curve25519Kex::server_dh` (`russh/src/kex/curve25519.rs:61-65`) checks
  `if pubkey_len != 32 { return Err(crate::Error::Kex); }` before
  `clone_from_slice`.
- The hybrid ML-KEM, ECDH-NIST, and DH/GEX paths all validate lengths.

Only the client-side curve25519 `compute_shared_secret` is missing the check.
This asymmetric validation gap makes the bug easy to miss in code review: a
malicious *client* cannot panic a `russh` server this way (the server path
checks the length), but a malicious *server* can panic a `russh` client.

Incriminated source code (repo-relative paths):

- Vulnerable `compute_shared_secret`: `russh/src/kex/curve25519.rs:110-117` (panic at line 113)
- Client-side entry point: `russh/src/client/kex.rs:266-277` (`KEX_ECDH_REPLY` → `Bytes::decode` → `compute_shared_secret`)
- Server-side contrast (has the length check): `russh/src/kex/curve25519.rs:51-88` (`server_dh`)
- Session spawn site: `russh/src/client/mod.rs` (`connect_stream` → `russh_util::runtime::spawn`)
- Runtime wrapper: `russh-util/src/runtime.rs:37-48` (`spawn` wraps `tokio::spawn`; panic surfaces as `JoinError`)

### PoC
A standalone, self-contained Cargo PoC is provided in
`vuln_poc/vuln_002_client_wronglen_x25519_panic/` in this repo. It installs a
global panic hook that sets an `AtomicBool` if any panic fires, starts a
malicious raw SSH server on `127.0.0.1:0` that completes the SSH id and
`KEXINIT` exchange, reads the client `KEX_ECDH_INIT`, and sends
`KEX_ECDH_REPLY` with a 16-byte server ephemeral (instead of 32) and a fake
signature. It then calls `russh::client::connect` with `Preferred::kex` set
to `curve25519-sha256` and a handler that accepts any server key (the check
is never reached because the client panics first) and prints a clear verdict.

Build & run:

```bash
cd vuln_poc/vuln_002_client_wronglen_x25519_panic
cargo run --release
```

Expected output (verdict line, from a successful reproduction):

```
[poc] panic captured: panicked at russh/src/kex/curve25519.rs:113:25:
  copy_from_slice: source slice length (16) does not match destination slice length (32)
[!] Vulnerability reproduced: russh client panicked in Curve25519Kex::compute_shared_secret
  on a wrong-length (16-byte) server ephemeral before verifying the host key signature
  (pre-auth client DoS).
```

The malicious payload is the `f` field of `KEX_ECDH_REPLY`:

```
MSG_KEX_ECDH_REPLY (1 byte, value 0x1f)
  string K_S            (server host key blob — any valid-looking bytes)
  string f              (server ephemeral — 16 bytes of 0x00 instead of 32)
  string signature      (fake; never verified by the client)
```

The length prefix of `f` is `4` (u32 BE) = 16, followed by 16 bytes. The
`russh` client decodes this into `exchange.server_ephemeral` (a `Vec<u8>` of
length 16) and passes it to `compute_shared_secret`, which panics on
`clone_from_slice`.

### Impact
**What kind of vulnerability:** CWE-704 (incorrect type conversion / cast —
`clone_from_slice` length mismatch) → deterministic panic → pre-authentication
per-connection Denial-of-Service. The attacker does not need the server's
private key; any network position that can deliver a malformed
`KEX_ECDH_REPLY` (a rogue server, or a MitM before authentication) suffices.

**Who is impacted:** any deployment that uses `russh::client::connect` (or
`connect_stream`) to connect to an attacker-controlled or MitM-reachable SSH
server, and that negotiates `curve25519-sha256` (the default and
most-preferred kex algorithm in `russh`). A single malformed
`KEX_ECDH_REPLY` kills the client session; the attack is deterministic and
single-packet. The panic is isolated to the spawned session task
(`tokio::spawn` catches it and surfaces a `JoinError`), so the embedding
process keeps running — the impact is per-connection DoS, not process crash,
unless the embedder installs a custom panic hook that calls
`std::process::abort`.

**Workaround:** until a fix is released, clients can reduce exposure by
disabling `curve25519-sha256` in the `Preferred::kex` list and preferring a
kex algorithm whose peer-ephemeral length is validated (e.g. the ECDH-NIST
or DH/GEX paths). This is a mitigation, not a fix.

**Suggested fix (one-line length check, mirrors the existing server-side
`server_dh` check):**

```rust
// russh/src/kex/curve25519.rs, at the top of compute_shared_secret:
fn compute_shared_secret(&mut self, remote_pubkey_: &[u8]) -> Result<(), crate::Error> {
    if remote_pubkey_.len() != 32 {
        return Err(crate::Error::Kex);
    }
    let local_secret = self.local_secret.take().ok_or(crate::Error::KexInit)?;
    let mut remote_pubkey = MontgomeryPoint([0; 32]);
    remote_pubkey.0.clone_from_slice(remote_pubkey_);
    let shared = local_secret * remote_pubkey;
    self.shared_secret = Some(shared);
    Ok(())
}
```

This makes the client-side `compute_shared_secret` consistent with the
existing server-side `server_dh` check at `russh/src/kex/curve25519.rs:61-65`
and with the other kex paths that already validate peer ephemeral lengths.

[vuln_poc.zip](https://github.com/user-attachments/files/29255207/vuln_poc.zip)

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-g9hv-x236-4qp3
- https://github.com/Eugeny/russh/commit/a7fc1eb5717264e31c3c5f7dd849b73989a08f3d
- https://github.com/Eugeny/russh
- https://github.com/Eugeny/russh/releases/tag/v0.62.4
