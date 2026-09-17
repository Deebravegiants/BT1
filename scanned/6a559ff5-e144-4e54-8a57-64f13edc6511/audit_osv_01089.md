# [H] ALPINE-CVE-2018-19788

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-19788
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2018-12-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-19788
Type: osv

## Affected
- Alpine:v3.6: `polkit` — affected >=0 <0.105-r8
- Alpine:v3.7: `polkit` — affected >=0 <0.105-r8
- Alpine:v3.8: `polkit` — affected >=0 <0.105-r9
- Alpine:v3.9: `polkit` — affected >=0 <0.105-r9

## Details
A flaw was found in PolicyKit (aka polkit) 0.115 that allows a user with a uid greater than INT_MAX to successfully execute any systemctl command.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-19788
