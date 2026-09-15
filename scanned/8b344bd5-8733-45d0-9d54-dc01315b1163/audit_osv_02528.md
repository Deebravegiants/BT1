# [C] ALPINE-CVE-2022-28738

## Summary
Severity: Critical
Advisory: ALPINE-CVE-2022-28738
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2022-05-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2022-28738
Type: osv

## Affected
- Alpine:v3.15: `ruby` — affected >=3.0.0 <3.0.4-r0
- Alpine:v3.16: `ruby` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.17: `ruby` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.18: `ruby` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.19: `ruby` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.20: `ruby` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.21: `ruby` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.22: `ruby` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.23: `ruby` — affected >=3.0.0 <3.1.2-r0
- Alpine:v3.24: `ruby` — affected >=3.0.0 <3.1.2-r0

## Details
A double free was found in the Regexp compiler in Ruby 3.x before 3.0.4 and 3.1.x before 3.1.2. If a victim attempts to create a Regexp from untrusted user input, an attacker may be able to write to unexpected memory locations.

## References
- https://security.alpinelinux.org/vuln/CVE-2022-28738
