# [C] ALPINE-CVE-2016-8622

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2016-8622
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.2, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 9.8 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-07-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-8622
Type: osv

## Affected
- Alpine:v3.10: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.11: `curl` — affected >=0 <7.51.0
- Alpine:v3.12: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.13: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.14: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.15: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.16: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.17: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.18: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.19: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.2: `curl` — affected >=0 <7.49.1-r4
- Alpine:v3.20: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.21: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.22: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.23: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.24: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.3: `curl` — affected >=0 <7.49.1-r4
- Alpine:v3.4: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.5: `curl` — affected >=0 <7.51.0-r0
- Alpine:v3.6: `curl` — affected >=0 <7.51.0
- Alpine:v3.7: `curl` — affected >=0 <7.51.0
- Alpine:v3.8: `curl` — affected >=0 <7.51.0
- Alpine:v3.9: `curl` — affected >=0 <7.51.0-r0

## Details
The URL percent-encoding decode function in libcurl before 7.51.0 is called `curl_easy_unescape`. Internally, even if this function would be made to allocate a unscape destination buffer larger than 2GB, it would return that new length in a signed 32 bit integer variable, thus the length would get either just truncated or both truncated and turned negative. That could then lead to libcurl writing outside of its heap based buffer.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-8622
