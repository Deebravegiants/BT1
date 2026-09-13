# [C] ALPINE-CVE-2017-1000257

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2017-1000257
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.1 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:H)
Published: 2017-10-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-1000257
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.11: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.12: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.13: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.14: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.15: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.16: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.17: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.18: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.19: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.20: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.21: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.22: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.23: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.24: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.3: `curl` — affected >=0 <7.55.0-r2
- Alpine:v3.4: `curl` — affected >=0 <7.55.0-r2
- Alpine:v3.5: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.6: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.7: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.8: `curl` — affected >=0 <7.56.1-r0
- Alpine:v3.9: `curl` — affected >=0 <7.56.1-r0

## Details
An IMAP FETCH response line indicates the size of the returned data, in number of bytes. When that response says the data is zero bytes, libcurl would pass on that (non-existing) data with a pointer and the size (zero) to the deliver-data function. libcurl's deliver-data function treats zero as a magic number and invokes strlen() on the data to figure out the length. The strlen() is called on a heap based buffer that might not be zero terminated so libcurl might read beyond the end of it into whatever memory lies after (or just crash) and then deliver that to the application as if it was actually downloaded.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-1000257
