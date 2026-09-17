# [H] ALPINE-CVE-2017-18594

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-18594
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2019-08-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-18594
Type: osv

## Affected
- Alpine:v3.10: `nmap` — affected >=0 <7.70-r4
- Alpine:v3.11: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.12: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.13: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.14: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.15: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.16: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.17: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.18: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.19: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.20: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.21: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.22: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.23: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.24: `nmap` — affected >=0 <7.80-r0
- Alpine:v3.7: `nmap` — affected >=0 <7.60-r3
- Alpine:v3.8: `nmap` — affected >=0 <7.70-r2
- Alpine:v3.9: `nmap` — affected >=0 <7.70-r4

## Details
nse_libssh2.cc in Nmap 7.70 is subject to a denial of service condition due to a double free when an SSH connection fails, as demonstrated by a leading \n character to ssh-brute.nse or ssh-auth-methods.nse.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-18594
