# [H] ALPINE-CVE-2018-12015

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-12015
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.12, Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:H/A:N)
Published: 2018-06-07
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-12015
Type: osv

## Affected
- Alpine:v3.10: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.11: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.12: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.13: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.14: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.15: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.16: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.17: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.18: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.19: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.20: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.21: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.22: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.23: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.24: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.5: `perl` — affected >=0 <5.24.4-r1
- Alpine:v3.6: `perl` — affected >=0 <5.24.4-r1
- Alpine:v3.7: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.8: `perl` — affected >=0 <5.26.2-r1
- Alpine:v3.9: `perl` — affected >=0 <5.26.2-r1

## Details
In Perl through 5.26.2, the Archive::Tar module allows remote attackers to bypass a directory-traversal protection mechanism, and overwrite arbitrary files, via an archive file containing a symlink and a regular file with the same name.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-12015
