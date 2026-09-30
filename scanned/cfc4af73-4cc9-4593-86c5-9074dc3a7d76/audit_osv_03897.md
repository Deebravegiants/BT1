# [H] ALPINE-CVE-2026-62432

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-62432
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.3 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-62432
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
The EVTCHNOP_expand_array hypercall checks for whether FIFO event
channels are enabled, but without holding the correct lock.  It can race
with EVTCHNOP_reset, resulting in dereferencing a NULL pointer.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-62432
