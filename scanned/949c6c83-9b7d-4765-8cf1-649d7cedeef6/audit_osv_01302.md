# [H] ALPINE-CVE-2019-1000018

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-1000018
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2019-02-04
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-1000018
Type: osv

## Affected
- Alpine:v3.13: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.14: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.15: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.16: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.17: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.18: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.19: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.20: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.21: `rssh` — affected >=0 <2.3.4-r2
- Alpine:v3.22: `rssh` — affected >=0 <2.3.4-r2

## Details
rssh version 2.3.4 contains a CWE-77: Improper Neutralization of Special Elements used in a Command ('Command Injection') vulnerability in allowscp permission that can result in Local command execution. This attack appear to be exploitable via An authorized SSH user with the allowscp permission.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-1000018
