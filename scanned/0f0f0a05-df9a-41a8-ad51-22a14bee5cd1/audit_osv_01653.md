# [H] ALPINE-CVE-2019-8321

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-8321
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2019-06-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-8321
Type: osv

## Affected
- Alpine:v3.6: `ruby` — affected >=0 <2.4.6-r0
- Alpine:v3.7: `ruby` — affected >=0 <2.4.6-r0
- Alpine:v3.8: `ruby` — affected >=0 <2.5.5-r0
- Alpine:v3.9: `ruby` — affected >=0 <2.5.5-r0

## Details
An issue was discovered in RubyGems 2.6 and later through 3.0.2. Since Gem::UserInteraction#verbose calls say without escaping, escape sequence injection is possible.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-8321
