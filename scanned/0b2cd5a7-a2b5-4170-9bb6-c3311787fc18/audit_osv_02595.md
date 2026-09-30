# [M] ALPINE-CVE-2022-33749

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2022-33749
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L)
Published: 2022-10-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-33749
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.18: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.19: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.20: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.21: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.22: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.23: `xen` — affected >=0 <4.17.0-r0
- Alpine:v3.24: `xen` — affected >=0 <4.17.0-r0

## Details
XAPI open file limit DoS It is possible for an unauthenticated client on the network to cause XAPI to hit its file-descriptor limit. This causes XAPI to be unable to accept new requests for other (trusted) clients, and blocks XAPI from carrying out any tasks that require the opening of file descriptors.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-33749
