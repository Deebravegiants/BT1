# [H] ALPINE-CVE-2019-6250

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-6250
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-01-13
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-6250
Type: osv

## Affected
- Alpine:v3.10: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.11: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.12: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.13: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.14: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.15: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.16: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.17: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.18: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.19: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.20: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.21: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.22: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.23: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.24: `zeromq` — affected >=0 <4.3.1-r0
- Alpine:v3.6: `zeromq` — affected >=0 <4.2.5-r0
- Alpine:v3.7: `zeromq` — affected >=0 <4.2.5-r0
- Alpine:v3.8: `zeromq` — affected >=0 <4.2.5-r0
- Alpine:v3.9: `zeromq` — affected >=0 <4.3.1-r0

## Details
A pointer overflow, with code execution, was discovered in ZeroMQ libzmq (aka 0MQ) 4.2.x and 4.3.x before 4.3.1. A v2_decoder.cpp zmq::v2_decoder_t::size_ready integer overflow allows an authenticated attacker to overwrite an arbitrary amount of bytes beyond the bounds of a buffer, which can be leveraged to run arbitrary code on the target system. The memory layout allows the attacker to inject OS commands into a data structure located immediately after the problematic buffer (i.e., it is not necessary to use a typical buffer-overflow exploitation technique that changes the flow of control).

## References
- https://security.alpinelinux.org/vuln/CVE-2019-6250
