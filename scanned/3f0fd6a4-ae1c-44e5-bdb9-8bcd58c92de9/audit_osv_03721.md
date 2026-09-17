# [M] ALPINE-CVE-2026-4360

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-4360
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:L/A:N)
Published: 2026-06-30
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-4360
Type: osv

## Affected
- Alpine:v3.21: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.22: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.23: `python3` — affected >=0 <3.12.14-r0
- Alpine:v3.24: `python3` — affected >=0 <3.14.7-r0

## Details
In the Tarfile.extract() function, the filter parameter is not passed properly when extracting hardlinks. An affected system that extracts content from untrusted tar files could end up writing files with an unexpected uid/gid despite the user passing filter='data' to the extract() function.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-4360
