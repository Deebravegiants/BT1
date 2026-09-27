# [M] CVE-2018-15594

## Summary
Severity: Medium
Advisory: CVE-2018-15594
CVSS: 5.5 (CVSS:3.0/AV:L/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N)
Published: 2018-08-20
Source: https://osv.dev/vulnerability/CVE-2018-15594
Type: osv

## Details
arch/x86/kernel/paravirt.c in the Linux kernel before 4.18.1 mishandles certain indirect calls, which makes it easier for attackers to conduct Spectre-v2 attacks against paravirtual guests.

## References
- http://lists.opensuse.org/opensuse-security-announce/2019-05/msg00043.html
- https://twitter.com/grsecurity/status/1029324426142199808
- https://usn.ubuntu.com/3776-1/
- https://usn.ubuntu.com/3776-2/
- https://usn.ubuntu.com/3777-1/
- https://usn.ubuntu.com/3777-3/
- http://www.securityfocus.com/bid/105120
- http://www.securitytracker.com/id/1041601
- https://cdn.kernel.org/pub/linux/kernel/v4.x/ChangeLog-4.18.1
- https://usn.ubuntu.com/3777-2/
- https://www.debian.org/security/2018/dsa-4308
- https://lists.debian.org/debian-lts-announce/2018/10/msg00003.html
- https://usn.ubuntu.com/3775-1/
- https://usn.ubuntu.com/3775-2/
- https://access.redhat.com/errata/RHSA-2019:2029
- https://access.redhat.com/errata/RHSA-2019:2043
- https://github.com/torvalds/linux/commit/5800dc5c19f34e6e03b5adab1282535cb102fafd
- http://git.kernel.org/cgit/linux/kernel/git/torvalds/linux.git/commit/?id=5800dc5c19f34e6e03b5adab1282535cb102fafd
