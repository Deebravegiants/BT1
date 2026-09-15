# [M] ALPINE-CVE-2025-1153

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2025-1153
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2025-02-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-1153
Type: osv

## Affected
- Alpine:v3.21: `binutils` — affected >=0 <2.43.1-r3
- Alpine:v3.22: `binutils` — affected >=0 <2.44-r2
- Alpine:v3.23: `binutils` — affected >=0 <2.44-r2
- Alpine:v3.24: `binutils` — affected >=0 <2.44-r2

## Details
A vulnerability classified as problematic was found in GNU Binutils 2.43/2.44. Affected by this vulnerability is the function bfd_set_format of the file format.c. The manipulation leads to memory corruption. The attack can be launched remotely. The complexity of an attack is rather high. The exploitation appears to be difficult. Upgrading to version 2.45 is able to address this issue. The identifier of the patch is 8d97c1a53f3dc9fd8e1ccdb039b8a33d50133150. It is recommended to upgrade the affected component.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-1153
