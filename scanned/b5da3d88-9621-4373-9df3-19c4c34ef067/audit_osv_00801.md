# [M] ALPINE-CVE-2017-9079

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-9079
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2017-05-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9079
Type: osv

## Affected
- Alpine:v3.4: `dropbear` — affected >=0 <2017.75-r0
- Alpine:v3.5: `dropbear` — affected >=0 <2017.75-r0

## Details
Dropbear before 2017.75 might allow local users to read certain files as root, if the file has the authorized_keys file format with a command= option. This occurs because ~/.ssh/authorized_keys is read with root privileges and symlinks are followed.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9079
