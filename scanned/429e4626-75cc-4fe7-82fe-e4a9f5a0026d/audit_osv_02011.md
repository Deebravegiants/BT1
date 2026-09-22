# [H] ALPINE-CVE-2020-8201

## Summary
Severity: High
Advisory: ALPINE-CVE-2020-8201
Ecosystem: Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.4 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:N)
Published: 2020-09-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2020-8201
Type: osv

## Affected
- Alpine:v3.11: `nodejs` — affected >=0 <12.20.1-r0
- Alpine:v3.12: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.13: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.14: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.15: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.16: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.17: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.18: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.19: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.20: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.21: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.22: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.23: `nodejs` — affected >=0 <12.18.4-r0
- Alpine:v3.24: `nodejs` — affected >=0 <12.18.4-r0

## Details
Node.js < 12.18.4 and < 14.11 can be exploited to perform HTTP desync attacks and deliver malicious payloads to unsuspecting users. The payloads can be crafted by an attacker to hijack user sessions, poison cookies, perform clickjacking, and a multitude of other attacks depending on the architecture of the underlying system. The attack was possible due to a bug in processing of carrier-return symbols in the HTTP header names.

## References
- https://security.alpinelinux.org/vuln/CVE-2020-8201
