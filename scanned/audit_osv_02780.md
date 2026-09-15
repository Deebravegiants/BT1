# [H] ALPINE-CVE-2023-23919

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-23919
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-23919
Type: osv

## Affected
- Alpine:v3.15: `nodejs` — affected >=0 <16.19.1-r0
- Alpine:v3.16: `nodejs` — affected >=0 <16.19.1-r0
- Alpine:v3.17: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <18.14.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <18.14.1-r0

## Details
A cryptographic vulnerability exists in Node.js <19.2.0, <18.14.1, <16.19.1, <14.21.3 that in some cases did does not clear the OpenSSL error stack after operations that may set it. This may lead to false positive errors during subsequent cryptographic operations that happen to be on the same thread. This in turn could be used to cause a denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-23919
