# [H] ALPINE-CVE-2023-34325

## Summary
Severity: High
Advisory: ALPINE-CVE-2023-34325
Ecosystem: Alpine:v3.15, Alpine:v3.16, Alpine:v3.17, Alpine:v3.18, Alpine:v3.19, Alpine:v3.20, Alpine:v3.21, Alpine:v3.22, Alpine:v3.23, Alpine:v3.24
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2024-01-05
Source: https://osv.dev/vulnerability/ALPINE-CVE-2023-34325
Type: osv

## Affected
- Alpine:v3.15: `xen` — affected >=0 <4.15.5-r3
- Alpine:v3.16: `xen` — affected >=0 <4.16.5-r3
- Alpine:v3.17: `xen` — affected >=0 <4.16.5-r3
- Alpine:v3.18: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.19: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.20: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.21: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.22: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.23: `xen` — affected >=0 <4.17.2-r3
- Alpine:v3.24: `xen` — affected >=0 <4.17.2-r3

## Details
[This CNA information record relates to multiple CVEs; the
text explains which aspects/vulnerabilities correspond to which CVE.]

libfsimage contains parsing code for several filesystems, most of them based on
grub-legacy code.  libfsimage is used by pygrub to inspect guest disks.

Pygrub runs as the same user as the toolstack (root in a priviledged domain).

At least one issue has been reported to the Xen Security Team that allows an
attacker to trigger a stack buffer overflow in libfsimage.  After further
analisys the Xen Security Team is no longer confident in the suitability of
libfsimage when run against guest controlled input with super user priviledges.

In order to not affect current deployments that rely on pygrub patches are
provided in the resolution section of the advisory that allow running pygrub in
deprivileged mode.

CVE-2023-4949 refers to the original issue in the upstream grub
project ("An attacker with local access to a system (either through a
disk or external drive) can present a modified XFS partition to
grub-legacy in such a way to exploit a memory corruption in grub’s XFS
file system implementation.")  CVE-2023-34325 refers specifically to
the vulnerabilities in Xen's copy of libfsimage, which is decended
from a very old version of grub.

## References
- https://security.alpinelinux.org/vuln/CVE-2023-34325
