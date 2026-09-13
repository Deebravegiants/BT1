# [M] ALPINE-CVE-2016-10130

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-10130
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2017-03-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-10130
Type: osv

## Affected
- Alpine:v3.10: `libgit2` — affected >=0 <0.25.1-r0
- Alpine:v3.11: `libgit2` — affected >=0 <0.25.1-r0
- Alpine:v3.4: `libgit2` — affected >=0 <0.24.6-r0
- Alpine:v3.5: `libgit2` — affected >=0 <0.24.6-r0
- Alpine:v3.6: `libgit2` — affected >=0 <0.25.1-r0
- Alpine:v3.7: `libgit2` — affected >=0 <0.25.1-r0
- Alpine:v3.8: `libgit2` — affected >=0 <0.25.1-r0
- Alpine:v3.9: `libgit2` — affected >=0 <0.25.1-r0

## Details
The http_connect function in transports/http.c in libgit2 before 0.24.6 and 0.25.x before 0.25.1 might allow man-in-the-middle attackers to spoof servers by leveraging clobbering of the error variable.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-10130
