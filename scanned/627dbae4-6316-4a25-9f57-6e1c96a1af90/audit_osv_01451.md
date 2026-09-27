# [H] ALPINE-CVE-2019-14889

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-14889
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-12-10
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-14889
Type: osv

## Affected
- Alpine:v3.10: `libssh` — affected >=0.9.0 <0.8.8-r0
- Alpine:v3.11: `libssh` — affected >=0.9.0 <0.9.3-r0
- Alpine:v3.8: `libssh` — affected >=0.9.0 <0.7.6-r1
- Alpine:v3.9: `libssh` — affected >=0.9.0 <0.7.6-r2

## Details
A flaw was found with the libssh API function ssh_scp_new() in versions before 0.9.3 and before 0.8.8. When the libssh SCP client connects to a server, the scp command, which includes a user-provided path, is executed on the server-side. In case the library is used in a way where users can influence the third parameter of the function, it would become possible for an attacker to inject arbitrary commands, leading to a compromise of the remote target.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-14889
