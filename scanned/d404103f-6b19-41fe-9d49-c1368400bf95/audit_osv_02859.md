# [H] ALPINE-CVE-2023-38552

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-38552
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2023-10-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-38552
Type: osv

## Affected
- Alpine:v3.17: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.18: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.19: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.20: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.21: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.22: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.23: `nodejs` — affected >=0 <18.18.2-r0
- Alpine:v3.24: `nodejs` — affected >=0 <18.18.2-r0

## Details
When the Node.js policy feature checks the integrity of a resource against a trusted manifest, the application can intercept the operation and return a forged checksum to the node's policy implementation, thus effectively disabling the integrity check.
Impacts:
This vulnerability affects all users using the experimental policy mechanism in all active release lines: 18.x and, 20.x.
Please note that at the time this CVE was issued, the policy mechanism is an experimental feature of Node.js.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-38552
