# [M] ALPINE-CVE-2018-15473

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2018-15473
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2018-08-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-15473
Type: osv

## Affected
- Alpine:v3.10: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.11: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.12: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.13: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.14: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.15: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.16: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.17: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.18: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.19: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.20: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.21: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.22: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.23: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.24: `openssh` — affected >=0 <7.7_p1-r4
- Alpine:v3.5: `openssh` — affected >=0 <7.4_p1-r2
- Alpine:v3.6: `openssh` — affected >=0 <7.5_p1-r3
- Alpine:v3.7: `openssh` — affected >=0 <7.5_p1-r9
- Alpine:v3.8: `openssh` — affected >=0 <7.7_p1-r3
- Alpine:v3.9: `openssh` — affected >=0 <7.7_p1-r4

## Details
OpenSSH through 7.7 is prone to a user enumeration vulnerability due to not delaying bailout for an invalid authenticating user until after the packet containing the request has been fully parsed, related to auth2-gss.c, auth2-hostbased.c, and auth2-pubkey.c.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-15473
