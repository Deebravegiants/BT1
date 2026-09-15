# [M] ALPINE-CVE-2016-8568

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2016-8568
Ecosystem: Alpine:v3.10, Alpine:v3.11, Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8, Alpine:v3.9
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:N/UI:R/S:U/C:N/I:N/A:H)
Published: 2017-02-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2016-8568
Type: osv

## Affected
- Alpine:v3.10: `libgit2` — affected >=0 <0.24.3-r0
- Alpine:v3.11: `libgit2` — affected >=0 <0.24.3-r0
- Alpine:v3.5: `libgit2` — affected >=0 <0.24.3-r0
- Alpine:v3.6: `libgit2` — affected >=0 <0.24.3-r0
- Alpine:v3.7: `libgit2` — affected >=0 <0.24.3-r0
- Alpine:v3.8: `libgit2` — affected >=0 <0.24.3-r0
- Alpine:v3.9: `libgit2` — affected >=0 <0.24.3-r0

## Details
The git_commit_message function in oid.c in libgit2 before 0.24.3 allows remote attackers to cause a denial of service (out-of-bounds read) via a cat-file command with a crafted object file.

## References
- https://security.alpinelinux.org/vuln/CVE-2016-8568
