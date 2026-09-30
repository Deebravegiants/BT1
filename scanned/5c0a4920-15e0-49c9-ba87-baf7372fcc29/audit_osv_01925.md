# [C] ALPINE-CVE-2020-27780

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2020-27780
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2020-12-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-27780
Type: osv

## Affected
- Alpine:v3.13: `linux-pam` — affected >=1.5.0 <1.5.1
- Alpine:v3.14: `linux-pam` — affected >=1.5.0 <1.5.1-r0
- Alpine:v3.15: `linux-pam` — affected >=1.5.0 <1.5.1-r0
- Alpine:v3.16: `linux-pam` — affected >=1.5.0 <1.5.1-r0
- Alpine:v3.17: `linux-pam` — affected >=1.5.0 <1.5.1-r0
- Alpine:v3.18: `linux-pam` — affected >=1.5.0 <1.5.1-r0
- Alpine:v3.19: `linux-pam` — affected >=1.5.0 <1.5.1-r0
- Alpine:v3.20: `linux-pam` — affected >=1.5.0 <1.5.1-r0
- Alpine:v3.21: `linux-pam` — affected >=1.5.0 <1.5.1-r0
- Alpine:v3.22: `linux-pam` — affected >=1.5.0 <1.5.1-r0
- Alpine:v3.23: `linux-pam` — affected >=1.5.0 <1.5.1-r0
- Alpine:v3.24: `linux-pam` — affected >=1.5.0 <1.5.1-r0

## Details
A flaw was found in Linux-Pam in versions prior to 1.5.1 in the way it handle empty passwords for non-existing users. When the user doesn't exist PAM try to authenticate with root and in the case of an empty password it successfully authenticate.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-27780
