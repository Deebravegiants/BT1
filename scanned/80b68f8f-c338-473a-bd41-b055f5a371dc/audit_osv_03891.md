# [H] ALPINE-CVE-2026-62426

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-62426
Ecosystem: Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 8.8 (CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-07-28
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-62426
Type: osv

## Affected
- Alpine:v3.21: `xen` — affected >=0 <4.19.6-r0
- Alpine:v3.22: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.23: `xen` — affected >=0 <4.20.4-r0
- Alpine:v3.24: `xen` — affected >=0 <4.21.2-r0

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

To manage the system, sysctl and platform operations are used by the
control domain or a possible Xenstore domain.  Some of these operations
may not be executed in parallel, so a system-wide lock each is used.
The way those locks are acquired is, however, not providing any fairness.
Furthermore, with XSM/Flask in use, the lock acquire will, for some
operations, occur ahead of any permission checking.

The sysctl issue is CVE-2026-62426.

The platform-op issue is CVE-2026-62427.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-62426
