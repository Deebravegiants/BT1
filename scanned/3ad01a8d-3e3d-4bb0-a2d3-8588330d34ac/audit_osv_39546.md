# [H] RDMA/mana: Remove user triggerable WARN_ON() in mana_ib_create_qp_rss()

## Summary
Severity: High
Advisory: CVE-2026-46117
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46117
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.8.0 <6.12.91, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mana: Remove user triggerable WARN_ON() in mana_ib_create_qp_rss()

Sashiko points out that the user can specify WQs sharing the same CQ as a
part of the uAPI and this will trigger the WARN_ON() then go on to corrupt
the kernel.

Just reject it outright and fail the QP creation.

## References
- https://git.kernel.org/stable/c/159f2efabc89d3f931d38f2d35876535d4abf0a3
- https://git.kernel.org/stable/c/9cc0c6b1ba8cd5c55aef043e1384de0a8b4efa71
- https://git.kernel.org/stable/c/9ef65af26b2a6738bf15812042e84b3112402d3a
- https://git.kernel.org/stable/c/db991ba50087ad99fa12a2c483aa3be19671ea73
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46117.json
- https://access.redhat.com/errata/RHSA-2026:27789
- https://access.redhat.com/errata/RHSA-2026:30129
- https://access.redhat.com/errata/RHSA-2026:42550
- https://access.redhat.com/errata/RHSA-2026:42552
- https://access.redhat.com/errata/RHSA-2026:65712
- https://access.redhat.com/security/cve/CVE-2026-46117
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46117.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46117
- https://bugzilla.redhat.com/show_bug.cgi?id=2482576
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
