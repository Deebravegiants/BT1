# [M] ALPINE-CVE-2023-29469

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-29469
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2023-04-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-29469
Type: osv

## Affected
- Alpine:v3.17: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.18: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.19: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.20: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.21: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.22: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.23: `libxml2` — affected >=0 <2.10.4-r0
- Alpine:v3.24: `libxml2` — affected >=0 <2.10.4-r0

## Details
An issue was discovered in libxml2 before 2.10.4. When hashing empty dict strings in a crafted XML document, xmlDictComputeFastKey in dict.c can produce non-deterministic values, leading to various logic and memory errors, such as a double free. This behavior occurs because there is an attempt to use the first byte of an empty string, and any value is possible (not solely the '\0' value).

## References
- https://security.alpinelinux.org/vuln/CVE-2023-29469
