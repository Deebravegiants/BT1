# [H] ALPINE-CVE-2017-8114

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-8114
Ecosystem: Alpine:v3.2, Alpine:v3.3, Alpine:v3.4, Alpine:v3.5
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-04-29
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8114
Type: osv

## Affected
- Alpine:v3.2: `roundcubemail` — affected >=0 <1.1.9-r0
- Alpine:v3.3: `roundcubemail` — affected >=0 <1.1.9-r0
- Alpine:v3.4: `roundcubemail` — affected >=0 <1.2.5-r0
- Alpine:v3.5: `roundcubemail` — affected >=0 <1.2.5-r0

## Details
Roundcube Webmail allows arbitrary password resets by authenticated users. This affects versions before 1.0.11, 1.1.x before 1.1.9, and 1.2.x before 1.2.5. The problem is caused by an improperly restricted exec call in the virtualmin and sasl drivers of the password plugin.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8114
