# [M] CVE-2023-7192

## Summary
Severity: Medium
Advisory: CVE-2023-7192
CVSS: 4.4 (CVSS:3.1/AV:L/AC:L/PR:H/UI:N/S:U/C:N/I:N/A:H)
Published: 2024-01-02
Source: https://osv.dev/vulnerability/CVE-2023-7192
Type: osv

## Details
A memory leak problem was found in ctnetlink_create_conntrack in net/netfilter/nf_conntrack_netlink.c in the Linux Kernel. This issue may allow a local attacker with CAP_NET_ADMIN privileges to cause a denial of service (DoS) attack due to a refcount overflow.

## References
- https://access.redhat.com/errata/RHSA-2024:1306
- https://access.redhat.com/errata/RHSA-2024:1367
- https://access.redhat.com/errata/RHSA-2024:1382
- https://access.redhat.com/errata/RHSA-2024:1404
- https://access.redhat.com/errata/RHSA-2024:2006
- https://access.redhat.com/errata/RHSA-2024:1188
- https://access.redhat.com/errata/RHSA-2024:1250
- https://access.redhat.com/errata/RHSA-2024:2008
- https://access.redhat.com/security/cve/CVE-2023-7192
- https://access.redhat.com/errata/RHSA-2024:0723
- https://access.redhat.com/errata/RHSA-2024:0725
- https://bugzilla.redhat.com/show_bug.cgi?id=2256279
- https://git.kernel.org/pub/scm/linux/kernel/git/netdev/net.git/commit/?id=ac4893980bbe79ce383daf9a0885666a30fe4c83
