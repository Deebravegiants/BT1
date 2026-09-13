# [H] ALPINE-CVE-2026-23555

## Summary
Severity: High
Advisory: ALPINE-CVE-2026-23555
Ecosystem: Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.1 (CVSS:3.1/AV:L/AC:L/PR:N/UI:N/S:C/C:N/I:N/A:H)
Published: 2026-03-23
Source: https://osv.dev/vulnerability/ALPINE-CVE-2026-23555
Type: osv

## Affected
- Alpine:v3.20: `xen` — affected >=4.18.0 <4.18.5-r5
- Alpine:v3.21: `xen` — affected >=4.18.0 <4.19.4-r2
- Alpine:v3.22: `xen` — affected >=4.18.0 <4.20.2-r2
- Alpine:v3.23: `xen` — affected >=4.18.0 <4.20.2-r2
- Alpine:v3.24: `xen` — affected >=4.18.0 <4.21.0-r3

## Details
Any guest issuing a Xenstore command accessing a node using the
(illegal) node path "/local/domain/", will crash xenstored due to a
clobbered error indicator in xenstored when verifying the node path.

Note that the crash is forced via a failing assert() statement in
xenstored. In case xenstored is being built with NDEBUG #defined,
an unprivileged guest trying to access the node path "/local/domain/"
will result in it no longer being serviced by xenstored, other guests
(including dom0) will still be serviced, but xenstored will use up
all cpu time it can get.

## References
- https://security.alpinelinux.org/vuln/CVE-2026-23555
