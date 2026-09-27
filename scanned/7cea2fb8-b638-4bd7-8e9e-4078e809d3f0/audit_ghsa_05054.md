# [M] Russh: Unchecked keyboard-interactive prompt count in client auth path

## Summary
Severity: Medium
Advisory: GHSA-g9g7-5cgw-6v28
CVE: CVE-2026-48107
CWE: CWE-20
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-06-11
Source: https://github.com/advisories/GHSA-g9g7-5cgw-6v28
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0.37.0 <0.61.0

## Details
### Summary
In the `russh` client keyboard-interactive authentication path, a malicious SSH server could send a `USERAUTH_INFO_REQUEST` with an attacker-controlled prompt count, and the client would use that raw count directly in `Vec::with_capacity(...)` before validating that enough prompt data was actually present in the packet.

This is a client-side denial-of-service / resource-exhaustion issue on the keyboard-interactive auth path.

### Details
The vulnerable code path is in:

- `russh/src/client/encrypted.rs`

When the client is in `CurrentRequest::KeyboardInteractive` state and receives `SSH_MSG_USERAUTH_INFO_REQUEST`, it parses:

1. `name`
2. `instructions`
3. `language tag`
4. `n_prompts`

Before the fix, the code then did:

```rust
let n_prompts = map_err!(u32::decode(&mut r))?;
let mut prompts = Vec::with_capacity(n_prompts.try_into().unwrap_or(0));
```

That means a malicious server could advertise an enormous `n_prompts` value even if the packet contained no prompt bodies at all.

The fix rejects inconsistent prompt counts before allocating:

```rust
let n_prompts = map_err!(u32::decode(&mut r))?;
let max_prompts = r.remaining_len() / 5;
let n_prompts = n_prompts as usize;
if n_prompts > max_prompts {
    return Err(crate::Error::Inconsistent.into());
}
let mut prompts = Vec::with_capacity(n_prompts);
```

Each prompt needs at least 4 bytes of string length plus 1 byte of echo flag, so `remaining_len() / 5` is a safe upper bound. If the declared count exceeds what the packet can actually contain, the packet is malformed and is now rejected instead of being silently truncated.

The tester did not find a same-class server-side bug in the reciprocal `USERAUTH_INFO_RESPONSE` path. The server already bounds the response count by remaining packet length before allocating.

Affected package and versions:

- package: `russh`
- earliest affected stable: `0.37.0`
- confirmed affected current release: `0.60.2`

The tester does not believe this issue affects the other crates in this workspace (`russh-config`, `russh-cryptovec`, `pageant`, or `russh-util`).

### PoC
An in-tree regression test was added:

- `client::tests::oversized_keyboard_interactive_prompt_count_is_rejected`

The test builds a client session in `WaitingAuthRequest(KeyboardInteractive)` state, feeds it a synthetic `USERAUTH_INFO_REQUEST` packet with:

- normal `name`
- normal `instructions`
- empty language tag
- `n_prompts = u32::MAX`
- no prompt bodies

On the fixed code, the client rejects the packet with `Error::Inconsistent` and does not emit a reply to the caller.

For old-code impact verification, the pre-fix path was also checked separately with a constrained-memory repro. On unfixed `upstream/main`, the same malformed packet attempted a very large allocation and failed with:

```text
memory allocation of 137438953440 bytes failed
```

Relevant verification commands:

```bash
cargo test -p russh oversized_keyboard_interactive_prompt_count_is_rejected -- --nocapture
cargo test -p russh --lib --no-default-features --features ring oversized_keyboard_interactive_prompt_count_is_rejected -- --nocapture
```

### Impact
Suggested CVSS v3.1:

- `CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H`
- Score: `6.5`

Reasoning:

- `AV:N`: reached by a malicious SSH server over the network
- `AC:L`: the packet format is straightforward
- `PR:N`: no prior authentication required
- `UI:R`: the victim must initiate a connection and proceed into keyboard-interactive auth
- `C:N`, `I:N`:  Confidentiality or integrity impact were not demonstrated
- `A:H`: the server can drive a very large allocation attempt in the client auth path, which can abort or exhaust client-side resources depending on allocator and platform behavior

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-g9g7-5cgw-6v28
- https://nvd.nist.gov/vuln/detail/CVE-2026-48107
- https://github.com/Eugeny/russh
