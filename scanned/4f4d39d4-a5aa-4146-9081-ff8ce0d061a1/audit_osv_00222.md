# [C] ALPINE-CVE-2016-7415

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-7415
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2016-09-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-7415
Type: osv

## Affected
- Alpine:v3.10: `icu` — affected >=0 <58.1-r1
- Alpine:v3.11: `icu` — affected >=0 <58.1-r1
- Alpine:v3.12: `icu` — affected >=0 <58.1-r1
- Alpine:v3.13: `icu` — affected >=0 <58.1-r1
- Alpine:v3.14: `icu` — affected >=0 <58.1-r1
- Alpine:v3.15: `icu` — affected >=0 <58.1-r1
- Alpine:v3.16: `icu` — affected >=0 <58.1-r1
- Alpine:v3.17: `icu` — affected >=0 <58.1-r1
- Alpine:v3.18: `icu` — affected >=0 <58.1-r1
- Alpine:v3.19: `icu` — affected >=0 <58.1-r1
- Alpine:v3.20: `icu` — affected >=0 <58.1-r1
- Alpine:v3.21: `icu` — affected >=0 <58.1-r1
- Alpine:v3.22: `icu` — affected >=0 <58.1-r1
- Alpine:v3.23: `icu` — affected >=0 <58.1-r1
- Alpine:v3.24: `icu` — affected >=0 <58.1-r1
- Alpine:v3.5: `icu` — affected >=0 <57.1-r2
- Alpine:v3.6: `icu` — affected >=0 <58.1-r1
- Alpine:v3.7: `icu` — affected >=0 <58.1-r1
- Alpine:v3.8: `icu` — affected >=0 <58.1-r1
- Alpine:v3.9: `icu` — affected >=0 <58.1-r1

## Details
Stack-based buffer overflow in the Locale class in common/locid.cpp in International Components for Unicode (ICU) through 57.1 for C/C++ allows remote attackers to cause a denial of service (application crash) or possibly have unspecified other impact via a long locale string.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-7415
