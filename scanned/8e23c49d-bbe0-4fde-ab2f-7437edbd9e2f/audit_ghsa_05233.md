# [H] Hackney has unbounded buffer accumulation in WebSocket

## Summary
Severity: High
Advisory: GHSA-q8jg-fgj4-fphf
CVE: CVE-2026-47073
CWE: CWE-400
Ecosystem: Hex
CVSS: CVSS:4.0/AV:N/AC:L/AT:N/PR:N/UI:N/VC:N/VI:N/VA:H/SC:N/SI:N/SA:N (CVSS_V4)
Published: 2026-06-26
Source: https://github.com/advisories/GHSA-q8jg-fgj4-fphf
Type: github-advisory

## Affected
- Hex: `hackney` — affected >=2.0.0 <4.0.1

## Details
### Summary

The WebSocket client in `src/hackney_ws.erl` imposes no upper bound on memory consumption across three distinct code paths. In each case, an attacker-controlled WebSocket server can exhaust the connecting process's memory without any authentication or special client configuration.

### Details

**1. Handshake response buffer (`read_handshake_response/3`)**

The function accumulates received bytes into a growing buffer waiting for `\r\n\r\n`. The per-receive timeout resets on every chunk, so a server that trickles bytes indefinitely without completing the HTTP upgrade response grows the buffer until OOM. No total-size cap exists.

**2. Frame payload accumulation (`parse_payload/9`, `parse_active_payload/8`)**

`parse_payload/9` (lines 816–817 and 825–826) appends each received chunk into a `Buffer` binary via `<<Buffer/binary, MoreData/binary>>` whenever the frame parser returns `{more, ...}`. `parse_active_payload/8` does the same in active mode by appending each incoming `tcp`/`ssl` message to `#ws_data.buffer`. RFC 6455 permits payload lengths up to 2⁶³-1 bytes, and neither path validates the declared `Len` against any limit. The `recv_timeout` applies per chunk, not to the whole frame, so a slow trickle never triggers it.

**3. Fragmentation buffer (`frag_buffer`)**

The `frag_buffer` field of `#ws_data{}` accumulates continuation frames. A server that sends an unbounded stream of non-final (`nofin`) fragments without ever sending a final (`fin`) frame grows `frag_buffer` without bound.

### PoC

1. Stand up a WebSocket server and connect to it with hackney's WebSocket client.
2. Trigger any of the three paths: (a) never send `\r\n\r\n` during the handshake; (b) announce a very large frame payload and dribble bytes slowly; (c) send an endless stream of `nofin` continuation frames.
3. Observe the hackney process's memory growing until the BEAM OOM-kills it or the node crashes.

### Impact

Denial of service via unbounded memory consumption. Affects hackney 2.0.0 through 4.0.0 for any application using the WebSocket client against an attacker-controlled server. No authentication or special configuration is required on the client side. CVSS v4.0: **8.7 (HIGH)**.

## Resources

* Introduction commit: https://github.com/benoitc/hackney/commit/690cecaf236fba49526da404a5bc889a24367a3e
* Patch commit: https://github.com/benoitc/hackney/commit/ce0109e2970ace6e20ff29bae9d05c3ac22ec6dc

## References
- https://github.com/benoitc/hackney/security/advisories/GHSA-q8jg-fgj4-fphf
- https://nvd.nist.gov/vuln/detail/CVE-2026-47073
- https://github.com/benoitc/hackney/commit/ce0109e2970ace6e20ff29bae9d05c3ac22ec6dc
- https://cna.erlef.org/cves/CVE-2026-47073.html
- https://github.com/benoitc/hackney
- https://osv.dev/vulnerability/EEF-CVE-2026-47073
