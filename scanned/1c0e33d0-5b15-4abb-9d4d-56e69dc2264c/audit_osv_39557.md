# [H] RDMA/mana: Validate rx_hash_key_len

## Summary
Severity: High
Advisory: CVE-2026-46145
Ecosystem: Linux
CVSS: 7.8 (CVSS:3.1/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2026-05-28
Source: https://osv.dev/vulnerability/CVE-2026-46145
Type: osv

## Affected
- Linux: `Kernel` — affected >=6.2.0 <6.6.141, >=6.7.0 <6.12.88, >=6.13.0 <6.18.30, >=6.19.0 <7.0.7

## Details
In the Linux kernel, the following vulnerability has been resolved:

RDMA/mana: Validate rx_hash_key_len

Sashiko points out that rx_hash_key_len comes from a uAPI structure and is
blindly passed to memcpy, allowing the userspace to trash kernel
memory. Bounds check it so the memcpy cannot overflow.

## References
- https://git.kernel.org/stable/c/012796f9541fcd0c1fa8ae4da7eb4d83931ef838
- https://git.kernel.org/stable/c/11c1431d641e0e4e0529e96957995820600c7287
- https://git.kernel.org/stable/c/6dd2d4ad9c8429523b1c220c5132bd551c006425
- https://git.kernel.org/stable/c/7d7c9f0fcd19c4d2f0164347c58d49cafa961b72
- https://git.kernel.org/stable/c/7d94f155f354b961c598f71bafa804dceded513f
- https://security.access.redhat.com/data/csaf/v2/vex/2026/cve-2026-46145.json
- https://access.redhat.com/errata/RHSA-2026:27353
- https://access.redhat.com/errata/RHSA-2026:27354
- https://access.redhat.com/errata/RHSA-2026:27789
- https://access.redhat.com/errata/RHSA-2026:30129
- https://access.redhat.com/errata/RHSA-2026:62568
- https://access.redhat.com/errata/RHSA-2026:64767
- https://access.redhat.com/errata/RHSA-2026:65712
- https://access.redhat.com/security/cve/CVE-2026-46145
- https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/46xxx/CVE-2026-46145.json
- https://nvd.nist.gov/vuln/detail/CVE-2026-46145
- https://bugzilla.redhat.com/show_bug.cgi?id=2482581
- https://git.kernel.org/pub/scm/linux/kernel/git/stable/linux.git
