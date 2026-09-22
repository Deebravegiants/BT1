# [M] ALPINE-CVE-2017-15722

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-15722
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.9 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-10-22
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-15722
Type: osv

## Affected
- Alpine:v3.10: `irssi` — affected >=0 <1.0.5-r0
- Alpine:v3.11: `irssi` — affected >=0 <1.0.5-r0
- Alpine:v3.12: `irssi` — affected >=0 <1.0.5-r0
- Alpine:v3.13: `irssi` — affected >=0 <1.0.5-r0
- Alpine:v3.14: `irssi` — affected >=0 <1.0.5-r0
- Alpine:v3.15: `irssi` — affected >=0 <1.0.5-r0
- Alpine:v3.16: `irssi` — affected >=0 <1.0.5-r0
- Alpine:v3.17: `irssi` — affected >=0 <1.0.5-r0
- Alpine:v3.6: `irssi` — affected >=0 <1.0.6-r0
- Alpine:v3.7: `irssi` — affected >=0 <1.0.5-r0
- Alpine:v3.8: `irssi` — affected >=0 <1.0.5-r0
- Alpine:v3.9: `irssi` — affected >=0 <1.0.5-r0

## Details
In certain cases, Irssi before 1.0.5 may fail to verify that a Safe channel ID is long enough, causing reads beyond the end of the string.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-15722
