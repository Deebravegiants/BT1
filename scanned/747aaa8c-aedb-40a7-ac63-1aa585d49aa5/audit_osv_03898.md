# [H] ALPINE-CVE-2026-62433

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-62433
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-62433
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
Parts of the DM_OP handling code assumes the caller has provided the
required number of buffers for the given operation without any checking
being done.  As a result, certain operations might access stack
rubble as structures are possibly uninitialized.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-62433
