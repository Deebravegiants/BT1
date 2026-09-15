# [H] ALPINE-CVE-2018-7158

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-7158
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-05-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-7158
Type: osv

## Affected
- Alpine:v3.10: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.11: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.12: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.13: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.14: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.15: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.16: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.17: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.18: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.19: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.20: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.21: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.22: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.23: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.24: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.8: `nodejs` — affected >=0 <8.11.0-r0
- Alpine:v3.9: `nodejs` — affected >=0 <8.11.0-r0

## Details
The `'path'` module in the Node.js 4.x release line contains a potential regular expression denial of service (ReDoS) vector. The code in question was replaced in Node.js 6.x and later so this vulnerability only impacts all versions of Node.js 4.x. The regular expression, `splitPathRe`, used within the `'path'` module for the various path parsing functions, including `path.dirname()`, `path.extname()` and `path.parse()` was structured in such a way as to allow an attacker to craft a string, that when passed through one of these functions, could take a significant amount of time to evaluate, potentially leading to a full denial of service.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-7158
