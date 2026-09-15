# [M] ALPINE-CVE-2023-27537

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-27537
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-03-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-27537
Type: osv

## Affected
- Alpine:v3.14: `curl` — affected >=0 <8.0.1-r0
- Alpine:v3.15: `curl` — affected >=0 <8.0.1-r0
- Alpine:v3.16: `curl` — affected >=0 <8.0.1-r0
- Alpine:v3.17: `curl` — affected >=0 <7.88.1-r1
- Alpine:v3.18: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.0.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.0.0-r0

## Details
A double free vulnerability exists in libcurl <8.0.0 when sharing HSTS data between separate "handles". This sharing was introduced without considerations for do this sharing across separate threads but there was no indication of this fact in the documentation. Due to missing mutexes or thread locks, two threads sharing the same HSTS data could end up doing a double-free or use-after-free.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-27537
