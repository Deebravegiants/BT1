# [H] ALPINE-CVE-2024-2398

## Summary
Severity: High
Advisory: ALPINE-CVE-2024-2398
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.6 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:L/A:L)
Published: 2024-03-27
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-2398
Type: osv

## Affected
- Alpine:v3.17: `curl` — affected >=7.44.0 <8.7.1-r0
- Alpine:v3.18: `curl` — affected >=7.44.0 <8.7.1-r0
- Alpine:v3.19: `curl` — affected >=7.44.0 <8.7.1-r0
- Alpine:v3.20: `curl` — affected >=7.44.0 <8.7.1-r0
- Alpine:v3.21: `curl` — affected >=7.44.0 <8.7.1-r0
- Alpine:v3.22: `curl` — affected >=7.44.0 <8.7.1-r0
- Alpine:v3.23: `curl` — affected >=7.44.0 <8.7.1-r0
- Alpine:v3.24: `curl` — affected >=7.44.0 <8.7.1-r0

## Details
When an application tells libcurl it wants to allow HTTP/2 server push, and the amount of received headers for the push surpasses the maximum allowed limit (1000), libcurl aborts the server push. When aborting, libcurl inadvertently does not free all the previously allocated headers and instead leaks the memory.  Further, this error condition fails silently and is therefore not easily detected by an application.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-2398
