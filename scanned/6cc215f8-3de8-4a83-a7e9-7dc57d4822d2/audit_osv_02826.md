# [C] ALPINE-CVE-2023-32002

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2023-32002
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2023-08-21
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-32002
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
The use of `Module._load()` can bypass the policy mechanism and require modules outside of the policy.json definition for a given module.

This vulnerability affects all users using the experimental policy mechanism in all active release lines: 16.x, 18.x and, 20.x.

Please note that at the time this CVE was issued, the policy is an experimental feature of Node.js.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-32002
