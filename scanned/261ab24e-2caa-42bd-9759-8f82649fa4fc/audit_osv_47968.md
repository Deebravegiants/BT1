# [H] CVE-2017-15649

## Summary
Severity: High
Advisory: CVE-2017-15649
CVSS: 7.8 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:H/A:H)
Published: 2017-10-19
Source: https://osv.dev/vulnerability/CVE-2017-15649
Type: osv

## Details
net/packet/af_packet.c in the Linux kernel before 4.13.6 allows local users to gain privileges via crafted system calls that trigger mishandling of packet_fanout data structures, because of a race condition (involving fanout_add and packet_do_bind) that leads to a use-after-free, a different vulnerability than CVE-2017-6346.

## References
- https://lists.debian.org/debian-lts-announce/2017/12/msg00004.html
- https://usn.ubuntu.com/3754-1/
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=4971613c1639d8e5f102c4e797c3bf8f83a5a69e
- http://patchwork.ozlabs.org/patch/818726/
- https://access.redhat.com/errata/RHSA-2018:0151
- https://blogs.securiteam.com/index.php/archives/3484
- http://www.securityfocus.com/bid/101573
- https://access.redhat.com/errata/RHSA-2018:0152
- https://access.redhat.com/errata/RHSA-2018:0181
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=008ba2a13f2d04c947adc536d19debb8fe66f110
- http://patchwork.ozlabs.org/patch/813945/
- https://github.com/torvalds/linux/commit/008ba2a13f2d04c947adc536d19debb8fe66f110
- https://github.com/torvalds/linux/commit/4971613c1639d8e5f102c4e797c3bf8f83a5a69e
- http://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.13.6
