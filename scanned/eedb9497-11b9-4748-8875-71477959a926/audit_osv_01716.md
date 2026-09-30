# [H] ALPINE-CVE-2020-11080

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-11080
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-06-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-11080
Type: osv

## Affected
- Alpine:v3.10: `nghttp2` — affected >=0 <1.39.2-r1
- Alpine:v3.11: `nghttp2` — affected >=0 <1.40.0-r1
- Alpine:v3.12: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.13: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.14: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.15: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.16: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.17: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.18: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.19: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.20: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.21: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.22: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.23: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.24: `nghttp2` — affected >=0 <1.41.0-r0
- Alpine:v3.9: `nghttp2` — affected >=0 <1.35.1-r2
- Alpine:v3.11: `nodejs` — affected >=0 <12.20.1-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.18.3-r0
- Alpine:v3.13: `nodejs` — affected >=0 <12.18.0-r0
- Alpine:v3.14: `nodejs` — affected >=0 <12.18.0-r0
- Alpine:v3.15: `nodejs` — affected >=0 <12.18.0-r0
- Alpine:v3.16: `nodejs` — affected >=0 <12.18.0-r0
- Alpine:v3.17: `nodejs` — affected >=0 <12.18.0-r0
- Alpine:v3.18: `nodejs` — affected >=0 <12.18.0-r0
- Alpine:v3.19: `nodejs` — affected >=0 <12.18.0-r0

## Details
In nghttp2 before version 1.41.0, the overly large HTTP/2 SETTINGS frame payload causes denial of service. The proof of concept attack involves a malicious client constructing a SETTINGS frame with a length of 14,400 bytes (2400 individual settings entries) over and over again. The attack causes the CPU to spike at 100%. nghttp2 v1.41.0 fixes this vulnerability. There is a workaround to this vulnerability. Implement nghttp2_on_frame_recv_callback callback, and if received frame is SETTINGS frame and the number of settings entries are large (e.g., > 32), then drop the connection.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-11080
