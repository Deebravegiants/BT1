# [H] ALPINE-CVE-2023-24807

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-24807
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2023-02-16
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-24807
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
Undici is an HTTP/1.1 client for Node.js. Prior to version 5.19.1, the `Headers.set()` and `Headers.append()` methods are vulnerable to Regular Expression Denial of Service (ReDoS) attacks when untrusted values are passed into the functions. This is due to the inefficient regular expression used to normalize the values in the `headerValueNormalize()` utility function. This vulnerability was patched in v5.19.1. No known workarounds are available.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-24807
