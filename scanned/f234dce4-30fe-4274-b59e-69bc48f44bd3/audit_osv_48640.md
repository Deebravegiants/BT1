# [M] CVE-2018-1065

## Summary
Severity: Medium
Advisory: CVE-2018-1065
CVSS: 4.7 (CVSS:3.0/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-03-02
Source: https://osv.dev/vulnerability/CVE-2018-1065
Type: osv

## Details
The netfilter subsystem in the Linux kernel through 4.15.7 mishandles the case of a rule blob that contains a jump but lacks a user-defined chain, which allows local users to cause a denial of service (NULL pointer dereference) by leveraging the CAP_NET_RAW or CAP_NET_ADMIN capability, related to arpt_do_table in net/ipv4/netfilter/arp_tables.c, ipt_do_table in net/ipv4/netfilter/ip_tables.c, and ip6t_do_table in net/ipv6/netfilter/ip6_tables.c.

## References
- https://usn.ubuntu.com/3654-1/
- https://usn.ubuntu.com/3656-1/
- https://usn.ubuntu.com/3654-2/
- http://lists.openwall.net/netdev/2018/01/27/46
- http://www.securitytracker.com/id/1040446
- https://access.redhat.com/errata/RHSA-2018:2948
- https://www.debian.org/security/2018/dsa-4188
- https://bugzilla.redhat.com/show_bug.cgi?id=1547824
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=57ebd808a97d7c5b1e1afb937c2db22beba3c1f8
- http://patchwork.ozlabs.org/patch/870355/
- https://github.com/torvalds/linux/commit/57ebd808a97d7c5b1e1afb937c2db22beba3c1f8
