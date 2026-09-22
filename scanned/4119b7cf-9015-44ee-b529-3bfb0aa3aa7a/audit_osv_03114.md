# [M] ALPINE-CVE-2024-46901

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2024-46901
Ecosystem: Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:N/I:N/A:L)
Published: 2024-12-09
Source: https://osv.dev/vulnerability/ALPINE-CVE-2024-46901
Type: osv

## Affected
- Alpine:v3.18: `subversion` — affected >=0 <1.14.5-r0
- Alpine:v3.19: `subversion` — affected >=0 <1.14.5-r0
- Alpine:v3.20: `subversion` — affected >=0 <1.14.5-r0
- Alpine:v3.21: `subversion` — affected >=0 <1.14.5-r0
- Alpine:v3.22: `subversion` — affected >=0 <1.14.5-r0
- Alpine:v3.23: `subversion` — affected >=0 <1.14.5-r0
- Alpine:v3.24: `subversion` — affected >=0 <1.14.5-r0

## Details
Insufficient validation of filenames against control characters in Apache Subversion repositories served via mod_dav_svn allows authenticated users with commit access to commit a corrupted revision, leading to disruption for users of the repository.

All versions of Subversion up to and including Subversion 1.14.4 are affected if serving repositories via mod_dav_svn. Users are recommended to upgrade to version 1.14.5, which fixes this issue.

Repositories served via other access methods are not affected.

## References
- https://security.alpinelinux.org/vuln/CVE-2024-46901
