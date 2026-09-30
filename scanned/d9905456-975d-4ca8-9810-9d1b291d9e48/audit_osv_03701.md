# [M] ALPINE-CVE-2026-42489

## Summary
Severity: Medium
Advisory: ALPINE-CVE-2026-42489
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 5.3 (CVSS:3.1/AV:L/AC:H/PR:H/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-06-18
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-42489
Type: osv

## Affected
- Alpine:v3.20: `xen` — affected >=0 <4.18.5-r9
- Alpine:v3.21: `xen` — affected >=0 <4.19.5-r4
- Alpine:v3.22: `xen` — affected >=0 <4.20.3-r4
- Alpine:v3.23: `xen` — affected >=0 <4.20.3-r4
- Alpine:v3.24: `xen` — affected >=0 <4.21.1-r6

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

To create and manage guests, domctl operations are used by the control
domain, a possible Xenstore domain, or by a domain controlling a
particular guest.  Some of these operations may not be executed in
parallel, so a system-wide lock is used.  The way that lock is acquired
is, however, not providing any fairness.  This is CVE-2026-42489.

Furthermore, with XSM/Flask in use, the lock acquire will, for some
operations, occur ahead of any permission checking.  This is
CVE-2026-42490.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-42489
