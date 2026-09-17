# [M] ALPINE-CVE-2021-44141

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-44141
Ecosystem: Alpine:v3.15, Alpine:v3.16
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-02-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-44141
Type: osv

## Affected
- Alpine:v3.15: `samba` — affected >=0 <4.15.5-r0
- Alpine:v3.16: `samba` — affected >=0 <4.15.5-r0

## Details
All versions of Samba prior to 4.15.5 are vulnerable to a malicious client using a server symlink to determine if a file or directory exists in an area of the server file system not exported under the share definition. SMB1 with unix extensions has to be enabled in order for this attack to succeed.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-44141
