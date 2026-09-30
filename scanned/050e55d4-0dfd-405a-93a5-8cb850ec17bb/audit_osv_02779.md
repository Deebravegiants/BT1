# [H] ALPINE-CVE-2023-23918

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-23918
Ecosystem: Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2023-02-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-23918
Type: osv

## Affected
- Alpine:v3.14: `nodejs` — affected >=0 <14.21.3-r0
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
A privilege escalation vulnerability exists in Node.js <19.6.1, <18.14.1, <16.19.1 and <14.21.3 that made it possible to bypass the experimental Permissions (https://nodejs.org/api/permissions.html) feature in Node.js and access non authorized modules by using process.mainModule.require(). This only affects users who had enabled the experimental permissions option with --experimental-policy.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-23918
