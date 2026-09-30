# [H] ALPINE-CVE-2023-46838

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-46838
Ecosystem: Alpine:v3.16, Alpine:v3.17, Alpine:v3.18
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-46838
Type: osv

## Affected
- Alpine:v3.16: `linux-lts` — affected >=0 <5.15.147-r1
- Alpine:v3.17: `linux-lts` — affected >=0 <5.15.147-r1
- Alpine:v3.18: `linux-lts` — affected >=0 <6.1.74-r0

## Details
Transmit requests in Xen's virtual network protocol can consist of
multiple parts.  While not really useful, except for the initial part
any of them may be of zero length, i.e. carry no data at all.  Besides a
certain initial portion of the to be transferred data, these parts are
directly translated into what Linux calls SKB fragments.  Such converted
request parts can, when for a particular SKB they are all of length
zero, lead to a de-reference of NULL in core networking code.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-46838
