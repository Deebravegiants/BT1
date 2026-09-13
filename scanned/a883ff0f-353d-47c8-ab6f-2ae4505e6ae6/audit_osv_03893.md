# [H] ALPINE-CVE-2026-62428

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-62428
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:C/C:H/I:H/A:H)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-62428
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
When grant-copy operations are processed, the respective grant may or may
not already be in use by another operation (a mapping or another copy).
For all copy operations the referenced guest frame is looked up.  When
another operation is already active for the grant (the grant is "pinned"),
what is being supplied back to actually carry out permission checks and
copy operation may not be consistent: The permission check may be carried
out on a page different from the one involved in the copy.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-62428
