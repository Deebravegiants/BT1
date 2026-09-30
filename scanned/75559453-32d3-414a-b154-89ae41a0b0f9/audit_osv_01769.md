# [M] ALPINE-CVE-2020-14355

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2020-14355
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.6 (CVSS:3.1/AV:N/AC:L/PR:H/UI:N/S:C/C:L/I:L/A:L)
Published: 2020-10-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-14355
Type: osv

## Affected
- Alpine:v3.15: `spice` — affected >=0 <0.15.0-r0
- Alpine:v3.16: `spice` — affected >=0 <0.15.0-r0
- Alpine:v3.17: `spice` — affected >=0 <0.15.0-r0
- Alpine:v3.18: `spice` — affected >=0 <0.15.0-r0
- Alpine:v3.19: `spice` — affected >=0 <0.15.0-r0
- Alpine:v3.20: `spice` — affected >=0 <0.15.0-r0
- Alpine:v3.21: `spice` — affected >=0 <0.15.0-r0
- Alpine:v3.22: `spice` — affected >=0 <0.15.0-r0
- Alpine:v3.23: `spice` — affected >=0 <0.15.0-r0
- Alpine:v3.24: `spice` — affected >=0 <0.15.0-r0

## Details
Multiple buffer overflow vulnerabilities were found in the QUIC image decoding process of the SPICE remote display system, before spice-0.14.2-1. Both the SPICE client (spice-gtk) and server are affected by these flaws. These flaws allow a malicious client or server to send specially crafted messages that, when processed by the QUIC image compression algorithm, result in a process crash or potential code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-14355
