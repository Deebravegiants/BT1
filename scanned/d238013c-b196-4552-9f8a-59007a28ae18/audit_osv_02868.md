# [M] ALPINE-CVE-2023-40217

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2023-40217
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:N/A:N)
Published: 2023-08-25
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-40217
Type: osv

## Affected
- Alpine:v3.15: `python3` — affected >=0 <3.9.18-r0
- Alpine:v3.16: `python3` — affected >=0 <3.10.13-r0
- Alpine:v3.17: `python3` — affected >=0 <3.10.13-r0
- Alpine:v3.18: `python3` — affected >=0 <3.11.5-r0
- Alpine:v3.19: `python3` — affected >=0 <3.11.5-r0
- Alpine:v3.20: `python3` — affected >=0 <3.11.5-r0
- Alpine:v3.21: `python3` — affected >=0 <3.11.5-r0
- Alpine:v3.22: `python3` — affected >=0 <3.11.5-r0
- Alpine:v3.23: `python3` — affected >=0 <3.11.5-r0
- Alpine:v3.24: `python3` — affected >=0 <3.11.5-r0

## Details
An issue was discovered in Python before 3.8.18, 3.9.x before 3.9.18, 3.10.x before 3.10.13, and 3.11.x before 3.11.5. It primarily affects servers (such as HTTP servers) that use TLS client authentication. If a TLS server-side socket is created, receives data into the socket buffer, and then is closed quickly, there is a brief window where the SSLSocket instance will detect the socket as "not connected" and won't initiate a handshake, but buffered data will still be readable from the socket buffer. This data will not be authenticated if the server-side TLS peer is expecting client certificate authentication, and is indistinguishable from valid TLS stream data. Data is limited in size to the amount that will fit in the buffer. (The TLS connection cannot directly be used for data exfiltration because the vulnerable code path requires that the connection be closed on initialization of the SSLSocket.)

## References
- https://security.alpinelinux.org/vuln/CVE-2023-40217
