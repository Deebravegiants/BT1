# [H] ALPINE-CVE-2020-10531

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-10531
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2020-03-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-10531
Type: osv

## Affected
- Alpine:v3.10: `icu` — affected >=0 <64.2-r1
- Alpine:v3.11: `icu` — affected >=0 <64.2-r1
- Alpine:v3.12: `icu` — affected >=0 <65.1-r1
- Alpine:v3.13: `icu` — affected >=0 <65.1-r1
- Alpine:v3.14: `icu` — affected >=0 <65.1-r1
- Alpine:v3.15: `icu` — affected >=0 <65.1-r1
- Alpine:v3.16: `icu` — affected >=0 <65.1-r1
- Alpine:v3.17: `icu` — affected >=0 <65.1-r1
- Alpine:v3.18: `icu` — affected >=0 <65.1-r1
- Alpine:v3.19: `icu` — affected >=0 <65.1-r1
- Alpine:v3.20: `icu` — affected >=0 <65.1-r1
- Alpine:v3.21: `icu` — affected >=0 <65.1-r1
- Alpine:v3.22: `icu` — affected >=0 <65.1-r1
- Alpine:v3.23: `icu` — affected >=0 <65.1-r1
- Alpine:v3.24: `icu` — affected >=0 <65.1-r1
- Alpine:v3.8: `icu` — affected >=0 <60.2-r3
- Alpine:v3.9: `icu` — affected >=0 <62.1-r1

## Details
An issue was discovered in International Components for Unicode (ICU) for C/C++ through 66.1. An integer overflow, leading to a heap-based buffer overflow, exists in the UnicodeString::doAppend() function in common/unistr.cpp.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-10531
