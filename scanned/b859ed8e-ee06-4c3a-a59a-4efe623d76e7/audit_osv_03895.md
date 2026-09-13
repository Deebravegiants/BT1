# [H] ALPINE-CVE-2026-62430

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-62430
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.5 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:N/A:N)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-62430
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
Accesses to the CMOS memory contents are done using an indirect IO port
pair.  Therefore Xen needs to cache the guest chosen index, and one of
the usages of the index didn't take the necessary locking to avoid
concurrent changes.  As a result, a guest could change the index after
it being checked, causing a subsequent out-of-bound read access to the
contents of an array.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-62430
