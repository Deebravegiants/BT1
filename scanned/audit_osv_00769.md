# [H] ALPINE-CVE-2017-7868

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-7868
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2017-04-14
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-7868
Type: osv

## Affected
- Alpine:v3.10: `icu` — affected >=0 <58.2-r2
- Alpine:v3.11: `icu` — affected >=0 <58.2-r2
- Alpine:v3.12: `icu` — affected >=0 <58.2-r2
- Alpine:v3.13: `icu` — affected >=0 <58.2-r2
- Alpine:v3.14: `icu` — affected >=0 <58.2-r2
- Alpine:v3.15: `icu` — affected >=0 <58.2-r2
- Alpine:v3.16: `icu` — affected >=0 <58.2-r2
- Alpine:v3.17: `icu` — affected >=0 <58.2-r2
- Alpine:v3.18: `icu` — affected >=0 <58.2-r2
- Alpine:v3.19: `icu` — affected >=0 <58.2-r2
- Alpine:v3.2: `icu` — affected >=0 <55.1-r3
- Alpine:v3.20: `icu` — affected >=0 <58.2-r2
- Alpine:v3.21: `icu` — affected >=0 <58.2-r2
- Alpine:v3.22: `icu` — affected >=0 <58.2-r2
- Alpine:v3.23: `icu` — affected >=0 <58.2-r2
- Alpine:v3.24: `icu` — affected >=0 <58.2-r2
- Alpine:v3.3: `icu` — affected >=0 <56.1-r2
- Alpine:v3.4: `icu` — affected >=0 <57.1-r3
- Alpine:v3.5: `icu` — affected >=0 <57.1-r3
- Alpine:v3.6: `icu` — affected >=0 <58.2-r2
- Alpine:v3.7: `icu` — affected >=0 <58.2-r2
- Alpine:v3.8: `icu` — affected >=0 <58.2-r2
- Alpine:v3.9: `icu` — affected >=0 <58.2-r2

## Details
International Components for Unicode (ICU) for C/C++ before 2017-02-13 has an out-of-bounds write caused by a heap-based buffer overflow related to the utf8TextAccess function in common/utext.cpp and the utext_moveIndex32* function.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-7868
