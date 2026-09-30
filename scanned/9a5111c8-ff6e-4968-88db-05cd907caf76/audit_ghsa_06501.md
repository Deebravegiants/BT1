# [H] Netty SPDY SETTINGS frame count materializes unbounded settings map

## Summary
Severity: High
Advisory: GHSA-6jqx-86gh-f27w
CVE: CVE-2026-55831
CWE: CWE-400
Ecosystem: Maven
CVSS: CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H (CVSS_V3)
Published: 2026-07-22
Source: https://github.com/advisories/GHSA-6jqx-86gh-f27w
Type: github-advisory

## Affected
- Maven: `io.netty:netty-codec-http` — affected >=4.2.0.Final <4.2.16.Final
- Maven: `io.netty:netty-codec-http` — affected >=4.1.0.Final <4.1.136.Final

## Details
### Summary
Netty's SPDY SETTINGS decoder accepts a peer-declared SETTINGS entry count up to the 24-bit frame-length limit and materializes every unique setting ID in `DefaultSpdySettingsFrame` without an implementation-level count cap. A remote SPDY/3.1 peer can send one syntactically valid roughly 2 MiB SETTINGS frame that creates 262144 map entries, amplifying network input into heap growth and ordered-map insertion work.

### Details
Inbound SPDY bytes enter `SpdyFrameCodec.decode()` and are passed directly to the frame decoder. The decoder reads the peer-controlled flags and 24-bit frame length from the common header, then accepts SETTINGS frames with only `length >= 4`. For SETTINGS payloads, it reads the peer-controlled `numSettings` field and validates only that the remaining payload is divisible into 8-byte entries and exactly matches that count. Each accepted entry then supplies an attacker-controlled 24-bit ID and value, and the normal delegate path forwards it into `spdySettingsFrame.setValue()`. The sink is `DefaultSpdySettingsFrame`: it backs settings with a `TreeMap`, checks only that IDs fit the SPDY 24-bit maximum, and inserts a new `Setting` for each previously unseen ID. There is no count budget between the wire-format count validation and the TreeMap insertion site.

### PoC
[poc.zip](https://github.com/user-attachments/files/28445737/poc.zip)

run with
```bash
bash ./poc/run.sh
```

expected output:
```text
NETTY_SPDY_SETTINGS_COUNT_MAP_TRIGGERED settings_count=262144 wire_bytes=2097164 approx_heap_delta=17692272 first_value=1 last_value=262144
```

The `NETTY_SPDY_SETTINGS_COUNT_MAP_TRIGGERED` line means the harness decoded the crafted SETTINGS frame and observed all 262144 peer-selected IDs in the resulting settings map. The `wire_bytes=2097164`, `first_value=1`, and `last_value=262144` fields distinguish this from a setup failure: they show the exact oversized frame was accepted and fully materialized.

### Impact
 remote unauthenticated network peer that can speak SPDY/3.1 to a Netty pipeline containing `SpdyFrameCodec` can trigger resource-exhaustion denial of service. The required guards are satisfied by a complete valid SETTINGS frame using the expected SPDY version, a length of `4 + numSettings * 8`, and IDs within the accepted 24-bit range; the verified PoC uses `numSettings=262144` and `wire_bytes=2097164`. On that input, Netty materializes 262144 attacker-controlled entries in a TreeMap-backed `DefaultSpdySettingsFrame`, with local runs observing about 17-18 MiB of heap growth per decoded frame plus CPU work for ordered-map insertion.

## References
- https://github.com/netty/netty/security/advisories/GHSA-6jqx-86gh-f27w
- https://nvd.nist.gov/vuln/detail/CVE-2026-55831
- https://github.com/netty/netty/commit/5b68c61f37aa4a3045cba624cbea239655c9003b
- https://github.com/netty/netty/commit/bb2ff68a1fb71cb4b0eb9a9e17b66c52aff680c6
- https://github.com/netty/netty
- https://github.com/netty/netty/releases/tag/netty-4.1.136.Final
- https://github.com/netty/netty/releases/tag/netty-4.2.16.Final
