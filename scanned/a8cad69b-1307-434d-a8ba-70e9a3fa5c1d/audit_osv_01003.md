# [H] ALPINE-CVE-2018-14912

## Summary
Severity: High
Advisory: ALPINE-CVE-2018-14912
Ecosystem: Alpine:v3.5, Alpine:v3.6, Alpine:v3.7, Alpine:v3.8
CVSS: 7.5 (CVSS:3.0/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-03
Source: https://osv.dev/vulnerability/ALPINE-CVE-2018-14912
Type: osv

## Affected
- Alpine:v3.5: `cgit` — affected >=0 <1.0-r2
- Alpine:v3.6: `cgit` — affected >=0 <1.1-r2
- Alpine:v3.7: `cgit` — affected >=0 <1.1-r3
- Alpine:v3.8: `cgit` — affected >=0 <1.1-r4

## Details
cgit_clone_objects in CGit before 1.2.1 has a directory traversal vulnerability when `enable-http-clone=1` is not turned off, as demonstrated by a cgit/cgit.cgi/git/objects/?path=../ request.

## References
- https://security.alpinelinux.org/vuln/CVE-2018-14912
