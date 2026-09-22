# [C] ALPINE-CVE-2021-43845

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2021-43845
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.1 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2021-12-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-43845
Type: osv

## Affected
- Alpine:v3.16: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.17: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.18: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.19: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.20: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.21: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.22: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.23: `pjproject` — affected >=0 <2.12-r0
- Alpine:v3.24: `pjproject` — affected >=0 <2.12-r0

## Details
PJSIP is a free and open source multimedia communication library. In version 2.11.1 and prior, if incoming RTCP XR message contain block, the data field is not checked against the received packet size, potentially resulting in an out-of-bound read access. This affects all users that use PJMEDIA and RTCP XR. A malicious actor can send a RTCP XR message with an invalid packet size.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-43845
