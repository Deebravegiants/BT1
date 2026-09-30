# [H] russh has pre-auth DoS via unbounded allocation in its keyboard-interactive auth handler

## Summary
Severity: High
Advisory: GHSA-f5v4-2wr6-hqmg
CVE: CVE-2026-42189
CWE: CWE-770, CWE-789
Ecosystem: crates.io
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-04-24
Source: https://github.com/advisories/GHSA-f5v4-2wr6-hqmg
Type: github-advisory

## Affected
- crates.io: `russh` — affected >=0 <0.60.1

## Details
## Summary

A pre-authentication denial-of-service vulnerability exists in the server's keyboard-interactive authentication handler. A malicious client can crash any russh-based server that implements keyboard-interactive auth (e.g., for 2FA/TOTP) with a single malformed packet, requiring no credentials.

## Vulnerability Details

In `russh/src/server/encrypted.rs`, the function `read_userauth_info_response` decodes a `u32` count from the client's `SSH_MSG_USERAUTH_INFO_RESPONSE` and passes it directly to `Vec::with_capacity()`:

```rust
let n = map_err!(u32::decode(r))?;

// Bound both allocation and iteration by remaining packet data to
// prevent a malicious client from causing a multi-GB allocation or
// billions of loop iterations with a crafted count.
// Each response needs at least 4 bytes (length prefix).
let max_responses = r.remaining_len().saturating_add(3) / 4;
let n = (n as usize).min(max_responses);
let mut responses = Vec::with_capacity(n);
for _ in 0..n {
    responses.push(Bytes::decode(r).ok())
}
```

An attacker can send `n = 0x10000000` (268M) or larger in a minimal packet (~50 bytes after encryption). The server attempts to allocate `n * ~24 bytes` (size of `Option<Bytes>`) = ~6.4GB, causing an OOM crash.

## Attack Flow

1. Attacker connects via TCP, completes key exchange (no credentials needed -- this is the anonymous DH handshake, not authentication)
2. Sends `USERAUTH_REQUEST` with method `keyboard-interactive`
3. Server handler returns `Auth::Partial` with prompts (standard for 2FA/TOTP)
4. Attacker sends `USERAUTH_INFO_RESPONSE` with `n = 0x10000000` and no response data
5. Server calls `Vec::with_capacity(268_435_456)`, OOM killed

No authentication is required. The allocation occurs before the handler validates any credentials. The attack is repeatable faster than the server can restart.

## Affected Configurations

Any russh-based server where the `Handler::auth_keyboard_interactive` implementation returns `Auth::Partial` (i.e., sends prompts to the client). The default handler returns `Auth::reject()` and is not affected.

Source code review suggests that downstream projects using keyboard-interactive for multi-step auth (e.g., TOTP/2FA) follow the affected pattern, since returning `Auth::Partial` before credential verification is the intended API usage for prompting.

## Confirmed End-to-End PoC

There is a complete Docker-contained PoC confirming the OOM kill:
- Minimal russh server returning `Auth::Partial` for keyboard-interactive
- Python client (paramiko for key exchange) sends malformed `USERAUTH_INFO_RESPONSE`
- Container with 512MB memory limit; server is OOM-killed (exit code 137)

Available on request.

## Proposed Fix

Cap the `Vec::with_capacity` allocation to what the remaining packet data can actually contain. Each response requires at least 4 bytes (length prefix), so:

```rust
let n = map_err!(u32::decode(r))?;

// Bound both allocation and iteration by remaining packet data to
// prevent a malicious client from causing a multi-GB allocation or
// billions of loop iterations with a crafted count.
// Each response needs at least 4 bytes (length prefix).
let max_responses = r.remaining_len().saturating_add(3) / 4;
let n = (n as usize).min(max_responses);
let mut responses = Vec::with_capacity(n);
for _ in 0..n {
    responses.push(Bytes::decode(r).ok())
}
```

This bounds the allocation to at most the packet size (~256KB), while preserving the existing behavior for well-formed packets. This fix has been implemented, tested, and contributed via the temporary private fork.

## Severity

Pre-auth, remote, no credentials required, crashes the server process affecting all active sessions.

## References
- https://github.com/Eugeny/russh/security/advisories/GHSA-f5v4-2wr6-hqmg
- https://nvd.nist.gov/vuln/detail/CVE-2026-42189
- https://github.com/Eugeny/russh/commit/6c3c80a9b6d60763d6227d60fa8310e57172a4d1
- https://github.com/Eugeny/russh
- https://github.com/Eugeny/russh/releases/tag/v0.60.1
