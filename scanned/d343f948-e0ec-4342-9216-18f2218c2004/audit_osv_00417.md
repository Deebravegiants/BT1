# [H] ALPINE-CVE-2017-12136

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-12136
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.8 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2017-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-12136
Type: osv

## Affected
- Alpine:v3.10: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.11: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.12: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.13: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.14: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.15: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.16: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.17: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.18: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.19: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.20: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.21: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.22: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.23: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.24: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.3: `xen` — affected >=0 <4.6.6-r0
- Alpine:v3.4: `xen` — affected >=0 <4.6.6-r0
- Alpine:v3.5: `xen` — affected >=0 <4.7.3-r0
- Alpine:v3.6: `xen` — affected >=0 <4.8.2-r0
- Alpine:v3.7: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.8: `xen` — affected >=0 <4.9.0-r1
- Alpine:v3.9: `xen` — affected >=0 <4.9.0-r1

## Details
Race condition in the grant table code in Xen 4.6.x through 4.9.x allows local guest OS administrators to cause a denial of service (free list corruption and host crash) or gain privileges on the host via vectors involving maptrack free list handling.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-12136
