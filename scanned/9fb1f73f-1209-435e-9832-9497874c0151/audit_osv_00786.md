# [H] ALPINE-CVE-2017-8386

## Summary
Severity: High
Advisory: ALPINE-CVE-2017-8386
Ecosystem: Alpine:v3.3
CVSS: 8.8 (CVSS:3.0/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-06-01
Source: https://osv.dev/vulnerability/ALPINE-CVE-2017-8386
Type: osv

## Affected
- Alpine:v3.3: `git` — affected >=0 <2.6.7-r0

## Details
git-shell in git before 2.4.12, 2.5.x before 2.5.6, 2.6.x before 2.6.7, 2.7.x before 2.7.5, 2.8.x before 2.8.5, 2.9.x before 2.9.4, 2.10.x before 2.10.3, 2.11.x before 2.11.2, and 2.12.x before 2.12.3 might allow remote authenticated users to gain privileges via a repository name that starts with a - (dash) character.

## References
- https://security.alpinelinux.org/vuln/CVE-2017-8386
