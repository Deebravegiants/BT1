# [H] ALPINE-CVE-2019-8324

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-8324
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:R/S:U/C:H/I:H/A:H)
Published: 2019-06-17
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-8324
Type: osv

## Affected
- Alpine:v3.6: `ruby` — affected >=0 <2.4.6-r0
- Alpine:v3.7: `ruby` — affected >=0 <2.4.6-r0
- Alpine:v3.8: `ruby` — affected >=0 <2.5.5-r0
- Alpine:v3.9: `ruby` — affected >=0 <2.5.5-r0

## Details
An issue was discovered in RubyGems 2.6 and later through 3.0.2. A crafted gem with a multi-line name is not handled correctly. Therefore, an attacker could inject arbitrary code to the stub line of gemspec, which is eval-ed by code in ensure_loadable_spec during the preinstall check.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-8324
