# [H] ALPINE-CVE-2021-22901

## Summary
Severity: High
Advisory: ALPINE-CVE-2021-22901
Ecosystem: Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2021-06-11
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-22901
Type: osv

## Affected
- Alpine:v3.12: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.13: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.14: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.15: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.16: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.17: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.18: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.19: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.20: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.21: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.22: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.23: `curl` — affected >=7.75.0 <7.77.0-r0
- Alpine:v3.24: `curl` — affected >=7.75.0 <7.77.0-r0

## Details
curl 7.75.0 through 7.76.1 suffers from a use-after-free vulnerability resulting in already freed memory being used when a TLS 1.3 session ticket arrives over a connection. A malicious server can use this in rare unfortunate circumstances to potentially reach remote code execution in the client. When libcurl at run-time sets up support for TLS 1.3 session tickets on a connection using OpenSSL, it stores pointers to the transfer in-memory object for later retrieval when a session ticket arrives. If the connection is used by multiple transfers (like with a reused HTTP/1.1 connection or multiplexed HTTP/2 connection) that first transfer object might be freed before the new session is established on that connection and then the function will access a memory buffer that might be freed. When using that memory, libcurl might even call a function pointer in the object, making it possible for a remote code execution if the server could somehow manage to get crafted memory content into the correct place in memory.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-22901
