# [M] ALPINE-CVE-2022-42319

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-42319
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:C/C:N/I:N/A:H)
Published: 2022-11-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-42319
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=4.9.0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=4.9.0 <4.15.4-r0
- Alpine:v3.16: `xen` — affected >=4.9.0 <4.16.3-r0
- Alpine:v3.17: `xen` — affected >=4.9.0 <4.16.3-r0
- Alpine:v3.18: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.19: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.20: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.21: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.22: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.23: `xen` — affected >=4.9.0 <4.17.0-r0
- Alpine:v3.24: `xen` — affected >=4.9.0 <4.17.0-r0

## Details
Xenstore: Guests can cause Xenstore to not free temporary memory When working on a request of a guest, xenstored might need to allocate quite large amounts of memory temporarily. This memory is freed only after the request has been finished completely. A request is regarded to be finished only after the guest has read the response message of the request from the ring page. Thus a guest not reading the response can cause xenstored to not free the temporary memory. This can result in memory shortages causing Denial of Service (DoS) of xenstored.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-42319
