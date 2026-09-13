# [M] ALPINE-CVE-2024-6874

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-6874
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2024-07-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-6874
Type: osv

## Affected
- Alpine:v3.17: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.18: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.19: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.20: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.21: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.22: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.23: `curl` — affected >=0 <8.9.0-r0
- Alpine:v3.24: `curl` — affected >=0 <8.9.0-r0

## Details
libcurl's URL API function
[curl_url_get()](https://curl.se/libcurl/c/curl_url_get.html) offers punycode
conversions, to and from IDN. Asking to convert a name that is exactly 256
bytes, libcurl ends up reading outside of a stack based buffer when built to
use the *macidn* IDN backend. The conversion function then fills up the
provided buffer exactly - but does not null terminate the string.

This flaw can lead to stack contents accidently getting returned as part of
the converted string.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-6874
