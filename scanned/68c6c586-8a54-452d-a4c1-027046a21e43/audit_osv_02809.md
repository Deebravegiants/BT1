# [M] ALPINE-CVE-2023-28320

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-28320
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.9 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-05-26
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-28320
Type: osv

## Affected
- Alpine:v3.15: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.16: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.17: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.18: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.1.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.1.0-r0

## Details
A denial of service vulnerability exists in curl <v8.1.0 in the way libcurl provides several different backends for resolving host names, selected at build time. If it is built to use the synchronous resolver, it allows name resolves to time-out slow operations using `alarm()` and `siglongjmp()`. When doing this, libcurl used a global buffer that was not mutex protected and a multi-threaded application might therefore crash or otherwise misbehave.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-28320
