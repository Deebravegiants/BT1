# [H] ALPINE-CVE-2021-44142

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-44142
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-02-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-44142
Type: osv

## Affected
- Alpine:v3.13: `samba` — affected >=4.14.0 <4.13.17-r0
- Alpine:v3.14: `samba` — affected >=4.14.0 <4.14.12-r0
- Alpine:v3.15: `samba` — affected >=4.14.0 <4.15.12-r0
- Alpine:v3.16: `samba` — affected >=4.14.0 <4.15.12-r0

## Details
The Samba vfs_fruit module uses extended file attributes (EA, xattr) to provide "...enhanced compatibility with Apple SMB clients and interoperability with a Netatalk 3 AFP fileserver." Samba versions prior to 4.13.17, 4.14.12 and 4.15.5 with vfs_fruit configured allow out-of-bounds heap read and write via specially crafted extended file attributes. A remote attacker with write access to extended file attributes can execute arbitrary code with the privileges of smbd, typically root.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-44142
