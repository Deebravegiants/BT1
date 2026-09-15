# [M] ALPINE-CVE-2021-28544

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2021-28544
Ecosystem: Alpine:v3.13, Alpine:v3.14, Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 4.3 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:L/I:N/A:N)
Published: 2022-04-12
Source: https://osv.dev/vulnerability/ALPINE-CVE-2021-28544
Type: osv

## Affected
- Alpine:v3.13: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.14: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.15: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.16: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.17: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.18: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.19: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.20: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.21: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.22: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.23: `subversion` — affected >=1.10.0 <1.14.2-r0
- Alpine:v3.24: `subversion` — affected >=1.10.0 <1.14.2-r0

## Details
Apache Subversion SVN authz protected copyfrom paths regression Subversion servers reveal 'copyfrom' paths that should be hidden according to configured path-based authorization (authz) rules. When a node has been copied from a protected location, users with access to the copy can see the 'copyfrom' path of the original. This also reveals the fact that the node was copied. Only the 'copyfrom' path is revealed; not its contents. Both httpd and svnserve servers are vulnerable.

## References
- https://security.alpinelinux.org/vuln/CVE-2021-28544
