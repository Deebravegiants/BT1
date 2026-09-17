# [H] ALPINE-CVE-2022-33743

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-33743
Ecosystem: Alpine:v3.14, Alpine:v3.15
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-07-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-33743
Type: osv

## Affected
- Alpine:v3.14: `xen` — affected >=0 <4.15.4-r0
- Alpine:v3.15: `xen` — affected >=0 <4.15.4-r0

## Details
network backend may cause Linux netfront to use freed SKBs While adding logic to support XDP (eXpress Data Path), a code label was moved in a way allowing for SKBs having references (pointers) retained for further processing to nevertheless be freed.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-33743
