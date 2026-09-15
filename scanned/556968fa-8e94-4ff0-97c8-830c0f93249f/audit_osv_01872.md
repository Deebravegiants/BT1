# [H] ALPINE-CVE-2020-24606

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-24606
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2020-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-24606
Type: osv

## Affected
- Alpine:v3.10: `squid` — affected >=3.0 <4.13-r0
- Alpine:v3.11: `squid` — affected >=3.0 <4.13-r0
- Alpine:v3.12: `squid` — affected >=3.0 <4.13-r0
- Alpine:v3.13: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.14: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.15: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.16: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.17: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.18: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.19: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.20: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.21: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.22: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.23: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.24: `squid` — affected >=3.0 <4.13.0-r0
- Alpine:v3.9: `squid` — affected >=3.0 <4.13-r0

## Details
Squid before 4.13 and 5.x before 5.0.4 allows a trusted peer to perform Denial of Service by consuming all available CPU cycles during handling of a crafted Cache Digest response message. This only occurs when cache_peer is used with the cache digests feature. The problem exists because peerDigestHandleReply() livelocking in peer_digest.cc mishandles EOF.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-24606
