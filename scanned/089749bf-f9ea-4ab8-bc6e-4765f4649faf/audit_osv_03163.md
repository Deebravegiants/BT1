# [M] ALPINE-CVE-2024-7264

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-7264
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2024-07-31
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-7264
Type: osv

## Affected
- Alpine:v3.18: `curl` — affected >=0 <8.9.1-r0
- Alpine:v3.19: `curl` — affected >=0 <8.9.1-r0
- Alpine:v3.20: `curl` — affected >=0 <8.9.1-r0
- Alpine:v3.21: `curl` — affected >=0 <8.9.1-r0
- Alpine:v3.22: `curl` — affected >=0 <8.9.1-r0
- Alpine:v3.23: `curl` — affected >=0 <8.9.1-r0
- Alpine:v3.24: `curl` — affected >=0 <8.9.1-r0

## Details
libcurl's ASN1 parser code has the `GTime2str()` function, used for parsing an
ASN.1 Generalized Time field. If given an syntactically incorrect field, the
parser might end up using -1 for the length of the *time fraction*, leading to
a `strlen()` getting performed on a pointer to a heap buffer area that is not
(purposely) null terminated.

This flaw most likely leads to a crash, but can also lead to heap contents
getting returned to the application when
[CURLINFO_CERTINFO](https://curl.se/libcurl/c/CURLINFO_CERTINFO.html) is used.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-7264
