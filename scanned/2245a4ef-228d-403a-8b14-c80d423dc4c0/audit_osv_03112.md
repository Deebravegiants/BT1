# [M] ALPINE-CVE-2024-45819

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-45819
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.5 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2024-12-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-45819
Type: osv

## Affected
- Alpine:v3.17: `xen` — affected >=4.8.0 <4.16.6-r3
- Alpine:v3.18: `xen` — affected >=4.8.0 <4.17.5-r2
- Alpine:v3.19: `xen` — affected >=4.8.0 <4.18.3-r2
- Alpine:v3.20: `xen` — affected >=4.8.0 <4.18.3-r2
- Alpine:v3.21: `xen` — affected >=4.8.0 <4.19.0-r1
- Alpine:v3.22: `xen` — affected >=4.8.0 <4.19.0-r1
- Alpine:v3.23: `xen` — affected >=4.8.0 <4.19.0-r1
- Alpine:v3.24: `xen` — affected >=4.8.0 <4.19.0-r1

## Details
PVH guests have their ACPI tables constructed by the toolstack.  The
construction involves building the tables in local memory, which are
then copied into guest memory.  While actually used parts of the local
memory are filled in correctly, excess space that is being allocated is
left with its prior contents.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-45819
