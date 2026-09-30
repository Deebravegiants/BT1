# [H] ALPINE-CVE-2022-43548

## Summary
Severity: High
Advisory: ALPINE-CVE-2022-43548
Ecosystem: Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.1 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-12-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-43548
Type: osv

## Affected
- Alpine:v3.17: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.18: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.19: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.20: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.21: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.22: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.23: `nodejs` — affected >=0 <18.12.1-r0
- Alpine:v3.24: `nodejs` — affected >=0 <18.12.1-r0

## Details
A OS Command Injection vulnerability exists in Node.js versions <14.21.1, <16.18.1, <18.12.1, <19.0.1 due to an insufficient IsAllowedHost check that can easily be bypassed because IsIPAddress does not properly check if an IP address is invalid before making DBS requests allowing rebinding attacks.The fix for this issue in https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2022-32212 was incomplete and this new CVE is to complete the fix.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-43548
