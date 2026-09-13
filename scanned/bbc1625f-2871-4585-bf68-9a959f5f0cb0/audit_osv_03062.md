# [C] ALPINE-CVE-2024-3596

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2024-3596
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.0 (CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:C/C:H/I:H/A:H)
Published: 2024-07-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-3596
Type: osv

## Affected
- Alpine:v3.18: `freeradius` — affected >=0 <3.0.27-r0
- Alpine:v3.19: `freeradius` — affected >=0 <3.0.27-r0
- Alpine:v3.20: `freeradius` — affected >=0 <3.0.27-r0
- Alpine:v3.21: `freeradius` — affected >=0 <3.0.27-r0
- Alpine:v3.22: `freeradius` — affected >=0 <3.0.27-r0
- Alpine:v3.23: `freeradius` — affected >=0 <3.0.27-r0
- Alpine:v3.24: `freeradius` — affected >=0 <3.0.27-r0

## Details
RADIUS Protocol under RFC 2865 is susceptible to forgery attacks by a local attacker who can modify any valid Response (Access-Accept, Access-Reject, or Access-Challenge) to any other response using a chosen-prefix collision attack against MD5 Response Authenticator signature.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-3596
