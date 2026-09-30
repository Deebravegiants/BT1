# [M] CVE-2017-15129

## Summary
Severity: Medium
Advisory: CVE-2017-15129
CVSS: 4.7 (CVSS:3.1/AV:L/AC:H/PR:L/UI:N/S:U/C:N/I:N/A:H)
Published: 2018-01-09
Source: https://osv.dev/vulnerability/CVE-2017-15129
Type: osv

## Details
A use-after-free vulnerability was found in network namespaces code affecting the Linux kernel before 4.14.11. The function get_net_ns_by_id() in net/core/net_namespace.c does not check for the net::count value after it has found a peer network in netns_ids idr, which could lead to double free and memory corruption. This vulnerability could allow an unprivileged local user to induce kernel memory corruption on the system, leading to a crash. Due to the nature of the flaw, privilege escalation cannot be fully ruled out, although it is thought to be unlikely.

## References
- http://www.securityfocus.com/bid/102485
- https://marc.info/?t=151370468900001&r=1&w=2
- https://usn.ubuntu.com/3632-1/
- https://access.redhat.com/errata/RHSA-2018:0654
- https://access.redhat.com/errata/RHSA-2018:0676
- https://www.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.14.11
- http://seclists.org/oss-sec/2018/q1/7
- https://access.redhat.com/security/cve/CVE-2017-15129
- https://usn.ubuntu.com/3617-3/
- https://usn.ubuntu.com/3619-2/
- https://access.redhat.com/errata/RHSA-2018:1062
- https://access.redhat.com/errata/RHSA-2019:1946
- https://usn.ubuntu.com/3617-1/
- https://usn.ubuntu.com/3617-2/
- https://usn.ubuntu.com/3619-1/
- https://github.com/torvalds/linux/commit/21b5944350052d2583e82dd59b19a9ba94a007f0
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=21b5944350052d2583e82dd59b19a9ba94a007f0
- https://marc.info/?l=linux-netdev&m=151370451121029&w=2
- https://bugzilla.redhat.com/show_bug.cgi?id=1531174
