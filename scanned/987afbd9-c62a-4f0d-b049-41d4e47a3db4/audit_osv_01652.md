# [H] ALPINE-CVE-2019-8320

## Summary
Severity: High
Advisory: ALPINE-CVE-2019-8320
Ecosystem: Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.4 (CVSS:3.0/AV:N/AC:H/PR:N/UI:N/S:U/C:N/I:H/A:H)
Published: 2019-06-06
Source: https://osv.dev/vulnerability/ALPINE-CVE-2019-8320
Type: osv

## Affected
- Alpine:v3.6: `ruby` — affected >=0 <2.4.6-r0
- Alpine:v3.7: `ruby` — affected >=0 <2.4.6-r0
- Alpine:v3.8: `ruby` — affected >=0 <2.5.5-r0
- Alpine:v3.9: `ruby` — affected >=0 <2.5.5-r0

## Details
A Directory Traversal issue was discovered in RubyGems 2.7.6 and later through 3.0.2. Before making new directories or touching files (which now include path-checking code for symlinks), it would delete the target destination. If that destination was hidden behind a symlink, a malicious gem could delete arbitrary files on the user's machine, presuming the attacker could guess at paths. Given how frequently gem is run as sudo, and how predictable paths are on modern systems (/tmp, /usr, etc.), this could likely lead to data loss or an unusable system.

## References
- https://security.alpinelinux.org/vuln/CVE-2019-8320
