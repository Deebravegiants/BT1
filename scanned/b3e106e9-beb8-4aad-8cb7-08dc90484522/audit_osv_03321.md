# [H] ALPINE-CVE-2025-5222

## Summary
Severity: High
Advisory: ALPINE-CVE-2025-5222
Ecosystem: Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.0 (CVSS:3.1/AV:L/AC:H/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2025-05-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2025-5222
Type: osv

## Affected
- Alpine:v3.19: `icu` — affected >=0 <74.1-r1
- Alpine:v3.20: `icu` — affected >=0 <74.2-r1
- Alpine:v3.21: `icu` — affected >=0 <74.2-r1
- Alpine:v3.22: `icu` — affected >=0 <76.1-r1
- Alpine:v3.23: `icu` — affected >=0 <76.1-r1
- Alpine:v3.24: `icu` — affected >=0 <76.1-r1

## Details
A stack buffer overflow was found in Internationl components for unicode (ICU ). While running the genrb binary, the 'subtag' struct overflowed at the SRBRoot::addTag function. This issue may lead to memory corruption and local arbitrary code execution.

## References
- https://security.alpinelinux.org/vuln/CVE-2025-5222
