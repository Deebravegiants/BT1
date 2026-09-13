# [H] ALPINE-CVE-2022-40284

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-40284
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-11-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-40284
Type: osv

## Affected
- Alpine:v3.17: `ntfs-3g` — affected >=0 <2022.10.3-r0
- Alpine:v3.18: `ntfs-3g` — affected >=0 <2022.10.3-r0
- Alpine:v3.19: `ntfs-3g` — affected >=0 <2022.10.3-r0
- Alpine:v3.20: `ntfs-3g` — affected >=0 <2022.10.3-r0
- Alpine:v3.21: `ntfs-3g` — affected >=0 <2022.10.3-r0
- Alpine:v3.22: `ntfs-3g` — affected >=0 <2022.10.3-r0
- Alpine:v3.23: `ntfs-3g` — affected >=0 <2022.10.3-r0
- Alpine:v3.24: `ntfs-3g` — affected >=0 <2022.10.3-r0

## Details
A buffer overflow was discovered in NTFS-3G before 2022.10.3. Crafted metadata in an NTFS image can cause code execution. A local attacker can exploit this if the ntfs-3g binary is setuid root. A physically proximate attacker can exploit this if NTFS-3G software is configured to execute upon attachment of an external storage device.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-40284
