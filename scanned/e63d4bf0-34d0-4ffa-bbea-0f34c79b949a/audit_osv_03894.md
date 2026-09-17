# [M] ALPINE-CVE-2026-62429

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-62429
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 6.5 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-62429
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
Accessing the vNUMA configuration data of a guest is still possible when
domain destruction has already started.  The cleaning up of that
configuration information is not synchronized with its retrieval by a
device model controlling the guest.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-62429
