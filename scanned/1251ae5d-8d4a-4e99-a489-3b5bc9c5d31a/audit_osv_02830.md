# [H] ALPINE-CVE-2023-32559

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-32559
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:H/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-24
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-32559
Type: osv

## Affected
- Alpine:v3.15: `nodejs` — affected >=0 <16.20.2-r0
- Alpine:v3.16: `nodejs` — affected >=0 <16.20.2-r0
- Alpine:v3.17: `nodejs` — affected >=0 <18.17.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <18.17.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <18.17.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <18.17.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <18.17.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <18.17.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <18.17.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <18.17.1-r0

## Details
A privilege escalation vulnerability exists in the experimental policy mechanism in all active release lines: 16.x, 18.x and, 20.x. The use of the deprecated API `process.binding()` can bypass the policy mechanism by requiring internal modules and eventually take advantage of `process.binding('spawn_sync')` run arbitrary code, outside of the limits defined in a `policy.json` file. Please note that at the time this CVE was issued, the policy is an experimental feature of Node.js.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-32559
