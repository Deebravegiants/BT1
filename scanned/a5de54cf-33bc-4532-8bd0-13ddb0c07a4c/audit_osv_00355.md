# [M] ALPINE-CVE-2017-1000100

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2017-1000100
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 6.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:N/A:N)
Published: 2017-10-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000100
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.11: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.12: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.13: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.20: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.3: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.4: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.5: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.6: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.7: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.8: `curl` — affected >=0 <7.55.0-r0
- Alpine:v3.9: `curl` — affected >=0 <7.55.0-r0

## Details
When doing a TFTP transfer and curl/libcurl is given a URL that contains a very long file name (longer than about 515 bytes), the file name is truncated to fit within the buffer boundaries, but the buffer size is still wrongly updated to use the untruncated length. This too large value is then used in the sendto() call, making curl attempt to send more data than what is actually put into the buffer. The endto() function will then read beyond the end of the heap based buffer. A malicious HTTP(S) server could redirect a vulnerable libcurl-using client to a crafted TFTP URL (if the client hasn't restricted which protocols it allows redirects to) and trick it to send private memory contents to a remote server over UDP. Limit curl's redirect protocols with --proto-redir and libcurl's with CURLOPT_REDIR_PROTOCOLS.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000100
