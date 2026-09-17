# [H] ALPINE-CVE-2017-9078

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-9078
Ecosystem: Alpine:v3.4, Alpine:v3.5
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-05-19
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-9078
Type: osv

## Affected
- Alpine:v3.4: `dropbear` — affected >=0 <2017.75-r0
- Alpine:v3.5: `dropbear` — affected >=0 <2017.75-r0

## Details
The server in Dropbear before 2017.75 might allow post-authentication root remote code execution because of a double free in cleanup of TCP listeners when the -a option is enabled.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-9078
