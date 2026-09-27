# [H] ALPINE-CVE-2018-1000168

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-1000168
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-08
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-1000168
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.11: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.12: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.13: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.14: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.15: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.16: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.17: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.18: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.19: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.20: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.21: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.22: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.23: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.24: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.8: `nodejs` — affected >=0 <8.11.3-r0
- Alpine:v3.9: `nodejs` — affected >=0 <8.11.3-r0

## Details
nghttp2 version >= 1.10.0 and nghttp2 <= v1.31.0 contains an Improper Input Validation CWE-20 vulnerability in ALTSVC frame handling that can result in segmentation fault leading to denial of service. This attack appears to be exploitable via network client. This vulnerability appears to have been fixed in >= 1.31.1.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-1000168
