# [C] tcp: fix potential race in tcp_v6_syn_recv_sock()

## Summary
Severity: Critical
Advisory: CVE-2026-43198
Ecosystem: Linux
CVSS: 9.8 (CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-06
Source: https://osv.dev/vulnerability/CVE-2026-43198
Type: osv

## Affected
- Linux: `Kernel` — affected >=2.6.12 <6.18.16, >=6.19.0 <6.19.6

## Details
In the Linux kernel, the following vulnerability has been resolved:

tcp: fix potential race in tcp_v6_syn_recv_sock()

Code in tcp_v6_syn_recv_sock() after the call to tcp_v4_syn_recv_sock()
is done too late.

After tcp_v4_syn_recv_sock(), the child socket is already visible
from TCP ehash table and other cpus might use it.

Since newinet->pinet6 is still pointing to the listener ipv6_pinfo
bad things can happen as syzbot found.

Move the problematic code in tcp_v6_mapped_child_init()
and call this new helper from tcp_v4_syn_recv_sock() before
the ehash insertion.

This allows the removal of one tcp_sync_mss(), since
tcp_v4_syn_recv_sock() will call it with the correct
context.

## References
- https://git.kernel.org/stable/c/7178e2a8027423b2af17ab95df73a749a5b72e5b
- https://git.kernel.org/stable/c/858d2a4f67ff69e645a43487ef7ea7f28f06deae
- https://git.kernel.org/stable/c/fe89b2f05b854847784f91127319172945c1fadd
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-43198.json
- https://access.redhat.com/errata/RHSA-2026:30129
- https://access.redhat.com/errata/RHSA-2026:33215
- https://access.redhat.com/errata/RHSA-2026:33285
- https://access.redhat.com/errata/RHSA-2026:34094
- https://access.redhat.com/errata/RHSA-2026:34443
- https://access.redhat.com/errata/RHSA-2026:35863
- https://access.redhat.com/errata/RHSA-2026:35894
- https://access.redhat.com/errata/RHSA-2026:35896
- https://access.redhat.com/errata/RHSA-2026:35904
- https://access.redhat.com/errata/RHSA-2026:36073
- https://access.redhat.com/errata/RHSA-2026:36216
- https://access.redhat.com/errata/RHSA-2026:36348
- https://access.redhat.com/errata/RHSA-2026:36349
- https://access.redhat.com/errata/RHSA-2026:41236
- https://access.redhat.com/security/cve/CVE-2026-43198
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/43xxx/CVE-2026-43198.json
